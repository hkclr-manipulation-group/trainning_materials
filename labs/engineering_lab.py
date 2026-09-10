"""Deterministic engineering exercises. No device, socket, or hardware access."""

import argparse
import json
import math
from pathlib import Path
import statistics
import struct

from algorithm_lab import jacobian
from course_lab import fk


FD_LENGTHS = tuple(range(9)) + (12, 16, 20, 24, 32, 48, 64)


def fd_layout(application_bytes):
    """Choose the smallest wire capacity; does not define protocol padding bytes."""
    if type(application_bytes) is not int or not 0 <= application_bytes <= 64:
        raise ValueError("Application length must be an integer from 0 to 64")
    dlc = next(i for i, capacity in enumerate(FD_LENGTHS) if capacity >= application_bytes)
    capacity = FD_LENGTHS[dlc]
    return {"application_bytes": application_bytes, "dlc": dlc,
            "wire_bytes": capacity, "padding_bytes": capacity - application_bytes}


def cia402_state(statusword):
    """Decode standard state bits only, not mode-specific diagnostics or interlocks."""
    if type(statusword) is not int or not 0 <= statusword <= 0xFFFF:
        raise ValueError("Statusword must be a uint16")
    for mask, value, state in (
        (0x004F, 0x0000, "not_ready"),
        (0x004F, 0x0040, "switch_on_disabled"),
        (0x006F, 0x0021, "ready_to_switch_on"),
        (0x006F, 0x0023, "switched_on"),
        (0x006F, 0x0027, "operation_enabled"),
        (0x006F, 0x0007, "quick_stop_active"),
        (0x004F, 0x000F, "fault_reaction_active"),
        (0x004F, 0x0008, "fault"),
    ):
        if statusword & mask == value:
            return state
    return "unknown"


def decode_teaching_pdo(payload):
    """Only this exercise's packed LE uint16 status + int32 position layout."""
    if not isinstance(payload, (bytes, bytearray)) or len(payload) != 6:
        raise ValueError("Teaching PDO must contain exactly 6 bytes")
    status, position = struct.unpack("<Hi", payload)
    return {"statusword": status, "drive_state": cia402_state(status),
            "position_counts": position}


def process_input(payload, actual_wkc, expected_wkc):
    """Illustrate rejecting incomplete process exchange before publishing input."""
    if type(expected_wkc) is not int or expected_wkc <= 0:
        raise ValueError("Expected WKC must be a positive configured value")
    if type(actual_wkc) is not int or actual_wkc < 0:
        raise ValueError("Actual WKC must be a nonnegative integer")
    if actual_wkc != expected_wkc:
        return {"valid": False, "reason": "wkc_mismatch", "input": None}
    return {"valid": True, "reason": "exchange_valid_only",
            "input": decode_teaching_pdo(payload)}


def timing_report(starts_s, durations_s, period_s):
    """Deadlines relative to first release; starts/durations use one clock."""
    if len(starts_s) < 2 or len(starts_s) != len(durations_s):
        raise ValueError("Need matching start/duration arrays with at least two cycles")
    if not math.isfinite(period_s) or period_s <= 0:
        raise ValueError("Period must be positive and finite")
    if any(not math.isfinite(x) for x in [*starts_s, *durations_s]):
        raise ValueError("Times must be finite")
    if any(x < 0 for x in durations_s):
        raise ValueError("Durations cannot be negative")
    if any(b <= a for a, b in zip(starts_s, starts_s[1:])):
        raise ValueError("Cycle starts must be strictly increasing")
    intervals = [b - a for a, b in zip(starts_s, starts_s[1:])]
    rows = []
    for k, (start, duration) in enumerate(zip(starts_s, durations_s)):
        release = starts_s[0] + k * period_s
        lateness = max(0., start + duration - (release + period_s))
        rows.append({"cycle": k, "start_s": start,
                     "release_error_s": start - release,
                     "finish_s": start + duration,
                     "deadline_lateness_s": lateness,
                     "missed": lateness > 1e-12})
    return {"mean_interval_s": statistics.mean(intervals),
            "max_interval_s": max(intervals),
            "missed_deadlines": sum(row["missed"] for row in rows), "cycles": rows}


def sample_segment(start, end, forbidden, segments):
    """Deliberately discrete 1D checker, to demonstrate a thin-obstacle miss."""
    if type(segments) is not int or segments < 1:
        raise ValueError("Positive integer segment count required")
    lo, hi = forbidden
    if any(not math.isfinite(x) for x in (start, end, lo, hi)) or lo > hi:
        raise ValueError("Finite ordered obstacle interval required")
    points = [start + (end - start) * i / segments for i in range(segments + 1)]
    collisions = [x for x in points if lo <= x <= hi]
    return {"samples": points, "collisions": collisions,
            "sampled_valid": not collisions,
            "scope": "discrete samples, not continuous collision certification"}


def episode_overlap(train_ids, test_ids):
    return sorted(set(train_ids).intersection(test_ids))


