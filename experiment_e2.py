"""Small Monte Carlo check of per-path time-simultaneous region inclusion.

Reports Monte Carlo fractions, NOT a formal empirical replication of E2's
300 trajectories, all methods and exact endpoint decisions.

Run: python examples/experiment_e2.py
"""
from __future__ import annotations
import json
from pathlib import Path
from fractions import Fraction as F
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from hmmcert import AffineRefresh, in_refresh_region, in_block_region, in_lr_region

ROOT=Path(__file__).resolve().parents[1]
model=AffineRefresh.from_dict(json.loads((ROOT/'examples'/'rank_deficient.json').read_text()))
hmm=model.hmm()
true=(F(3,10),F(3,10),F(2,5))
alpha=F(1,20)
ref=[((F(i,10),F(0),F(10-i,10)),F(1,11)) for i in range(11)]
R,T=20,20
covered=[0,0,0]
for seed in range(R):
    obs,_=hmm.sample(true,T,seed=20261121+seed)
    flags=[True,True,True]
    for t in range(2,T+1):
        p=obs[:t]
        flags[0]&=in_refresh_region(model,p,true,alpha)
        flags[1]&=in_block_region(hmm,p,true,B=2,alpha=alpha)
        flags[2]&=in_lr_region(hmm,p,true,ref,alpha)
    covered=[x+int(flag) for x,flag in zip(covered,flags)]
for label,num in zip(('one-symbol polytope','block-frequency B=2','likelihood ratio'),covered):
    print(f'{label}: {num}/{R} sample paths included at every checkpoint 2..{T}')
print('These are exploratory Monte Carlo counts, not guarantees about the fitted financial model.')
