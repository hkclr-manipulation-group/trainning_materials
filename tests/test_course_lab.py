import math
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "labs"))
import course_lab as lab


class CourseTests(unittest.TestCase):
    def test_units(self):
        self.assertAlmostEqual(lab.demo_units()["90_deg_in_rad"], math.pi / 2)

    def test_fk_hand_calculation(self):
        x, y = lab.fk(0, math.pi / 2)
        self.assertAlmostEqual(x, .3)
        self.assertAlmostEqual(y, .2)

    def test_ik_two_branches(self):
        solutions = lab.ik(.3, .2)
        self.assertGreater(solutions[0][1], 0)
        self.assertLess(solutions[1][1], 0)
        for solution in solutions:
            self.assertLess(math.dist(lab.fk(*solution), (.3, .2)), 1e-12)

    def test_ik_unreachable_inner_and_outer(self):
        self.assertEqual(lab.ik(.6, 0), [])
        self.assertEqual(lab.ik(0, 0), [])

    def test_invalid_geometry(self):
        for args in [(0, 0, -1, .2), (float("nan"), 0, .3, .2)]:
            with self.assertRaises(ValueError):
                lab.fk(*args)

    def test_protocol_golden_vector(self):
        payload = bytes.fromhex("a1 01 07 00 fa 00 00 00")
        self.assertEqual(lab.encode_frame(1, 7, .25), payload)
        self.assertEqual(lab.decode_frame(payload), {"node": 1, "sequence": 7, "angle_rad": .25})

    def test_protocol_negative_golden_vector(self):
        self.assertEqual(lab.encode_frame(2, 65535, -.25), bytes.fromhex("a1 02 ff ff 06 ff ff ff"))
        self.assertEqual(lab.decode_frame(bytes.fromhex("a1 02 ff ff 06 ff ff ff"))["angle_rad"], -.25)

    def test_bad_frames(self):
        for payload in [b"", bytes(7), bytes(9), bytes(8), bytes.fromhex("a1 00 07 00 fa 00 00 00")]:
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                lab.decode_frame(payload)

    def test_bad_encode(self):
        for node, seq, angle in [(0, 1, 0), (1, -1, 0), (1, 1, float("nan")), (1, 1, 3e6)]:
            with self.assertRaises(ValueError):
                lab.encode_frame(node, seq, angle)

    def test_feedback_boundary(self):
        self.assertTrue(lab.feedback_fresh(.1, .1))
        self.assertFalse(lab.feedback_fresh(.10001, .1))
        with self.assertRaises(ValueError):
            lab.feedback_fresh(-.1, .1)

    def test_control_convergence_and_speed(self):
        rows, final = lab.simulate_control()
        self.assertLess(abs(final - 1), 1e-6)
        self.assertTrue(all(abs(r["command_rad_s"]) <= .5 for r in rows))
        self.assertTrue(all(0 <= r["position_rad"] <= 1 for r in rows))

    def test_control_negative_target(self):
        _, final = lab.simulate_control(target=-1)
        self.assertLess(abs(final + 1), 1e-6)

    def test_control_invalid_period(self):
        with self.assertRaises(ValueError):
            lab.simulate_control(dt=0)

    def test_sphere_touching_and_symmetry(self):
        self.assertAlmostEqual(lab.sphere_gap((0, 0, 0), 1, (3, 0, 0), 2), 0)
        self.assertAlmostEqual(lab.sphere_gap((3, 0, 0), 2, (0, 0, 0), 1), 0)
        self.assertLess(lab.demo_collision()["oversized_sphere_gap_m"], 0)

    def test_fit_known_line(self):
        slope, intercept = lab.fit_line([(0, 1), (1, 3), (2, 5)])
        self.assertAlmostEqual(slope, 2)
        self.assertAlmostEqual(intercept, 1)
        self.assertEqual(lab.mse([(3, 7)], slope, intercept), 0)

    def test_fit_degenerate_and_empty(self):
        with self.assertRaises(ValueError):
            lab.fit_line([(1, 2), (1, 3)])
        with self.assertRaises(ValueError):
            lab.mse([], 1, 0)

    def test_ai_beats_baseline_on_disjoint_samples(self):
        result = lab.demo_ai()
        self.assertLess(result["heldout_mse"], result["constant_baseline_heldout_mse"])
        train_x = {x for x, _ in result["train_samples"]}
        test_x = {x for x, _ in result["heldout_samples"]}
        self.assertFalse(train_x & test_x)


if __name__ == "__main__":
    unittest.main()
