import math,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'labs'))
from spatial_lab import *

class SpatialTests(unittest.TestCase):
    def test_hand_computed_matrix(self):
        self.assertEqual(matmul([[1,2],[3,4]],[[2,0],[1,2]]),[[4,4],[10,8]])
    def test_dimensions(self):
        with self.assertRaises(ValueError): matmul([[1,2]],[[1,2]])
        with self.assertRaises(ValueError): matmul([[1],[2,3]],[[1]])
    def test_point_and_direction(self):
        t=homogeneous(rz(math.pi/2),[.3,.1,0])
        for a,b in zip(transform(t,[.2,.1,0]),[.2,.3,0]): self.assertAlmostEqual(a,b)
        for a,b in zip(transform(t,[.2,.1,0],True),[-.1,.2,0]): self.assertAlmostEqual(a,b)
    def test_noncommuting_transforms(self):
        r=rotation_z(math.pi/2);s=translation(1)
        for t,wanted in [(matmul(s,r),[1,1,0]),(matmul(r,s),[0,2,0])]:
            for a,b in zip(transform(t,[1,0,0]),wanted): self.assertAlmostEqual(a,b)
    def test_inverse_hand_translation(self):
        inverse=inverse_rigid(homogeneous(rz(math.pi/2),[.3,.1,0]))
        for row,b in zip(inverse[:3],[-.1,.3,0]): self.assertAlmostEqual(row[3],b)
    def test_reflection_rejected(self):
        with self.assertRaises(ValueError): inverse_rigid(homogeneous([[1,0,0],[0,1,0],[0,0,-1]],[0,0,0]))
    def test_fk_against_trigonometry(self):
        for a,b in [(0,0),(.3,.7),(-1,2),(math.pi/6,math.pi/3)]:
            p=transform(fk_matrix(a,b),[0,0,0])
            self.assertAlmostEqual(p[0],.3*math.cos(a)+.2*math.cos(a+b))
            self.assertAlmostEqual(p[1],.3*math.sin(a)+.2*math.sin(a+b))
    def test_uart_fixed_vector(self):
        self.assertEqual(uart_8n1(0xA5),[0,1,0,1,0,0,1,0,1,1])
        self.assertEqual(uart_payload_rate(115200),11520)
    def test_wire_hand_values(self):
        self.assertAlmostEqual(spi_transfer_seconds(76,1e6),.000608)
        self.assertAlmostEqual(parallel_resistance([120,120]),60)
    def test_invalid_wire_inputs(self):
        for call in [lambda:uart_8n1(256),lambda:spi_transfer_seconds(-1,1),lambda:parallel_resistance([0]),lambda:uart_payload_rate(0)]:
            with self.assertRaises(ValueError): call()

if __name__=='__main__': unittest.main()
