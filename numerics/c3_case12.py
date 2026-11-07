"""Heavy multistart on CSD2 case 12 (SDP rank 4, NLP > SDP by 2.5%)."""
import numpy as np, json
import models
from runner import run_many
from c1_csd2_check import make_cases
if __name__ == "__main__":
    cases, a = make_cases(); c = cases[12]
    for N in [c["N"]]:
        P = models.gtpl(rho1=a, rho2=a, m0=1.0, alpha=0.0, omega=c["om"])
        spec = ("M1", P, dict(tf=c["tf"], N=N, planar=False, use_r=True, tent=True))
        tgt = np.concatenate([c["wv_m"], c["wr_m"]])
        best = None
        for p_con in [0.0, 0.35, 0.8]:
            models.ReachM1.p_coning = p_con
            r = run_many(spec, dict(mode="dist", target=tgt), 160, chunk=20, seed0=int(100 * p_con) + 7)
            fs = np.array(r["fs"])
            print(f"p_coning={p_con}: best={r['f']:.6f}  n_ok={r['nok']}  quantiles={np.round(np.quantile(fs, [0, .05, .25, .5]), 6)}", flush=True)
        print("SDP = 0.027532", flush=True)
