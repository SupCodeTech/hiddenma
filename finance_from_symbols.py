"""Use the manuscript's frozen finance model on your own categorical prefix.

Requires only a JSON array of 0-indexed symbols 0,1,2,3.
Example: python examples/finance_from_symbols.py examples/observations.json
The manuscript encodes its observations as Y=1+2V+C, hence subtract one
when supplying paper-indexed symbols.
"""
from __future__ import annotations
import json,sys
from pathlib import Path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from hmmcert import AffineRefresh, SolverSettings, solve
from hmmcert.certificate import build_certificate,save_certificate

ROOT=Path(__file__).resolve().parents[1]
if len(sys.argv)!=2:
    raise SystemExit('usage: python examples/finance_from_symbols.py observations.json')
model=AffineRefresh.from_dict(json.loads((ROOT/'examples'/'finance.json').read_text()))
observations=json.loads(Path(sys.argv[1]).read_text())
result=solve(model,observations,SolverSettings())
save_certificate(build_certificate(model,result),'finance_custom_certificate.json')
print('status:',result.status)
print('exact posterior interval:',None if result.bounds is None else result.bounds[:2])
print('extremum certification gaps:',result.gaps)
print('certificate: finance_custom_certificate.json')
