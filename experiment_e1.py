"""Small runnable E1-style quotient experiment.

Not the 300-replicate numerical experiment in the paper. Here one path is
simulated from the EXACT rational rank-deficient construction and checked
at progressively increasing horizon lengths. No finance observations used.

Run: python examples/experiment_e1.py
"""
from __future__ import annotations
import json
from pathlib import Path
from fractions import Fraction as F
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from hmmcert import AffineRefresh, SolverSettings, solve, refresh_vertices
from hmmcert.geometry import diameter_approx

ROOT=Path(__file__).resolve().parents[1]
model=AffineRefresh.from_dict(json.loads((ROOT/'examples'/'rank_deficient.json').read_text()))
theta=(F(3,10),F(3,10),F(2,5))
T=5000
obs,_=model.hmm().sample(theta,T,20261121)
print('t,D_theta,D_q,outer_target_width,gap_lower,gap_upper,status,cells')
for t in (12,100,500,2000,5000):
    prefix=obs[:t]
    result=solve(model,prefix,SolverSettings(epsilon=F(1,200),max_memory=18,max_cells=32))
    dtheta=diameter_approx(result.vertices)
    dq=diameter_approx(result.vertices,model.signature)
    if result.bounds is None:
        print(f'{t},{dtheta:.6f},{dq:.6f},NA,NA,NA,{result.status},{len(result.cells)}')
    else:
        width=float(result.bounds[1]-result.bounds[0])
        print(f'{t},{dtheta:.6f},{dq:.6f},{width:.6f},{float(result.gaps[0]):.6f},'
              f'{float(result.gaps[1]):.6f},{result.status},{len(result.cells)}')
