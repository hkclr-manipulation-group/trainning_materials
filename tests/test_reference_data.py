import csv
import hashlib
import json
import math
from pathlib import Path
import unittest

DATA = Path(__file__).resolve().parents[1]/"references"/"data"


def rows(name):
    with (DATA/name).open(encoding="utf-8",newline="") as stream:
        return list(csv.DictReader(stream))


class ReferenceDataTests(unittest.TestCase):
    def test_manifest_matches_files_and_row_counts(self):
        for item in json.loads((DATA/"manifest.json").read_text(encoding="utf-8")):
            payload=(DATA/item["file"]).read_bytes()
            self.assertEqual(hashlib.sha256(payload).hexdigest(),item["sha256"])
            if "rows" in item:
                self.assertEqual(len(rows(item["file"])),item["rows"])

    def test_fk_table_has_independent_right_angle_answers(self):
        table={(int(r["q1_deg"]),int(r["q2_deg"])):r for r in rows("fk_reference.csv")}
        for key,answer in [((0,0),(.5,0)),((0,90),(.3,.2)),((90,0),(0,.5)),((90,-90),(.2,.3))]:
            self.assertAlmostEqual(float(table[key]["x_m"]),answer[0])
            self.assertAlmostEqual(float(table[key]["y_m"]),answer[1])

    def test_path_reference_has_valid_steps_and_no_blocked_nodes(self):
        blocked={(int(r["x"]),int(r["y"])) for r in rows("grid_reference.csv") if int(r["blocked"])}
        path=[(int(r["x"]),int(r["y"])) for r in rows("path_reference.csv")]
        self.assertEqual(len(path)-1,19)
        self.assertFalse(set(path)&blocked)
        for a,b in zip(path,path[1:]):
            self.assertEqual(abs(a[0]-b[0])+abs(a[1]-b[1]),1)

    def test_trajectory_reference_has_expected_limits(self):
        table=rows("trajectory_reference.csv")
        self.assertEqual(float(table[0]["q_rad"]),0)
        self.assertEqual(float(table[-1]["q_rad"]),1)
        self.assertEqual(float(table[-1]["t_s"]),2.5)
        self.assertTrue(all(abs(float(r["v_rad_s"]))<=.5+1e-12 for r in table))

    def test_learning_split_has_disjoint_inputs(self):
        table=rows("learning_reference.csv")
        train={r["observation"] for r in table if r["split"]=="train"}
        test={r["observation"] for r in table if r["split"]=="test"}
        self.assertEqual((len(train),len(test)),(6,5))
        self.assertFalse(train&test)

    def test_snapshot_is_labelled_and_retains_zero_declarations(self):
        metadata=json.loads((DATA/"local_model_sources.json").read_text(encoding="utf-8"))
        self.assertIn("not verified",metadata["scope"])
        self.assertEqual(len(metadata["models"]),4)
        table=rows("local_model_declarations.csv")
        self.assertEqual(len(table),24)
        design=[r for r in table if r["model"].startswith("D2026")]
        self.assertEqual(len(design),18)
        self.assertTrue(all(float(r["declared_velocity_rad_s"])==0 for r in design))


if __name__ == "__main__":
    unittest.main()
