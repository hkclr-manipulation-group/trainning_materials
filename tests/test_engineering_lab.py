import math
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "labs"))
from engineering_lab import (cia402_state, decode_teaching_pdo, fd_layout, math_demo,
                             process_input, timing_report, sample_segment,
                             episode_overlap, transition)


class EngineeringTests(unittest.TestCase):
    def test_fd_boundaries_and_padding(self):
        self.assertEqual(fd_layout(9), {"application_bytes": 9, "dlc": 9,
                                        "wire_bytes": 12, "padding_bytes": 3})
        self.assertEqual(fd_layout(33)["wire_bytes"], 48)
        self.assertEqual(fd_layout(64)["dlc"], 15)
        self.assertEqual(fd_layout(0)["wire_bytes"], 0)
        for n in (8, 12, 16, 20, 24, 32, 48, 64):
            self.assertEqual(fd_layout(n)["padding_bytes"], 0)

    def test_fd_rejects_bad_lengths_without_truncation(self):
        for n in (-1, 65, 9.0, True, None):
            with self.subTest(n=n), self.assertRaises(ValueError):
                fd_layout(n)

    def test_pdo_signed_position_and_known_bytes(self):
        decoded = decode_teaching_pdo(bytes.fromhex("27 00 18 fc ff ff"))
        self.assertEqual(decoded["position_counts"], -1000)
        self.assertEqual(decoded["drive_state"], "operation_enabled")
        self.assertEqual(decode_teaching_pdo(bytes.fromhex("40 00 00 00 00 80"))[
            "position_counts"], -(2**31))

    def test_pdo_rejects_truncation_and_extra_fields(self):
        for n in (0, 5, 7, 8):
            with self.subTest(n=n), self.assertRaises(ValueError):
                decode_teaching_pdo(bytes(n))

    def test_drive_state_masks_ignore_unrelated_bits(self):
        self.assertEqual(cia402_state(0x1227), "operation_enabled")
        self.assertEqual(cia402_state(0x0240), "switch_on_disabled")
        self.assertEqual(cia402_state(0x0008), "fault")
        self.assertEqual(cia402_state(0x000F), "fault_reaction_active")
        self.assertEqual(cia402_state(0x0007), "quick_stop_active")
        self.assertEqual(cia402_state(0x006F), "unknown")

    def test_incomplete_exchange_cannot_publish_cached_input(self):
        raw = bytes.fromhex("27 00 18 fc ff ff")
        self.assertTrue(process_input(raw, 6, 6)["valid"])
        failed = process_input(raw, 4, 6)
        self.assertFalse(failed["valid"])
        self.assertIsNone(failed["input"])

    def test_expected_wkc_requires_configuration(self):
        for expected in (0, -1, True):
            with self.assertRaises(ValueError):
                process_input(bytes(6), 0, expected)

    def test_mean_period_can_hide_deadline_miss(self):
        report = timing_report([0., .001, .0024, .003, .004],
                               [.0003, .0004, .0008, .0004, .0003], .001)
        self.assertAlmostEqual(report["mean_interval_s"], .001)
        self.assertEqual(report["missed_deadlines"], 1)
        self.assertAlmostEqual(report["cycles"][2]["deadline_lateness_s"], .0002)

    def test_timing_rejects_invalid_clock_data(self):
        for starts, durations, period in (([0., 0.], [0., 0.], .001),
                                         ([0., math.nan], [0., 0.], .001),
                                         ([0., .001], [0., -1.], .001),
                                         ([0., .001], [0., 0.], 0)):
            with self.assertRaises(ValueError):
                timing_report(starts, durations, period)

    def test_jacobian_against_independent_finite_difference(self):
        report = math_demo()
        self.assertLess(report["max_abs_error"], 1e-8)
        self.assertAlmostEqual(report["static_torque_nm"], 4.0221)
        self.assertAlmostEqual(report["load_inertia_kg_m2"], .146)

    def test_thin_obstacle_missed_by_endpoint_only_check(self):
        self.assertTrue(sample_segment(0., 1., (.49, .51), 1)["sampled_valid"])
        self.assertEqual(sample_segment(0., 1., (.49, .51), 2)["collisions"], [.5])

    def test_episode_split_detects_neighbor_frame_leakage(self):
        self.assertEqual(episode_overlap(["A", "A", "B"], ["A", "C"]), ["A"])
        self.assertEqual(episode_overlap(["A", "B"], ["C"]), [])

    def test_reconnect_cannot_restart_motion(self):
        state = transition("RUNNING", "fault")
        state = transition(state, "connection_restored")
        self.assertEqual(transition(state, "start"), "FAULT")
        state = transition(state, "verified_reset")
        self.assertEqual(state, "READY")
        self.assertEqual(transition(state, "start"), "RUNNING")


if __name__ == "__main__":
    unittest.main()
