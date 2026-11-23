# hiddenma — certified time-uniform posterior intervals for shared-transition HMMs

[中文说明](README.zh-CN.md)

Exact-arithmetic reference implementation accompanying the paper

> *Functional identifiability and certified time-uniform posterior inference in hidden Markov models with transition matrices mixed from known modes* (J. Chen).

For a hidden Markov model whose transition matrix is a mixture of known, strictly positive modes, with one unknown weight vector shared over the whole observation sequence, the package

1. builds the observation-only, time-uniform confidence region for the mixture weights;
2. encloses the minimum and maximum of a target posterior (e.g. the stress-state probability) over that region using positive Bernstein coefficient ratios, an exact forgetting bound and feasible witnesses;
3. writes a JSON certificate that an independent verifier can replay.

The core uses only the Python standard library (`fractions.Fraction`); no floating-point result is ever trusted as a bound. Simulation outputs used in the paper are archived separately on Zenodo: <https://doi.org/10.5281/zenodo.24462482>.

## Quick start

Requires Python 3.10 or later.

```bash
git clone https://github.com/SupCodeTech/hiddenma.git
cd hiddenma

python run.py demo                                   # simulate -> confidence region -> certify -> save -> replay
python run.py verify demo_certificate.json           # independent replay of the certificate

python -m pip install -e '.[test]'
python -m pytest -q                                  # 33 tests, a few seconds
```

After installation, `hmmcert demo` and `python -m hmmcert demo` are equivalent to `python run.py demo`.

### Built-in demonstration models

```bash
python run.py demo --model rank_deficient            # Section 3.4 / experiment E1 (S=K=3)
python run.py demo --model finance --length 12       # frozen market-stress inputs of Section 7 (E6)
python run.py demo --model four_mode --length 40 --max-memory 10   # K=4 modes, 3-dimensional polytope
```

`--model finance` uses only the paper's frozen matrices with freshly simulated observations; it does not reproduce the 2022–2024 market study.

### Certify your own observation sequence

```bash
python run.py certify --model examples/rank_deficient.json \
    --observations examples/observations.json \
    --alpha 1/20 --epsilon 1/200 --max-memory 18 --max-cells 48 \
    --output my_certificate.json
python run.py verify my_certificate.json
```

Observations are a JSON array of integer symbols, 0-based by default. Add `--paper-indexed` to supply the paper's 1-based symbols (for the financial model, `Y = 1 + 2V + C` in 1..4). Give rational inputs as strings such as `"1/20"` or `"0.05"`; binary floats are rejected. `--max-seconds` sets a time budget; when a budget runs out, the status is `resource-limited`, never `certified`.

## What "certified" means

For each returned prefix the certificate states exact rationals `L <= Lbar` and `Uunder <= U` with

* `L <= inf_{theta in C} F_t(theta) <= Lbar` and `Uunder <= sup_{theta in C} F_t(theta) <= U`;
* status `certified` only if both gaps `Lbar - L` and `U - Uunder` are at most `epsilon`.

As in the paper, three guarantees are kept separate:

1. **Statistical coverage** — the confidence region contains the true weights simultaneously over time with probability at least `1 - alpha`, *if* the model with its fixed, known components is correctly specified.
2. **Numerical certification** — for the declared rational inputs, `[L, U]` encloses the exact posterior range, whatever the statistics. The width `U - L` is the posterior range, not an optimization error; the optimization error is the pair of gaps.
3. **Model correctness** — not addressed: fitted modes, emissions and data processing are taken as given.

## Verification

`python run.py verify FILE` (or `verify_certificate(cert)`) rebuilds the confidence polytope from the raw observations, replays every recorded bisection, recomputes all cell enclosures, and compares every number exactly. By default it also runs checks that do **not** reuse the solver's code path:

