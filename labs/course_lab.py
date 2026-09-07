"""Offline teaching examples. No robot, device, network, or external packages."""
import argparse
import csv
import json
import math
from pathlib import Path
import struct


OUTPUT = Path(__file__).resolve().parents[1] / "outputs"


def finite(*values):
    if not all(math.isfinite(v) for v in values):
        raise ValueError("values must be finite")


def fk(q1, q2, l1=0.3, l2=0.2):
    """Planar two-link endpoint, angles rad, lengths m."""
    finite(q1, q2, l1, l2)
    if min(l1, l2) <= 0:
        raise ValueError("link lengths must be positive")
    return (l1 * math.cos(q1) + l2 * math.cos(q1 + q2),
            l1 * math.sin(q1) + l2 * math.sin(q1 + q2))


def ik(x, y, l1=0.3, l2=0.2):
    """Geometric position IK only; no limits, orientation, or collision model."""
    finite(x, y, l1, l2)
    if min(l1, l2) <= 0:
        raise ValueError("link lengths must be positive")
    c2 = (x * x + y * y - l1 * l1 - l2 * l2) / (2 * l1 * l2)
    if abs(c2) > 1 + 1e-12:
        return []
    c2 = max(-1.0, min(1.0, c2))
    solutions = []
    for q2 in (math.acos(c2), -math.acos(c2)):
        q1 = math.atan2(y, x) - math.atan2(l2 * math.sin(q2), l1 + l2 * math.cos(q2))
        solutions.append((q1, q2))
    return solutions


def encode_frame(node, sequence, angle_rad):
    """Invented 8-byte teaching payload, NOT a real motor command."""
    finite(angle_rad)
    if type(node) is not int or not 1 <= node <= 255:
        raise ValueError("node must be an integer in [1, 255]")
    if type(sequence) is not int or not 0 <= sequence <= 65535:
        raise ValueError("sequence must be an integer in [0, 65535]")
    if abs(angle_rad) > 2147483.647:
        raise ValueError("angle outside teaching payload range")
    return struct.pack("<BBHi", 0xA1, node, sequence, round(angle_rad * 1000))


def decode_frame(payload):
    if len(payload) != 8:
        raise ValueError("payload must contain exactly 8 bytes")
    marker, node, sequence, angle_mrad = struct.unpack("<BBHi", payload)
    if marker != 0xA1 or node == 0:
        raise ValueError("invalid teaching marker or node")
    return {"node": node, "sequence": sequence, "angle_rad": angle_mrad / 1000}


def feedback_fresh(age_s, timeout_s):
    finite(age_s, timeout_s)
    if age_s < 0 or timeout_s <= 0:
        raise ValueError("age must be nonnegative and timeout positive")
    return age_s <= timeout_s


def simulate_control(target=1.0, kp=4.0, dt=0.01, steps=600, vmax=0.5):
    """Velocity-commanded integrator with P feedback; not motor dynamics."""
    finite(target, kp, dt, vmax)
    if min(kp, dt, vmax) <= 0 or type(steps) is not int or steps <= 0:
        raise ValueError("gain, timestep, speed and step count must be positive")
    q = 0.0
    rows = []
    for index in range(steps):
        error = target - q
        velocity = max(-vmax, min(vmax, kp * error))
        rows.append({"time_s": index * dt, "position_rad": q,
                     "target_rad": target, "command_rad_s": velocity})
        q += velocity * dt
    return rows, q


def sphere_gap(c1, r1, c2, r2):
    if len(c1) != 3 or len(c2) != 3:
        raise ValueError("sphere centers must be 3D")
    finite(*c1, r1, *c2, r2)
    if min(r1, r2) <= 0:
        raise ValueError("radii must be positive")
    return math.dist(c1, c2) - r1 - r2


