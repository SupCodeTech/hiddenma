"""Small E4-style scaling run: certification cost as (S, K, t) grow jointly.

Each stratum draws random strictly positive rational affine-refresh models,
simulates a prefix, certifies it, and then re-evaluates the final cell cover
with the Fraction recurrence to report the paired rational/integer time ratio.
This illustrates the computation reported in the paper's experiment E4; it is
NOT a replication of its 30-trajectory strata or its timings.

Run:  python examples/experiment_e4_scaling.py            (about 2-3 minutes)
      python examples/experiment_e4_scaling.py --reps 3 --strata 3,3,200 5,4,500 6,5,500
"""
from __future__ import annotations
import argparse
import sys
import time
from fractions import Fraction as F
from pathlib import Path
from random import Random
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from hmmcert import AffineRefresh, SolverSettings, solve
from hmmcert.bernstein import cell_enclosure


def _simplex_point(rng, n, denominator=40):
    """Strictly positive rational probability vector with the given denominator."""
    cuts = sorted(rng.sample(range(1, denominator), n-1))
    parts = [b-a for a, b in zip([0]+cuts, cuts+[denominator])]
    return tuple(F(p, denominator) for p in parts)


def random_model(rng, S, K, b=2):
    return AffineRefresh(F(1, 2), tuple(_simplex_point(rng, S) for _ in range(S)),
                         tuple(_simplex_point(rng, S) for _ in range(K)),
                         tuple(_simplex_point(rng, b) for _ in range(S)),
                         _simplex_point(rng, S), tuple(F(int(i == S-1)) for i in range(S)))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--strata", nargs="+", default=["3,3,200", "4,4,300", "5,4,300"],
                    help="S,K,t triples")
    ap.add_argument("--reps", type=int, default=2)
    ap.add_argument("--memory", type=int, default=12)
    ap.add_argument("--max-cells", type=int, default=120)
    ap.add_argument("--epsilon", default="1/50")
    ap.add_argument("--seed", type=int, default=20261123)
    args = ap.parse_args(argv)
    print("S,K,t,rep,status,cells,gap_lower,gap_upper,solve_s,integer_cells_s,rational_cells_s,rational_over_integer")
    for stratum in args.strata:
        S, K, t = (int(v) for v in stratum.split(","))
        for rep in range(args.reps):
            rng = Random(args.seed + 1000*S + 100*K + rep)
            model = random_model(rng, S, K)
            obs, _ = model.hmm().sample(_simplex_point(rng, K), t, seed=rng.randrange(10**9))
            settings = SolverSettings(epsilon=args.epsilon, max_memory=args.memory, max_cells=args.max_cells)
            t0 = time.perf_counter()
            result = solve(model, obs, settings)
            t_int = time.perf_counter()-t0
            hmm = model.hmm()
            t0 = time.perf_counter()
            for cell in result.cells:
                cell_enclosure(hmm, cell, obs, args.memory, arithmetic="rational")
            t_rat = time.perf_counter()-t0
            t0 = time.perf_counter()
            for cell in result.cells:
                cell_enclosure(hmm, cell, obs, args.memory)
            t_int_cells = time.perf_counter()-t0
            gaps = ("NA", "NA") if result.gaps is None else tuple(f"{float(g):.5f}" for g in result.gaps)
            ratio = t_rat/t_int_cells if t_int_cells > 0 else float("nan")
            print(f"{S},{K},{t},{rep},{result.status},{len(result.cells)},{gaps[0]},{gaps[1]},"
                  f"{t_int:.3f},{t_int_cells:.3f},{t_rat:.3f},{ratio:.2f}")


if __name__ == "__main__":
    main()
