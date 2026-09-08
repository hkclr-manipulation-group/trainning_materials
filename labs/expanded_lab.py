"""Reproducible stack/IK/feedback teaching examples; no network or hardware IO."""
import math
from course_lab import fk, ik, finite
from algorithm_lab import numerical_ik


class LengthPrefixedDecoder:
    """Two-byte big-endian payload length; terminal error until reset()."""
    def __init__(self, max_length=1024):
        if type(max_length) is not int or not 1 <= max_length <= 65535:
            raise ValueError("max_length must be an integer in [1,65535]")
        self.max_length = max_length
        self.reset()

    def reset(self):
        self.buffer = bytearray()
        self.failed = False

    def feed(self, chunk):
        if self.failed:
            raise ValueError("decoder failed; reset only at a known new stream boundary")
        if not isinstance(chunk, (bytes, bytearray)):
            raise TypeError("chunk must be bytes")
        self.buffer.extend(chunk)
        messages = []
        while len(self.buffer) >= 2:
            length = int.from_bytes(self.buffer[:2], "big")
            if not 1 <= length <= self.max_length:
                self.failed = True
                raise ValueError("invalid length prefix")
            if len(self.buffer) < 2 + length:
                break
            messages.append(bytes(self.buffer[2:2+length]))
            del self.buffer[:2+length]
        return messages


def framed(payload):
    if not isinstance(payload, bytes) or not 1 <= len(payload) <= 65535:
        raise ValueError("payload must contain 1..65535 bytes")
    return len(payload).to_bytes(2, "big") + payload


def arbitration_trace(identifiers=(0x120, 0x100)):
    """Only the 11 identifier bits of simultaneous standard data frames."""
    if not identifiers or any(type(i) is not int or not 0 <= i <= 0x7ff for i in identifiers):
        raise ValueError("standard identifiers must be integers in [0,2047]")
    active = set(identifiers)
    result = []
    for bit in range(10, -1, -1):
        sent = {i: (i >> bit) & 1 for i in active}
        bus = min(sent.values())  # dominant zero wins
        lost = sorted(i for i, value in sent.items() if value != bus)
        active.difference_update(lost)
        result.append({"bit": bit, "sent": sent, "bus": bus, "lost": lost, "active": sorted(active)})
    return result


def ik_dataset():
    # One elbow branch; avoid exactly singular endpoints. Deterministic grid.
    return [(fk(q1, q2), (q1, q2))
            for q1 in [-math.pi + 2*math.pi*i/25 for i in range(25)]
            for q2 in [.08 + (math.pi-.16)*j/16 for j in range(17)]]


def nearest_seed(target, dataset):
    if len(target) != 2 or not dataset:
        raise ValueError("need a 2D target and a nonempty dataset")
    finite(*target)
    return min(dataset, key=lambda item: math.dist(item[0], target))[1]


def ik_benchmark():
    data = ik_dataset()
    # Held-out off-grid configurations; fixed examples, not a general benchmark.
    samples = [(-2.8 + 5.6*(i+.31)/30, .18 + 2.75*((i*7)%30+.43)/30) for i in range(30)]
    rows = []
    for index, true_q in enumerate(samples):
        target = fk(*true_q)
        seed = nearest_seed(target, data)
        refined = numerical_ik(target=target, seed=seed)
        baseline = numerical_ik(target=target, seed=(.3, .6))
        rows.append({"sample": index, "x_m": target[0], "y_m": target[1],
                     "nearest_error_m": math.dist(fk(*seed), target),
                     "refined_error_m": refined["error_m"], "refined_success": refined["success"],
                     "refined_updates": len(refined["history"])-1,
                     "fixed_seed_success": baseline["success"], "fixed_seed_updates": len(baseline["history"])-1})
    return rows


def branch_average_example():
    target = (.3, .2)
    solutions = ik(*target)
    average = tuple(sum(q[j] for q in solutions)/len(solutions) for j in range(2))
    return {"target": target, "solutions": solutions, "mean_q": average,
            "mean_xy": fk(*average), "error_m": math.dist(fk(*average), target)}


def delay_response(delay_steps=0, kp=12., dt=.01, steps=250):
    """Unsaturated velocity integrator, delayed measured position, target=1 rad."""
    finite(kp, dt)
    if type(delay_steps) is not int or delay_steps < 0 or type(steps) is not int or steps <= 0 or kp <= 0 or dt <= 0:
        raise ValueError("nonnegative delay and positive gain, dt, integer steps required")
    states, rows = [0.], []
    for k in range(steps):
        measured = states[max(0, k-delay_steps)]
        command = kp*(1-measured)
        rows.append({"time_s": k*dt, "q_rad": states[k], "measured_rad": measured,
                     "velocity_rad_s": command, "nominal_delay_s": delay_steps*dt})
        states.append(states[k]+command*dt)
    return rows