* every cell vertex is re-tested against the defining inequalities;
* the total volume of the cells must equal the region volume computed by a different method (interval length for K=2, the shoelace formula for K=3, a pulling triangulation from the opposite apex for K>=4);
* every Bernstein bound is recomputed with the Fraction recurrence and must equal the integer-lift value exactly (the paper's integer-lift invariance).

Use `--no-cross-check` to skip these for speed. The SHA-256 field only detects accidental modification; it is not a signature. Forged numbers are caught by the replay itself, even when the hash has been recomputed.

## Paper-to-code map

| Paper | Module | Notes |
| --- | --- | --- |
| Mixture transition, filter, likelihood (Section 2) | `model.py` | exact normalized filtering, stationary laws, sampling |
| Finite-word posterior equivalence (Proposition 2) | `identifiability.py` | span-based exact test, polynomial in S and b; brute-force reference kept |
| Uniform sensitivity constant `L_phi` (Theorem 1) | `identifiability.py` | rational upper bound |
| Block-frequency region `C_any` (Section 4.1) | `confidence.py` | exact membership test |
| Likelihood-ratio region `C_LR` (Section 4.2) | `confidence.py` | exact membership test |
| Affine-refresh polytope `C_obs` (Section 4.3) | `confidence.py`, `geometry.py` | outward-rounded radii; exact vertices and simplicial cover for any K>=2 |
| Forgetting bound `E_V(m)` (Theorem 12) | `bernstein.py` | regional contraction oracle, rational majorants |
| Bernstein ratio enclosure (Theorem 13) and integer lift (Proposition 16) | `bernstein.py` | integer and Fraction recurrences |
| Global certificate and gaps (Theorem 14, Algorithm 1) | `solver.py` | adaptive longest-edge bisection, honest budget status |
| Certificate replay | `certificate.py` | schemas `hmmcert-v1` and `hmmcert-v2` |

## Example scripts

```bash
python examples/experiment_e1.py           # one path of the rank-deficient model: D_theta, D_q, target width
python examples/experiment_e2.py           # small Monte Carlo of time-simultaneous inclusion, three regions
python examples/experiment_e4_scaling.py   # (S,K,t) scaling incl. K=4, integer vs rational recurrence (2-3 min)
python examples/finance_from_symbols.py examples/observations.json
```

These are small illustrations of each experiment's computation. They do not regenerate the paper's tables, which used larger designs (for example 300 trajectories per model).

## Scope and limitations

Implemented:

* filtering, likelihood, sampling and block-frequency / likelihood-ratio membership for positive HMMs with any finite S, b and K;
* certified global extrema over the affine-refresh confidence polytope for **any K >= 2** (exact vertex enumeration and pulling triangulation for K >= 4), including lower-dimensional, single-point and empty regions;
* exact Bernstein ratio bounds, integer lift, regional contraction and forgetting bounds.

Not implemented:

* global extremum search over curved block-frequency or likelihood-ratio regions (real quantifier elimination / CAD); only membership tests are provided;
* a decision procedure for fiber invariance over a whole polytope; the equivalence test is for a fixed pair of parameters;
* inference for estimated model components.

Cost grows quickly: the number of Bernstein coefficients per cell is `binomial(m + K - 1, K - 1)` for memory window `m`, and vertex enumeration for K >= 4 solves up to `binomial(#constraints, K - 1)` exact linear systems (it returns immediately when the whole simplex is feasible, the common case for short prefixes). Start with small `--max-memory` values when K is large.

## Python API

```python
import json
from hmmcert import AffineRefresh, SolverSettings, solve
from hmmcert.certificate import build_certificate, verify_certificate

model = AffineRefresh.from_dict(json.load(open("examples/rank_deficient.json")))
result = solve(model, [0, 1, 1, 0, 1, 0], SolverSettings(alpha="1/20", epsilon="1/200"))
print(result.status, result.bounds, result.gaps)
print(verify_certificate(build_certificate(model, result)))
```

## Project layout

```text
hiddenma/
├── run.py                   entry point (python run.py demo|certify|verify|inspect)
├── hmmcert/                 package: exact, model, identifiability, confidence,
│                            geometry, bernstein, solver, certificate, data/*.json
├── examples/                model JSON files, example scripts, sample v1 certificate
├── tests/                   pytest suite
├── paper_sources/           LaTeX sources used to build the implementation
├── CITATION.cff             citation metadata
└── FILE_CHECKSUMS.sha256    SHA-256 of every distributed file
```

## Changes in 0.2.0

* Certified optimization for any number of modes K >= 2 (previously K <= 3).
* Span-based finite-word equivalence test: exact and polynomial; the worst case for the financial model drops from about 36 s to milliseconds.
* Per-cell caching of transition matrices: 2–3x faster solves with bit-identical results.
* Verifier cross-checks (vertex feasibility, independent region volume, integer vs rational recurrence); certificate schema `hmmcert-v2`, while v1 certificates still verify.
* CLI: `--paper-indexed`, input validation, `four_mode` demo model, `verify --no-cross-check`.
* New tests (33 in total) and the E4-style scaling example.

## Citation

See `CITATION.cff`. The simulation outputs are cited as: Chen J. *Functional identifiability and certified time-uniform posterior inference in hidden Markov models with transition matrices mixed from known modes* [dataset]. Zenodo; 2026. doi:10.5281/zenodo.24462482.