def fit_line(samples):
    if len(samples) < 2:
        raise ValueError("at least two training samples required")
    for x, y in samples:
        finite(x, y)
    xm = sum(x for x, _ in samples) / len(samples)
    ym = sum(y for _, y in samples) / len(samples)
    denom = sum((x - xm) ** 2 for x, _ in samples)
    if denom <= 1e-15:
        raise ValueError("training observations must vary")
    slope = sum((x - xm) * (y - ym) for x, y in samples) / denom
    return slope, ym - slope * xm


def mse(samples, slope, intercept):
    if not samples:
        raise ValueError("evaluation samples must not be empty")
    finite(slope, intercept)
    for x, y in samples:
        finite(x, y)
    return sum((slope * x + intercept - y) ** 2 for x, y in samples) / len(samples)


def demo_units():
    return {"90_deg_in_rad": math.radians(90), "300_mm_in_m": 300 / 1000,
            "100_hz_period_s": 1 / 100}


def demo_kinematics():
    target = fk(math.radians(30), math.radians(60))
    solutions = ik(*target)
    return {"target_m": target, "solutions_rad": solutions,
            "fk_roundtrip_errors_m": [math.dist(fk(*q), target) for q in solutions],
            "outside_target_solutions": ik(0.6, 0)}


def demo_protocol():
    payload = encode_frame(1, 7, 0.25)
    return {"payload_hex": payload.hex(" "), "decoded": decode_frame(payload),
            "feedback_120ms_timeout_100ms_fresh": feedback_fresh(0.12, 0.1)}


def demo_control():
    rows, q = simulate_control()
    OUTPUT.mkdir(exist_ok=True)
    with (OUTPUT / "control.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return {"final_position_rad": q, "final_error_rad": 1.0 - q,
            "max_command_rad_s": max(abs(row["command_rad_s"]) for row in rows),
            "model": "velocity integrator; no physical motor dynamics"}


def demo_collision():
    # A=[-0.008,0.008], B=[0.012,0.028] on a teaching 1D line.
    return {"true_1d_interval_gap_m": 0.012 - 0.008,
            "oversized_sphere_gap_m": sphere_gap((0, 0, 0), .015, (.02, 0, 0), .015),
            "smaller_sphere_gap_m": sphere_gap((0, 0, 0), .009, (.02, 0, 0), .009),
            "limitation": "1D illustration, not 3D mesh coverage validation"}


def demo_ai():
    # Disjoint synthetic observations; no random library or external dataset.
    train = [(x, 0.5 * x + 0.1 + 0.01 * math.sin(7 * x))
             for x in (-1.0, -0.6, -0.2, 0.2, 0.6, 1.0)]
    test = [(x, 0.5 * x + 0.1 + 0.01 * math.sin(7 * x))
            for x in (-0.8, -0.4, 0.0, 0.4, 0.8)]
    slope, intercept = fit_line(train)
    baseline = sum(y for _, y in train) / len(train)
    return {"slope": slope, "intercept": intercept,
            "train_mse": mse(train, slope, intercept),
            "heldout_mse": mse(test, slope, intercept),
            "constant_baseline_heldout_mse": mse(test, 0, baseline),
            "train_samples": train, "heldout_samples": test,
            "limitation": "synthetic regression, not a deployable robot policy"}


DEMOS = {"units": demo_units, "kinematics": demo_kinematics,
         "protocol": demo_protocol, "control": demo_control,
         "collision": demo_collision, "ai": demo_ai}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("experiment", choices=[*DEMOS, "all"])
    args = parser.parse_args()
    selected = DEMOS if args.experiment == "all" else {args.experiment: DEMOS[args.experiment]}
    report = {name: run() for name, run in selected.items()}
    report["scope"] = "offline teaching only; no real robot or GPU validation"
    OUTPUT.mkdir(exist_ok=True)
    destination = OUTPUT / ("course_report.json" if args.experiment == "all" else args.experiment + ".json")
    destination.write_text(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False))
    print(f"Saved: {destination}")


if __name__ == "__main__":
    main()
