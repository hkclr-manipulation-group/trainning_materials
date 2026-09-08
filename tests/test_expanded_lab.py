import math
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"labs"))
from course_lab import fk
from expanded_lab import LengthPrefixedDecoder, framed, arbitration_trace, ik_dataset, nearest_seed, branch_average_example, delay_response


class ExpandedLabTests(unittest.TestCase):
    def test_stream_every_two_chunk_boundary(self):
        wire = framed(b"ABC") + framed(b"DE")
        for boundary in range(len(wire)+1):
            decoder = LengthPrefixedDecoder()
            result = decoder.feed(wire[:boundary])+decoder.feed(wire[boundary:])
            self.assertEqual(result, [b"ABC", b"DE"])
            self.assertFalse(decoder.buffer)

    def test_stream_byte_at_a_time(self):
        decoder = LengthPrefixedDecoder()
        result = []
        for value in b"\x00\x03ABC\x00\x02DE":
            result += decoder.feed(bytes([value]))
        self.assertEqual(result, [b"ABC", b"DE"])

    def test_invalid_length_poisoning(self):
        decoder = LengthPrefixedDecoder(max_length=8)
        with self.assertRaises(ValueError):
            decoder.feed(b"\x00\x09")
        with self.assertRaises(ValueError):
            decoder.feed(b"\x00\x01A")
        decoder.reset()
        self.assertEqual(decoder.feed(b"\x00\x01A"), [b"A"])

    def test_can_known_bit(self):
        trace = arbitration_trace()
        self.assertEqual(trace[-1]["active"], [0x100])
        losses = [(r["bit"], r["lost"]) for r in trace if r["lost"]]
        self.assertEqual(losses, [(5, [0x120])])
        with self.assertRaises(ValueError):
            arbitration_trace([0x800])

    def test_mean_not_an_inverse(self):
        result = branch_average_example()
        for q in result["solutions"]:
            self.assertLess(math.dist(fk(*q), result["target"]), 1e-12)
        self.assertAlmostEqual(result["error_m"], .5-math.sqrt(.13))

    def test_seed_is_from_data(self):
        data = ik_dataset()
        target = (.3, .2)
        q = nearest_seed(target, data)
        self.assertIn((fk(*q), q), data)
        self.assertAlmostEqual(math.dist(fk(*q), target), min(math.dist(p,target) for p,_ in data))

    def test_feedback_no_delay_closed_form(self):
        rows = delay_response(delay_steps=0)
        for k, row in enumerate(rows):
            self.assertAlmostEqual(row["q_rad"], 1-(1-.12)**k)

    def test_feedback_delay_uses_old_position(self):
        rows = delay_response(delay_steps=2, steps=5)
        self.assertAlmostEqual(rows[2]["q_rad"], .24)
        self.assertEqual(rows[2]["measured_rad"], 0.)
        self.assertAlmostEqual(rows[3]["measured_rad"], .12)


if __name__ == "__main__":
    unittest.main()
