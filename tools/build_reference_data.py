"""Create labelled teaching data; optionally snapshot local URDF declarations."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "labs"))
from course_lab import fk, demo_ai
from algorithm_lab import numerical_ik, trapezoid, pid_demo, filter_demo, planning_demo

OUT = ROOT / "references" / "data"


def write_csv(name, rows):
    rows = list(rows)
    with (OUT / name).open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot-models", type=Path,
                        help="Optional directory containing model/robot.urdf; not required for teaching data")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for q1, q2 in [(0, 0), (0, 90), (90, 0), (90, -90), (30, 60), (45, 45),
                   (0, 180), (180, 0), (-30, 60), (30, -60), (60, -120), (-90, 90)]:
        x, y = fk(math.radians(q1), math.radians(q2))
        rows.append(dict(q1_deg=q1, q2_deg=q2, x_m=x, y_m=y, x_cm=100*x, y_cm=100*y))
    write_csv("fk_reference.csv", rows)
    write_csv("lever_reference.csv", [dict(mass_kg=m, arm_m=l, gravity_m_s2=9.81,
               torque_nm=m*9.81*l) for m in (.2, .5, 1.0) for l in (.1, .2, .4)])
    trace = numerical_ik()["history"]
    write_csv("ik_trace.csv", [dict(iteration=r["iteration"], q1_rad=r["q_rad"][0],
               q2_rad=r["q_rad"][1], x_m=r["xy_m"][0], y_m=r["xy_m"][1], error_m=r["error_m"])
               for r in trace])
    write_csv("trajectory_reference.csv", trapezoid()["samples"])
    write_csv("pid_reference.csv", pid_demo())
    write_csv("filter_reference.csv", filter_demo())
    learning = demo_ai()
    write_csv("learning_reference.csv", [dict(split=split, observation=x, action=y)
               for split, key in [("train", "train_samples"), ("test", "heldout_samples")]
               for x, y in learning[key]])
    plan = planning_demo()
    write_csv("grid_reference.csv", [dict(x=x, y=y, blocked=int((x,y) in plan["blocked"]))
               for y in range(8) for x in range(12)])
    write_csv("path_reference.csv", [dict(step=i, x=x, y=y) for i, (x,y) in enumerate(plan["path"])])
    expected = {"fk_lengths_m": [.3, .2], "ik_target_m": [.3, .2],
                "ik_final_error_m": trace[-1]["error_m"], "astar_cost": plan["cost"],
                "trajectory_duration_s": 2.5, "trajectory_vmax_rad_s": .5,
                "trajectory_amax_rad_s2": 1.0, "pid_dt_s": .005,
                "pid_model": "unit inertia, viscous coefficient .3, torque clipped to +/-2",
                "filter_model": "scalar random walk, Q=.01, R=.25; deterministic sinusoidal teaching noise",
                "learning_heldout_mse": learning["heldout_mse"],
                "learning_baseline_mse": learning["constant_baseline_heldout_mse"],
                "randomness": "No random draws; explicit inputs and deterministic formulae",
                "scope": "Synthetic teaching examples, not hardware measurements"}
    (OUT / "expected_results.json").write_text(json.dumps(expected, indent=2)+"\n", encoding="utf-8")
    if args.snapshot_models:
        declarations, sources = [], []
        for model in ["spark2_v2", "D20260901B", "D20260902B60", "D20260903B10"]:
            path = args.snapshot_models / model / "robot.urdf"
            payload = path.read_bytes()
            sources.append(dict(model=model, source_relative=f"collision_shpere_generation/models/{model}/robot.urdf",
                                sha256=hashlib.sha256(payload).hexdigest()))
            robot = ET.fromstring(payload)
            for joint in robot.findall("joint"):
                if joint.get("type") != "revolute":
                    continue
                limit, origin, axis = joint.find("limit"), joint.find("origin"), joint.find("axis")
                declarations.append(dict(model=model, joint=joint.get("name"),
                    parent=joint.find("parent").get("link"), child=joint.find("child").get("link"),
                    lower_rad=limit.get("lower", ""), upper_rad=limit.get("upper", ""),
                    declared_velocity_rad_s=limit.get("velocity", ""), declared_effort_nm=limit.get("effort", ""),
                    origin_xyz_m=origin.get("xyz", "0 0 0") if origin is not None else "0 0 0",
                    axis=axis.get("xyz", "1 0 0") if axis is not None else "1 0 0"))
        write_csv("local_model_declarations.csv", declarations)
        (OUT / "local_model_sources.json").write_text(json.dumps({"snapshot_date": "2026-09-07",
            "scope": "URDF declarations only; not verified hardware ratings", "models": sources}, indent=2)+"\n", encoding="utf-8")
    manifest = []
    for path in sorted(OUT.iterdir()):
        if path.name == "manifest.json" or not path.is_file():
            continue
        entry = dict(file=path.name, sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                     kind="local_file_snapshot" if path.name.startswith("local_model") else "synthetic_teaching")
        if path.suffix == ".csv":
            with path.open(encoding="utf-8", newline="") as stream:
                reader = csv.DictReader(stream)
                entry["columns"] = reader.fieldnames
                entry["rows"] = sum(1 for _ in reader)
        manifest.append(entry)
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2)+"\n", encoding="utf-8")
    print("Reference files:", len(manifest), "in", OUT)


if __name__ == "__main__":
    main()
