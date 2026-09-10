"""Worked-course helpers: invented packets and offline models, no device access."""

from dataclasses import dataclass
import math
import struct

from engineering_lab import cia402_state


def _integer(value, low, high, name):
    if type(value) is not int or not low <= value <= high:
        raise ValueError(f"{name} must be an integer in [{low}, {high}]")


def pack_feedback(node, sequence, position_mrad, velocity_mrad_s, current_ma):
    """Invented 12-byte LE D1/node/seq/position/velocity/current teaching packet."""
    for value, low, high, name in (
        (node, 1, 127, "node"), (sequence, 0, 65535, "sequence"),
        (position_mrad, -(2**31), 2**31-1, "position"),
        (velocity_mrad_s, -32768, 32767, "velocity"),
        (current_ma, -32768, 32767, "current"),
    ):
        _integer(value, low, high, name)
    return struct.pack("<BBHihh", 0xD1, node, sequence, position_mrad,
                       velocity_mrad_s, current_ma)


def unpack_feedback(payload):
    if not isinstance(payload, (bytes, bytearray)) or len(payload) != 12:
        raise ValueError("Teaching feedback requires exactly 12 bytes")
    opcode, node, sequence, pos, vel, current = struct.unpack("<BBHihh", payload)
    if opcode != 0xD1 or not 1 <= node <= 127:
        raise ValueError("Wrong teaching opcode or node")
    return {"node": node, "sequence": sequence, "position_rad": pos / 1000.,
            "velocity_rad_s": vel / 1000., "current_a": current / 1000.}


@dataclass(frozen=True)
class Frame:
    channel: int
    can_id: int
    received_s: float
    payload: bytes
    is_fd: bool = True


class FeedbackRouter:
    """One receiver, per-channel/node records; recreated for each device session."""
    def __init__(self, routes):
        self.routes = dict(routes)  # (channel, CAN ID) -> payload node
        self.latest = {}

    def accept(self, frame):
        key = (frame.channel, frame.can_id)
        if key not in self.routes:
            return "unmapped_id"
        if not frame.is_fd:
            return "wrong_frame_type"
        if not math.isfinite(frame.received_s) or frame.received_s < 0:
            return "invalid_timestamp"
        try:
            value = unpack_feedback(frame.payload)
        except ValueError:
            return "invalid_payload"
        if value["node"] != self.routes[key]:
            return "node_mismatch"
        old = self.latest.get(key)
        if old is not None:
            if frame.received_s < old["received_s"]:
                return "backward_time"
            delta = (value["sequence"] - old["sequence"]) & 0xFFFF
            if delta == 0:
                return "duplicate"
            if delta >= 32768:
                return "old_or_ambiguous_sequence"
        self.latest[key] = {**value, "received_s": frame.received_s}
        return "accepted"

    def snapshot(self, now_s, max_age_s):
        if not math.isfinite(now_s) or not math.isfinite(max_age_s) or max_age_s < 0:
            raise ValueError("Finite clock and nonnegative age limit required")
        result = []
        for key, node in self.routes.items():
            value = self.latest.get(key)
            age = None if value is None else now_s - value["received_s"]
            result.append({"channel": key[0], "can_id": key[1], "node": node,
                           "receive_age_s": age,
                           "fresh": age is not None and 0 <= age <= max_age_s,
                           "value": None if value is None else dict(value)})
        return result


def drive_decision(al_state, statusword, feedback_valid, mode_confirmed,
                   target_aligned, start_requested):
    """Read-only decisions; target_aligned is a startup latch, not tracking error."""
    state = cia402_state(statusword)
    if not feedback_valid:
        return "stop_policy_invalid_feedback"
    if state in ("fault", "fault_reaction_active"):
        return "diagnose_fault_manual_reset_required"
    if al_state != "OP":
        return "stop_policy_bus_not_op" if state == "operation_enabled" else "wait_bus_configuration"
    if not start_requested:
        return "stop_policy" if state == "operation_enabled" else "hold_disabled"
    if not mode_confirmed or not target_aligned:
        return "stop_policy_mode_or_target" if state == "operation_enabled" else "wait_mode_and_target"
    return {"switch_on_disabled": "request_shutdown_0x0006",
            "ready_to_switch_on": "request_switch_on_0x0007",
            "switched_on": "request_enable_0x000f",
            "operation_enabled": "allow_bounded_reference"}.get(state, "wait_or_diagnose")


