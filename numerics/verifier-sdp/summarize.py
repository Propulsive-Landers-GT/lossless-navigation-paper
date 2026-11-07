"""[verifier-sdp] Summaries (markdown) of all result files."""
import os, json, glob, collections
import numpy as np

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")


def load(p):
    try:
        return [json.loads(l) for l in open(p)]
    except FileNotFoundError:
        return []


def fixed():
    print("## Fixed thrust (delta=0) sweep: run_fixed.py\n")
    print("| file | N | targets | Clarabel status | nongenuine (perp>1e-5) | max (U-L)/scale^2 | min (U-L)/scale^2 | max rel gap where (U-L)/scale^2>1e-8 | SCS-Clarabel max |diff|/scale^2 |")
    print("|---|---|---|---|---|---|---|---|---|")
    for f in sorted(glob.glob(os.path.join(D, "fixed_*.jsonl"))):
        R = load(f)
        if not R:
            continue
        for N in sorted(set(r["N"] for r in R)):
            Rn = [r for r in R if r["N"] == N]
            st = collections.Counter(r["st_clar"] for r in Rn)
            rels = [r["relgap"] for r in Rn if r["absgap"] > 1e-8]
            ds = [abs(r["sdp_scs"] - r["sdp_clar"]) / r["scale2"] for r in Rn if r["sdp_scs"] == r["sdp_scs"]]
            print(f"| {os.path.basename(f)} | {N} | {len(Rn)} | {dict(st)} | {sum(r['perp_sum'] > 1e-5 for r in Rn)} | "
                  f"{max(r['absgap'] for r in Rn):.1e} | {min(r['absgap'] for r in Rn):.1e} | {max(rels) if rels else 0:.1e} | "
                  f"{max(ds) if ds else float('nan'):.1e} |")
    R = sum((load(f) for f in glob.glob(os.path.join(D, "fixed_*.jsonl"))), [])
    print(f"\nTotal fixed-thrust targets: {len(R)}; by label:")
    c = collections.defaultdict(list)
    for r in R:
        c[r["label"].split(" perp")[0]].append(r)
    print("\n| target family | n | max (U-L)/scale^2 | share rank>3 |")
    print("|---|---|---|---|")
    for k, v in sorted(c.items()):
        print(f"| {k} | {len(v)} | {max(r['absgap'] for r in v):.1e} | {np.mean([r['perp_sum'] > 1e-5 for r in v]):.2f} |")
    print("\nSlater margin min:", min(r["slater"] for r in R))


def adv():
    R = load(os.path.join(D, "adv_proofsdp.jsonl"))
    if R:
        print("\n## [proof-sdp] regimes (a),(b), delta=0\n")
        for part in ("a", "b"):
            Rp = [r for r in R if r["part"] == part]
            print(f"- part {part}: {len(Rp)} instances, N={sorted(set(r['N'] for r in Rp))}, max rel gap {max(r['relgap'] for r in Rp):.2e}, "
                  f"min {min(r['relgap'] for r in Rp):.2e}, rank>3 in {sum(r['rank'] > 3 for r in Rp)}")


def gim():
    R = [r for r in load(os.path.join(D, "gim.jsonl")) if r.get("part") == "screen"]
    if not R:
        return
    print("\n## Gimbal screen (unit-d inner discretization, both cones) vs delta=0: run_gim.py\n")
    print("| N | delta | omega*tf | checked (SDP non-genuine or 10-15% spot) | gaps (rel>1e-5, abs>1e-9) | max rel gap |")
    print("|---|---|---|---|---|---|")
    keys = sorted(set((r["N"], r["deg"] if r["deg"] is not None else 0.0, r["wtf"]) for r in R))
    for N, deg, wtf in keys:
        Rk = [r for r in R if r["N"] == N and (r["deg"] or 0.0) == deg and r["wtf"] == wtf]
        g = [r for r in Rk if r["rel"] > 1e-5 and r["absn"] > 1e-9]
        print(f"| {N} | {deg:g} | {wtf:.2f} | {len(Rk)} | {len(g)} | {max([r['rel'] for r in g] + [0]):.2f} |")


def cvx():
    R = load(os.path.join(D, "cvx_check.jsonl"))
    if R:
        print(f"\n## Convexified lens on every unit-d gap instance: {len(R)} instances, "
              f"max (U-L)/scale^2 = {max(r['absn'] for r in R):.1e}, statuses {dict(collections.Counter(r['st'] for r in R))}")


def csd2p():
    R = sum((load(f) for f in glob.glob(os.path.join(D, "csd2p_*.jsonl"))), [])
    if not R:
        return
    print("\n## CSD2' screen (d=b and convexified lens): run_csd2p.py\n")
    print("| N | model | checked | gaps (rel>1e-4, abs>1e-8) | max (U-L)/scale^2 |")
    print("|---|---|---|---|---|")
    for N in sorted(set(r["N"] for r in R)):
        for m in ("d=b", "cvx15", "cvx40"):
            Rk = [r for r in R if r["N"] == N and r["model"] == m]
            if Rk:
                g = [r for r in Rk if r["absn"] > 1e-8 and r["rel"] > 1e-4]
                print(f"| {N} | {m} | {len(Rk)} | {len(g)} | {max(r['absn'] for r in Rk):.1e} |")


if __name__ == "__main__":
    fixed(); adv(); gim(); cvx(); csd2p()