def transition(state, event):
    """Small teaching application, not a hardware or safety controller."""
    states = {"DISCONNECTED", "READY", "RUNNING", "FAULT"}
    events = {"verified_connection", "start", "fault", "connection_restored",
              "verified_reset", "stop", "disconnect"}
    if state not in states or event not in events:
        raise ValueError("Unknown teaching state/event")
    if event == "disconnect":
        return "DISCONNECTED"
    if event == "fault":
        return "FAULT"
    return {("DISCONNECTED", "verified_connection"): "READY",
            ("READY", "start"): "RUNNING",
            ("RUNNING", "stop"): "READY",
            ("FAULT", "verified_reset"): "READY"}.get((state, event), state)


def canfd_demo():
    rows = [fd_layout(n) for n in (0, 8, 9, 12, 33, 64)]
    try:
        fd_layout(65)
    except ValueError as error:
        rejected = str(error)
    payload_bits_per_s = 6 * 1000 * 2 * 32 * 8
    return {"lengths": rows, "length_65_rejected": rejected,
            "payload_only_bits_per_s": payload_bits_per_s,
            "payload_only_fraction_at_5mbps": payload_bits_per_s / 5_000_000,
            "scope": "excludes arbitration, stuffing, CRC, gaps, retries and host overhead"}


def ethercat_demo():
    raw = bytes.fromhex("27 00 18 FC FF FF")
    try:
        decode_teaching_pdo(raw[:-1])
    except ValueError as error:
        rejected = str(error)
    return {"raw_hex": raw.hex(" "), "decoded": decode_teaching_pdo(raw),
            "additional_status_bits": cia402_state(0x1227),
            "complete_exchange": process_input(raw, 6, 6),
            "incomplete_exchange": process_input(raw, 4, 6),
            "truncated_rejected": rejected,
            "scope": "expected WKC=6 is a supplied teaching assumption, not slave count"}


def math_demo():
    q = (.4, .8)
    h = 1e-6
    analytic = jacobian(*q)
    numeric = [[0., 0.], [0., 0.]]
    for col in range(2):
        plus, minus = list(q), list(q)
        plus[col] += h
        minus[col] -= h
        fp, fm = fk(*plus), fk(*minus)
        for row in range(2):
            numeric[row][col] = (fp[row] - fm[row]) / (2 * h)
    errors = [abs(analytic[i][j] - numeric[i][j]) for i in range(2) for j in range(2)]
    return {"q_rad": q, "h_rad": h, "analytic": analytic, "numeric": numeric,
            "max_abs_error": max(errors),
            "zero_offset_tip_error_m": .5 * math.radians(.1),
            "static_torque_nm": .8 * 9.81 * .4 + .6 * 9.81 * .15,
            "load_inertia_kg_m2": .8 * .4**2 + .6 * .3**2 / 3}


def timing_demo():
    return timing_report([0., .001, .0024, .003, .004],
                         [.0003, .0004, .0008, .0004, .0003], .001)


def planning_demo():
    return {"endpoints_only": sample_segment(0., 1., (.49, .51), 1),
            "with_midpoint": sample_segment(0., 1., (.49, .51), 2)}


def perception_demo():
    fx, cx, u, z = 500., 320., 370., 1.
    return {"x_camera_m": (u - cx) * z / fx,
            "one_pixel_x_error_m": z / fx,
            "depth_10mm_x_error_m": (u - cx) / fx * .01,
            "wrong_time_transform_error_m": .2 * .040,
            "scope": "pinhole, optical-axis depth, constant translation, no rotation"}


def ai_demo():
    return {"leaking_split_overlap": episode_overlap(["A", "A", "B"], ["A", "C"]),
            "episode_split_overlap": episode_overlap(["A", "B"], ["C", "D"]),
            "scope": "no episode overlap alone does not prove no scene or preprocessing leakage"}


def software_demo():
    state = "DISCONNECTED"
    rows = []
    for event in ("verified_connection", "start", "fault", "connection_restored",
                  "start", "verified_reset", "start", "stop"):
        previous = state
        state = transition(state, event)
        rows.append({"before": previous, "event": event, "after": state})
    return rows


DEMOS = {"math": math_demo, "canfd": canfd_demo, "ethercat": ethercat_demo,
         "timing": timing_demo, "planning": planning_demo,
         "perception": perception_demo, "ai": ai_demo, "software": software_demo}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("experiment", choices=[*DEMOS, "all"])
    args = parser.parse_args()
    selected = DEMOS if args.experiment == "all" else {args.experiment: DEMOS[args.experiment]}
    report = {"scope": "synthetic offline exercises; no hardware verification",
              "experiments": {name: run() for name, run in selected.items()}}
    out = Path(__file__).resolve().parents[1] / "outputs"
    out.mkdir(exist_ok=True)
    destination = out / f"engineering_{args.experiment}.json"
    destination.write_text(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False)
                           + "\n", encoding="utf-8")
    print("Completed:", ", ".join(selected))
    print("Saved:", destination)


if __name__ == "__main__":
    main()
