import collections
import math
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"labs"))
import algorithm_lab as lab
from course_lab import fk, ik


class AlgorithmTests(unittest.TestCase):
    def test_jacobian_against_central_difference(self):
        for q in [(0,0),(.3,.8),(-1.2,2.0)]:
            j=lab.jacobian(*q)
            for col in range(2):
                plus,minus=list(q),list(q)
                plus[col]+=1e-6; minus[col]-=1e-6
                a,b=fk(*plus),fk(*minus)
                for row in range(2):
                    self.assertAlmostEqual((a[row]-b[row])/2e-6,j[row][col],places=8)

    def test_ik_converges_and_history_descends(self):
        result=lab.numerical_ik()
        self.assertTrue(result["success"])
        self.assertLess(math.dist(fk(*result["q_rad"]),(.3,.2)),1e-6)
        errors=[r["error_m"] for r in result["history"]]
        self.assertTrue(all(b<=a for a,b in zip(errors,errors[1:])))

    def test_stationary_seed_is_not_proof_of_unreachable(self):
        result=lab.numerical_ik((.3,0),(0,0))
        self.assertFalse(result["success"])
        self.assertEqual(result["reason"],"stationary_seed")
        self.assertTrue(ik(.3,0))

    def test_unreachable_ik_and_iteration_budget(self):
        self.assertFalse(lab.numerical_ik((.7,0))["success"])
        r=lab.numerical_ik(max_steps=1)
        self.assertFalse(r["success"])
        self.assertEqual(r["reason"],"iteration_budget")

    def test_ik_invalid_damping(self):
        with self.assertRaises(ValueError): lab.numerical_ik(damping=0)

    def test_astar_known_detour_and_edges(self):
        result=lab.planning_demo()
        self.assertEqual(result["cost"],19)
        self.assertEqual(result["path"][0],(1,1))
        self.assertEqual(result["path"][-1],(10,1))
        self.assertFalse(set(result["path"]) & set(result["blocked"]))
        for a,b in zip(result["path"],result["path"][1:]):
            self.assertEqual(abs(a[0]-b[0])+abs(a[1]-b[1]),1)

    def test_astar_matches_independent_bfs(self):
        blocked={(2,0),(2,1),(2,3),(2,4),(4,3)}
        queue=collections.deque([((0,0),0)]); seen={(0,0)}
        expected=None
        while queue:
            p,d=queue.popleft()
            if p==(5,4): expected=d; break
            for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
                nxt=(p[0]+dx,p[1]+dy)
                if 0<=nxt[0]<6 and 0<=nxt[1]<5 and nxt not in blocked and nxt not in seen:
                    seen.add(nxt); queue.append((nxt,d+1))
        self.assertEqual(lab.astar(6,5,blocked,(0,0),(5,4))["cost"],expected)

    def test_astar_no_path_and_same_start(self):
        self.assertFalse(lab.astar(3,3,{(1,y) for y in range(3)},(0,0),(2,0))["success"])
        self.assertEqual(lab.astar(2,2,set(),(0,0),(0,0))["cost"],0)
        with self.assertRaises(ValueError): lab.astar(2,2,{(0,0)},(0,0),(1,1))

    def test_trapezoid_hand_calculation(self):
        r=lab.trapezoid()
        self.assertAlmostEqual(r["duration_s"],2.5)
        self.assertAlmostEqual(r["peak_rad_s"],.5)
        self.assertEqual(r["samples"][0]["q_rad"],0)
        self.assertEqual(r["samples"][-1]["q_rad"],1)
        self.assertEqual(r["samples"][-1]["v_rad_s"],0)
        self.assertTrue(all(abs(s["v_rad_s"])<=.5+1e-12 and abs(s["a_rad_s2"])<=1 for s in r["samples"]))

    def test_triangular_and_zero_moves(self):
        r=lab.trapezoid(distance=.1)
        self.assertEqual(r["shape"],"triangle")
        self.assertAlmostEqual(r["duration_s"],2*math.sqrt(.1))
        self.assertEqual(lab.trapezoid(distance=0)["duration_s"],0)

    def test_kalman_hand_update_and_measurement_trust(self):
        self.assertEqual(lab.kalman_step(0,1,2,0,1),(1,.5,.5))
        x,p,k=lab.kalman_step(0,1,2,0,9)
        self.assertAlmostEqual(x,.2); self.assertAlmostEqual(k,.1)
        self.assertGreater(p,0)
        with self.assertRaises(ValueError): lab.kalman_step(0,1,2,0,0)

    def test_pid_bounded_and_tracks_teaching_target(self):
        rows=lab.pid_demo()
        self.assertTrue(all(abs(r["torque_nm"])<=2 for r in rows))
        self.assertLess(abs(rows[-1]["q_rad"]-1),.03)


if __name__ == "__main__":
    unittest.main()
