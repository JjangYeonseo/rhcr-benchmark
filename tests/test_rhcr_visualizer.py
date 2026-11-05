import tempfile
from pathlib import Path
import unittest
from scripts.visualize_rhcr import read_rhcr_map,read_rhcr_paths
from scripts.plot_comparison import read_csv

class TestRHCR(unittest.TestCase):
    def test_map_paths(self):
        with tempfile.TemporaryDirectory() as d:
            base=Path(d)
            mp=base/'case.map'
            mp.write_text('3,4\n1\n2\n100\n....\n.@e.\nr...\n',encoding='utf-8')
            grid=read_rhcr_map(mp)
            self.assertEqual(len(grid),3)
            pa=base/'paths.txt'
            pa.write_text('2\n0,-1,0;1,-1,1;2,-1,2;\n8,-1,0;9,-1,1;10,-1,2;\n',encoding='utf-8')
            ps,h=read_rhcr_paths(pa,grid)
            self.assertEqual((len(ps),h),(2,2))
    def test_mismatched_time_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            base=Path(d)
            pa=base/'paths.txt'
            pa.write_text('1\n0,-1,0;1,-1,2;\n',encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'nonconsecutive'):
                read_rhcr_paths(pa,['...'])
    def test_summary_csv(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'s.csv'
            p.write_text('Method,Goals,MeanPlanMs,MaxPlanMs\npbs_sipp_seed0,42,1.28,10.62\n',encoding='utf-8')
            self.assertEqual(read_csv(p)[0]['Goals'],42)
if __name__=='__main__': unittest.main()
