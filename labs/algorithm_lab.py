"""Deterministic standard-library algorithms for self study, not robot control."""
import argparse
import heapq
import json
import math
from pathlib import Path

from course_lab import fk, finite


def jacobian(q1, q2, l1=.3, l2=.2):
    finite(q1, q2, l1, l2)
    if min(l1, l2) <= 0:
        raise ValueError("positive link lengths required")
    s, c = math.sin(q1 + q2), math.cos(q1 + q2)
    return ((-l1 * math.sin(q1) - l2 * s, -l2 * s),
            (l1 * math.cos(q1) + l2 * c, l2 * c))


def numerical_ik(target=(.3, .2), seed=(.3, .6), damping=.03, max_steps=200, tolerance=1e-6):
    """Position-only damped least squares with bounded updates and backtracking."""
    if len(target) != 2 or len(seed) != 2:
        raise ValueError("target and seed must each contain two values")
    finite(*target, *seed, damping, tolerance)
    if damping <= 0 or tolerance <= 0 or type(max_steps) is not int or max_steps <= 0:
        raise ValueError("positive damping, tolerance, and integer step budget required")
    q = list(seed)
    history = []
    reason = "iteration_budget"
    for step in range(max_steps + 1):
        p = fk(*q)
        error = [target[i] - p[i] for i in range(2)]
        norm = math.hypot(*error)
        history.append({"iteration": step, "q_rad": q[:], "xy_m": p, "error_m": norm})
        if norm <= tolerance:
            reason = "converged"
            break
        if step == max_steps:
            break
        j = jacobian(*q)
        # A = J J^T + lambda^2 I; solve the symmetric 2x2 system.
        a = sum(v*v for v in j[0]) + damping*damping
        b = sum(j[0][k]*j[1][k] for k in range(2))
        d = sum(v*v for v in j[1]) + damping*damping
        det = a*d - b*b
        if det <= 0 or not math.isfinite(det):
            reason = "numerical_failure"
            break
        z = ((d*error[0] - b*error[1])/det, (a*error[1] - b*error[0])/det)
        delta = [sum(j[row][col]*z[row] for row in range(2)) for col in range(2)]
        length = math.hypot(*delta)
        if length < 1e-13:
            reason = "stationary_seed"
            break
        scale = min(1.0, .25/length)
        accepted = False
        for _ in range(16):
            proposal = [q[k] + scale*delta[k] for k in range(2)]
            if math.dist(fk(*proposal), target) < norm:
                q = proposal
                accepted = True
                break
            scale *= .5
        if not accepted:
            reason = "no_descent"
            break
    return {"success": reason == "converged", "reason": reason, "history": history,
            "target_m": target, "q_rad": q, "error_m": history[-1]["error_m"]}


def astar(width, height, blocked, start, goal):
    """Four-neighbor unit-cost grid, Manhattan heuristic. Nodes are (x,y)."""
    if any(type(v) is not int or v <= 0 for v in (width, height)):
        raise ValueError("positive integer grid dimensions required")
    blocked = set(blocked)
    def valid(p):
        return (len(p) == 2 and all(type(v) is int for v in p)
                and 0 <= p[0] < width and 0 <= p[1] < height)
    if any(not valid(p) for p in [start, goal, *blocked]):
        raise ValueError("grid coordinate outside bounds or noninteger")
    if start in blocked or goal in blocked:
        raise ValueError("start or goal is blocked")
    def h(p):
        return abs(p[0]-goal[0]) + abs(p[1]-goal[1])
    queue = [(h(start), 0, start)]
    scores, parent, expanded = {start: 0}, {}, []
    while queue:
        _, g, point = heapq.heappop(queue)
        if g != scores[point]:
            continue
        expanded.append(point)
        if point == goal:
            path = [goal]
            while path[-1] != start:
                path.append(parent[path[-1]])
            return {"success": True, "path": list(reversed(path)), "cost": g, "expanded": expanded}
        for dx, dy in ((1, 0), (0, 1), (-1, 0), (0, -1)):
            nxt = (point[0]+dx, point[1]+dy)
            if not valid(nxt) or nxt in blocked:
                continue
            ng = g + 1
            if ng < scores.get(nxt, math.inf):
                scores[nxt], parent[nxt] = ng, point
                heapq.heappush(queue, (ng+h(nxt), ng, nxt))
    return {"success": False, "path": [], "cost": None, "expanded": expanded}