def speed_pi(kp=1., ki=2., antiwindup=True, dt=.005, duration_s=8.,
             step_until_s=3., reference=4., inertia=.2, damping=.3, limit=1.):
    """First-order speed plant J*v_dot=u-b*v; unreachable step then release."""
    values = (kp, ki, dt, duration_s, step_until_s, reference, inertia, damping, limit)
    if any(not math.isfinite(v) for v in values):
        raise ValueError("Finite parameters required")
    if min(dt, duration_s, inertia, limit) <= 0 or min(kp, ki, damping) < 0:
        raise ValueError("Invalid gain, plant, or integration parameters")
    steps = math.ceil(duration_s / dt)
    if steps > 1_000_000 or not 0 < step_until_s < duration_s:
        raise ValueError("Invalid duration or too many steps")
    v = integral_torque = 0.
    rows = []
    for k in range(steps):
        t = k * dt
        ref = reference if t < step_until_s else 0.
        error = ref - v
        proposed = integral_torque + ki * error * dt
        raw = kp * error + proposed
        # Integrate if unsaturated, or if the increment pulls out of saturation.
        if not antiwindup or abs(raw) <= limit or raw * error < 0:
            integral_torque = proposed
        raw = kp * error + integral_torque
        u = min(limit, max(-limit, raw))
        rows.append({"t_s": t, "reference_rad_s": ref, "velocity_rad_s": v,
                     "integral_nm": integral_torque, "raw_nm": raw, "torque_nm": u,
                     "saturated": abs(raw) > limit})
        v += dt * (u - damping * v) / inertia
        if not math.isfinite(v):
            raise ValueError("Numerically unstable integration")
    return rows


def stopping_distance(velocity, deceleration, delay_s):
    if any(not math.isfinite(x) for x in (velocity, deceleration, delay_s)):
        raise ValueError("Finite parameters required")
    if velocity < 0 or deceleration <= 0 or delay_s < 0:
        raise ValueError("Invalid stopping model")
    return velocity * delay_s + velocity**2 / (2 * deceleration)


def fit_affine(train):
    if len(train) < 2 or any(not math.isfinite(x) or not math.isfinite(y) for x, y in train):
        raise ValueError("Need finite training pairs")
    xm = sum(x for x, _ in train) / len(train)
    ym = sum(y for _, y in train) / len(train)
    denom = sum((x-xm)**2 for x, _ in train)
    if denom <= 1e-15:
        raise ValueError("Unidentifiable gain: training inputs do not vary enough")
    gain = sum((x-xm)*(y-ym) for x, y in train) / denom
    return gain, ym - gain*xm


def calibration_report(train, heldout):
    if not heldout or any(not math.isfinite(x) or not math.isfinite(y) for x, y in heldout):
        raise ValueError("Need finite independent evaluation pairs")
    gain, bias = fit_affine(train)
    rows = [{"input": x, "measured": y, "predicted": gain*x+bias,
             "residual": gain*x+bias-y} for x, y in heldout]
    return {"gain": gain, "bias": bias, "heldout": rows,
            "heldout_rmse": math.sqrt(sum(r["residual"]**2 for r in rows)/len(rows))}


def interpolate_position(samples, timestamp_s, max_gap_s):
    """Scalar interpolation inside a bracket only, with one common time base."""
    if len(samples) < 2 or not math.isfinite(timestamp_s) or max_gap_s <= 0 or not math.isfinite(max_gap_s):
        raise ValueError("Need samples and a finite positive gap")
    if any(not math.isfinite(t) or not math.isfinite(q) for t, q in samples):
        raise ValueError("Finite samples required")
    if any(b[0] <= a[0] for a, b in zip(samples, samples[1:])):
        raise ValueError("Sample timestamps must increase strictly")
    for t, q in samples:
        if timestamp_s == t:
            return q
    for (ta, qa), (tb, qb) in zip(samples, samples[1:]):
        if ta < timestamp_s < tb:
            if tb - ta > max_gap_s:
                raise ValueError("Interpolation bracket is too wide")
            fraction = (timestamp_s-ta)/(tb-ta)
            return qa + fraction*(qb-qa)
    raise ValueError("No bracket: extrapolation is not allowed")
