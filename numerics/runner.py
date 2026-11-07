"""Parallel multistart helpers.  A 'spec' is (model_name, P_dict, kwargs_dict); NLPs are cached per process."""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import numpy as np
from concurrent.futures import ProcessPoolExecutor
import models

_CACHE = {}


def _key(spec):
    name, P, kw = spec
    return repr((name, sorted((k, (float(v) if isinstance(v, (int, float, np.floating)) else str(v)))
                              for k, v in P.items()), sorted((k, repr(v)) for k, v in kw.items())))


def get_nlp(spec):
    k = _key(spec)
    if k not in _CACHE:
        name, P, kw = spec
        cls = {"M1": models.ReachM1, "M1A": models.ReachM1A, "M3": models.ReachM3, "MT": models.ReachTilt}[name]
        # silence ipopt banner
        _CACHE[k] = cls(P, **kw)
    return _CACHE[k]


def task(args):
    spec, seed, nstart, solve_kw = args
    devnull = os.open(os.devnull, os.O_WRONLY); old = os.dup(1); os.dup2(devnull, 1)
    try:
        R = get_nlp(spec)
        rng = np.random.default_rng(seed)
        best, allr = R.multistart(nstart, rng, **solve_kw)
    finally:
        os.dup2(old, 1); os.close(devnull); os.close(old)
    if best is None:
        return dict(f=np.inf, z=None, x=None, nok=0, fs=[])
    return dict(f=best["f"], z=best["z"], x=best["x"], nok=len(allr), fs=sorted(r["f"] for r in allr))


_POOL = None


def pool():
    """Compute budget (comms/PROTOCOL.md): <= 2 workers by default; override with NUMERICS_WORKERS."""
    global _POOL
    if _POOL is None:
        _POOL = ProcessPoolExecutor(max_workers=int(os.environ.get("NUMERICS_WORKERS", "2")))
    return _POOL


def run_stream(jobs, nstarts):
    """Yield (j, result) as each job (spec, solve_kw) finishes; nstarts: int or list (one task per job)."""
    from concurrent.futures import as_completed
    if isinstance(nstarts, int):
        nstarts = [nstarts] * len(jobs)
    futs = {pool().submit(task, (spec, 1000 * j, ns, kw)): j for j, ((spec, kw), ns) in enumerate(zip(jobs, nstarts))}
    for f in as_completed(futs):
        yield futs[f], f.result()


def run_many(spec, solve_kw, nstart_total, chunk=10, seed0=0):
    """multistart split across processes; returns best dict plus all local optima values."""
    nchunks = max(1, nstart_total // chunk)
    args = [(spec, seed0 + i, chunk, solve_kw) for i in range(nchunks)]
    res = list(pool().map(task, args))
    best = min(res, key=lambda r: r["f"])
    fs = sorted(sum([r["fs"] for r in res], []))
    return dict(f=best["f"], z=best["z"], x=best["x"], nok=sum(r["nok"] for r in res), fs=fs)


def run_batch(jobs, nstart, chunk=None):
    """jobs: list of (spec, solve_kw). Each job gets nstart restarts (single chunk unless chunk set)."""
    chunk = chunk or nstart
    args = []
    for j, (spec, kw) in enumerate(jobs):
        for i in range(max(1, nstart // chunk)):
            args.append((spec, 1000 * j + i, chunk, kw))
    out = list(pool().map(task, args))
    res = []
    per = max(1, nstart // chunk)
    for j in range(len(jobs)):
        rr = out[j * per:(j + 1) * per]
        b = min(rr, key=lambda r: r["f"])
        res.append(dict(f=b["f"], z=b["z"], x=b["x"], nok=sum(r["nok"] for r in rr),
                        fs=sorted(sum([r["fs"] for r in rr], []))))
    return res