def trapezoid(distance=1.0, vmax=.5, amax=1.0, samples=201):
    """Rest-to-rest single-axis profile; includes triangular short moves."""
    finite(distance, vmax, amax)
    if distance < 0 or vmax <= 0 or amax <= 0 or type(samples) is not int or samples < 2:
        raise ValueError("nonnegative distance, positive limits, and >=2 samples required")
    peak = min(vmax, math.sqrt(distance*amax))
    ta = peak/amax
    tc = max(0.0, (distance - peak*peak/amax)/peak) if peak else 0.0
    total = 2*ta + tc
    rows = []
    for i in range(samples):
        t = total*i/(samples-1)
        if t < ta:
            q, v, a = .5*amax*t*t, amax*t, amax
        elif t < ta+tc:
            q, v, a = .5*amax*ta*ta+peak*(t-ta), peak, 0.0
        else:
            remain = total-t
            q, v, a = distance-.5*amax*remain*remain, amax*remain, -amax
        if i == samples-1:
            q, v, a = distance, 0.0, 0.0
        rows.append({"t_s": t, "q_rad": q, "v_rad_s": v, "a_rad_s2": a})
    return {"duration_s": total, "peak_rad_s": peak,
            "shape": "trapezoid" if tc > 0 else "triangle", "samples": rows}


def kalman_step(x, variance, measurement, process_variance=.01, measurement_variance=.25):
    """Scalar random-walk estimate; variances, not standard deviations."""
    finite(x, variance, measurement, process_variance, measurement_variance)
    if variance < 0 or process_variance < 0 or measurement_variance <= 0:
        raise ValueError("invalid variances")
    prior = variance + process_variance
    gain = prior/(prior+measurement_variance)
    return x+gain*(measurement-x), (1-gain)*prior, gain


def filter_demo():
    x, variance = 0.0, 1.0
    rows = []
    for k in range(60):
        truth = 1.0 if k < 30 else 1.5
        z = truth + .25*math.sin(2.3*k) + .08*math.cos(.8*k)
        x, variance, gain = kalman_step(x, variance, z)
        rows.append({"step": k, "truth": truth, "measurement": z,
                     "estimate": x, "variance": variance, "gain": gain})
    return rows


def pid_demo(kp=16.0, ki=4.0, kd=6.0, steps=1200, dt=.005):
    """Unit inertia + viscous friction, limited torque, conditional integration."""
    finite(kp, ki, kd, dt)
    if min(kp, ki, kd) < 0 or dt <= 0 or type(steps) is not int or steps <= 0:
        raise ValueError("nonnegative gains, positive dt and integer steps required")
    q, v, integral = 0.0, 0.0, 0.0
    rows = []
    for k in range(steps):
        error = 1.0-q
        trial_i = integral+error*dt
        raw = kp*error + ki*trial_i - kd*v
        command = max(-2.0, min(2.0, raw))
        if abs(raw) <= 2.0 or error*raw < 0:
            integral = trial_i
        command = max(-2.0, min(2.0, kp*error+ki*integral-kd*v))
        rows.append({"t_s": k*dt, "q_rad": q, "v_rad_s": v, "torque_nm": command})
        v += (command-.3*v)*dt
        q += v*dt
    return rows


def planning_demo():
    blocked = {(5, y) for y in range(8) if y != 6}
    result = astar(12, 8, blocked, (1, 1), (10, 1))
    return {**result, "blocked": sorted(blocked), "width": 12, "height": 8}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("experiment", choices=["ik", "planning", "trajectory", "filter", "pid", "all"])
    args = parser.parse_args()
    demos = {"ik": numerical_ik, "planning": planning_demo,
             "trajectory": trapezoid, "filter": filter_demo, "pid": pid_demo}
    selected = demos if args.experiment == "all" else {args.experiment: demos[args.experiment]}
    data = {name: fn() for name, fn in selected.items()}
    out = Path(__file__).resolve().parents[1]/"outputs"
    out.mkdir(exist_ok=True)
    path = out/("algorithms_"+args.experiment+".json")
    path.write_text(json.dumps(data, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    for name, result in data.items():
        if name == "ik":
            print(name, result["reason"], "error_m=", result["error_m"])
        elif name == "planning":
            print(name, "success=", result["success"], "cost=", result["cost"])
        elif name == "trajectory":
            print(name, result["shape"], "duration_s=", result["duration_s"])
        else:
            print(name, "samples=", len(result))
    print("Saved:", path)


if __name__ == "__main__":
    main()
