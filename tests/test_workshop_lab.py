import math
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "labs"))
from workshop_lab import (Frame, FeedbackRouter, pack_feedback, unpack_feedback,
                          drive_decision, speed_pi, stopping_distance,
                          fit_affine, calibration_report, interpolate_position)


class WorkshopTests(unittest.TestCase):
    def test_packet_against_independent_golden_bytes(self):
        golden = bytes.fromhex("d1 02 ff ff 06 ff ff ff 64 00 0c fe")
        self.assertEqual(pack_feedback(2, 65535, -250, 100, -500), golden)
        self.assertEqual(unpack_feedback(golden), {
            "node": 2, "sequence": 65535, "position_rad": -.25,
            "velocity_rad_s": .1, "current_a": -.5})

    def test_packet_signed_extremes_and_overflow(self):
        value = unpack_feedback(pack_feedback(1, 0, -(2**31), -32768, 32767))
        self.assertEqual(value["position_rad"], -(2**31)/1000)
        self.assertEqual(value["velocity_rad_s"], -32.768)
        for args in ((0, 0, 0, 0, 0), (1, 65536, 0, 0, 0),
                     (1, 0, 2**31, 0, 0), (1, 0, 0, 0, 40000),
                     (True, 0, 0, 0, 0)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                pack_feedback(*args)

    def test_packet_rejects_invalid_layout(self):
        golden = bytes.fromhex("d1 02 ff ff 06 ff ff ff 64 00 0c fe")
        for raw in (golden[:-1], golden+b"\x00", b"\xa1"+golden[1:], b"\xd1\x00"+golden[2:]):
            with self.assertRaises(ValueError):
                unpack_feedback(raw)

    def test_router_duplicate_does_not_refresh_or_replace(self):
        router = FeedbackRouter({(0, 0x282): 2})
        router.accept(Frame(0, 0x282, 1., pack_feedback(2, 7, -250, 0, 0)))
        self.assertEqual(router.accept(Frame(0, 0x282, 1.1, pack_feedback(2, 7, 999, 0, 0))), "duplicate")
        state = router.snapshot(1.15, .1)[0]
        self.assertFalse(state["fresh"])
        self.assertAlmostEqual(state["receive_age_s"], .15)
        self.assertEqual(state["value"]["position_rad"], -.25)

    def test_router_wrap_and_old_sequence(self):
        router = FeedbackRouter({(0, 0x282): 2})
        expected = ("accepted", "accepted", "old_or_ambiguous_sequence", "old_or_ambiguous_sequence")
        for k, (seq, result) in enumerate(zip((65535, 0, 65535, 32768), expected)):
            self.assertEqual(router.accept(Frame(0, 0x282, 1+k*.01,
                                                pack_feedback(2, seq, 0, 0, 0))), result)

    def test_router_invalid_input_cannot_pollute_valid_state(self):
        router = FeedbackRouter({(0, 0x282): 2})
        good = pack_feedback(2, 1, 250, 0, 0)
        router.accept(Frame(0, 0x282, 1., good))
        rejected = [
            (Frame(1, 0x282, 2., good), "unmapped_id"),
            (Frame(0, 0x282, 2., good, False), "wrong_frame_type"),
            (Frame(0, 0x282, 2., good[:-1]), "invalid_payload"),
            (Frame(0, 0x282, 2., pack_feedback(3, 2, 0, 0, 0)), "node_mismatch"),
            (Frame(0, 0x282, .5, pack_feedback(2, 2, 0, 0, 0)), "backward_time"),
            (Frame(0, 0x282, math.nan, good), "invalid_timestamp"),
        ]
        for frame, reason in rejected:
            self.assertEqual(router.accept(frame), reason)
        self.assertEqual(router.snapshot(2., .1)[0]["value"]["received_s"], 1.)

    def test_router_missing_node_and_snapshot_copy(self):
        router = FeedbackRouter({(0, 0x282): 2, (0, 0x283): 3})
        router.accept(Frame(0, 0x282, 1., pack_feedback(2, 1, 250, 0, 0)))
        result = router.snapshot(1., .1)
        self.assertIsNone(result[1]["value"])
        self.assertFalse(result[1]["fresh"])
        result[0]["value"]["position_rad"] = 99
        self.assertEqual(router.snapshot(1., .1)[0]["value"]["position_rad"], .25)

    def test_drive_requires_all_startup_conditions(self):
        self.assertEqual(drive_decision("PREOP", 0x40, True, True, True, True), "wait_bus_configuration")
        self.assertEqual(drive_decision("OP", 0x40, True, False, True, True), "wait_mode_and_target")
        self.assertEqual(drive_decision("OP", 0x40, True, True, True, False), "hold_disabled")
        self.assertEqual(drive_decision("OP", 0x40, True, True, True, True), "request_shutdown_0x0006")
        self.assertEqual(drive_decision("OP", 0x21, True, True, True, True), "request_switch_on_0x0007")
        self.assertEqual(drive_decision("OP", 0x23, True, True, True, True), "request_enable_0x000f")

    def test_enabled_drive_losing_conditions_enters_stop_policy(self):
        self.assertEqual(drive_decision("OP", 0x27, False, True, True, True), "stop_policy_invalid_feedback")
        self.assertEqual(drive_decision("SAFEOP", 0x27, True, True, True, True), "stop_policy_bus_not_op")
        self.assertEqual(drive_decision("OP", 0x27, True, False, True, True), "stop_policy_mode_or_target")
        self.assertEqual(drive_decision("OP", 0x27, True, True, True, False), "stop_policy")
        self.assertEqual(drive_decision("OP", 8, True, True, True, True), "diagnose_fault_manual_reset_required")

    def test_pi_first_step_matches_hand_integration(self):
        raw = speed_pi(antiwindup=False, duration_s=.04, step_until_s=.02)
        bounded = speed_pi(antiwindup=True, duration_s=.04, step_until_s=.02)
        self.assertAlmostEqual(raw[0]["integral_nm"], .04)
        self.assertEqual(bounded[0]["integral_nm"], 0.)
        self.assertAlmostEqual(raw[1]["velocity_rad_s"], .025)
        self.assertTrue(all(abs(r["torque_nm"]) <= 1 for r in raw+bounded))

    def test_antiwindup_improves_release_in_specified_model(self):
        plain = speed_pi(antiwindup=False)
        clamped = speed_pi(antiwindup=True)
        integral = lambda rows: sum(abs(r["velocity_rad_s"])*.005 for r in rows if r["t_s"] >= 3)
        self.assertLess(integral(clamped), integral(plain))
        self.assertTrue(all(abs(r["torque_nm"]) <= 1 for r in plain+clamped))

    def test_stopping_distance_delay_and_speed_scaling(self):
        self.assertAlmostEqual(stopping_distance(.5, 1., .04), .145)
        self.assertAlmostEqual(stopping_distance(.5, 1., .08), .165)
        self.assertAlmostEqual(stopping_distance(1., 1., .04), .54)
        with self.assertRaises(ValueError):
            stopping_distance(.5, 0, .04)

    def test_calibration_independent_points_and_degenerate_input(self):
        report = calibration_report([(0., 1.), (1., 3.), (2., 5.)], [(3., 7.2), (4., 8.8)])
        self.assertEqual((report["gain"], report["bias"]), (2., 1.))
        self.assertAlmostEqual(report["heldout_rmse"], .2)
        with self.assertRaises(ValueError):
            fit_affine([(1., 2.), (1., 3.)])

    def test_interpolation_uses_capture_time_not_latest(self):
        self.assertAlmostEqual(interpolate_position([(1., .2), (1.02, .24)], 1.005, .03), .21)
        self.assertEqual(interpolate_position([(1., .2), (1.02, .24)], 1.02, .03), .24)

    def test_interpolation_rejects_missing_bracket_and_large_gap(self):
        for samples, time, gap in (
            ([(1., .2), (1.02, .24)], 1.03, .03),
            ([(1., .2), (1.2, .24)], 1.005, .03),
            ([(1., .2), (1., .24)], 1., .03),
            ([(1., .2), (1.02, .24)], math.nan, .03),
        ):
            with self.assertRaises(ValueError):
                interpolate_position(samples, time, gap)


if __name__ == "__main__":
    unittest.main()
