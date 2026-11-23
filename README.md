## 1. Quick Start

Requires Python **3.10+**, and Python 3.11 is recommended.

```bash
# Enter the directory of the decompressed project
cd hmm_paper_code

# One command sequence: Simulation observation -> Construction of confidence interval -> Bernstein precise optimization -> Saving of JSON certificate -> Playback
python run.py demo

# Independently verify the certificate that was just generated
python run.py verify demo_certificate.json

# Check all tests (pytest needs to be installed)
python -m pip install -e '.[test]'
python -m pytest -q
```
You can directly use `python -m hmmcert demo` or run `hmmcert demo` after installation.
### Use the financial model from the paper (no need to connect to the internet)

```bash
python run.py demo --model finance --length 12 --output finance_certificate.json
python run.py verify finance_certificate.json
```

## VI. Project Outline

```text
hmm_paper_code/
├── run.py                         # One-click entry point
├── pyproject.toml                 # Installable, no additional core dependencies
├── README.md                      # This Chinese description
├── hmmcert/
│   ├── __main__.py                # commands for demo, certification, verification, inspection
│   ├── exact.py                   # Fraction, matrix solving, sqrt/log strict rational upper bounds
│   ├── model.py                   # General shared hybrid HMM + affine refresh model
│   ├── identifiability.py         # Finite alphabet target equivalence and sensitivity
│   ├── confidence.py              # Three types of time-consistent statistical confidence regions
│   ├── geometry.py                # Exact rational geometry for K<=3
│   ├── bernstein.py               # Region contraction + integer lift + endpoint bounds
│   ├── solver.py                  # Global subdivision solver for two-sided gap verification
│   └── certificate.py             # Certificate creation and complete geometry / numerical replay
├── examples/
│   ├── rank_deficient.json        # The precise rank-deficient model of Paper E1
│   ├── finance.json               # The fixed financial matrix of Paper E6
│   ├── observations.json          # User-defined input examples
│   ├── experiment_e1.py          # Simplified E1 experiment
│   ├── experiment_e2.py          # Simplified E2 experiment
│   └── finance_from_symbols.py   # Using financial matrix to process custom symbols
├── tests/                         # pytest automated tests
└── paper_sources/                 # Uploaded original LaTeX and Fig1 for easy verification
```

## VII. Python API Examples

```python
import json
from fractions import Fraction as F
from hmmcert import AffineRefresh, SolverSettings, solve
from hmmcert.certificate import build_certificate, verify_certificate

model = AffineRefresh.from_dict(json.load(open("examples/rank_deficient.json")))
observations = [0, 1, 1, 0, 1, 0]
result = solve(model, observations, SolverSettings(alpha = F(1, 20), epsilon = F(1, 200)))
print(result.status, result.bounds, result.gaps)
certificate = build_certificate(model,result)
print(verify_certificate(certificate))
```
