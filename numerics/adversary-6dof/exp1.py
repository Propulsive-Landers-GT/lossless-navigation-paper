import numpy as np, sys
from m3tvc import *
P = gtpl()
pats = {
 "const": lambda s,r: 1.0,
 "half": lambda s,r: 1.0 if s<0.5 else -1.0,
 "quarter": lambda s,r: 1.0 if (s<0.25 or s>0.75) else -1.0,
 "chatter": lambda s,r: (1.0 if int(s*60)%2==0 else -1.0),
 "rand": None,
}
def run(tf, N, term, gimbal="cone", rate=False, roll=True, nstart=3, dec=None):
    R = Reach6(P, tf, N, gimbal=gimbal, rate_limited=rate, terminal_att=term, roll=roll,
               decoupled=dec is not None, tau_dec=dec)
    rng = np.random.default_rng(0)
    best=None; out=[]
    axis = np.array([1.0,1.0])/np.sqrt(2) if gimbal=="box" else None
    for name,p in pats.items():
        for i in range(nstart if p is None else 1):
            R.init(rng, p, axis=None if (p is None or axis is None) else axis*np.sqrt(2) if gimbal=="box" else None)
            r = R.solve()
            out.append((name, r["ok"], r["vN"][2], np.hypot(*r["vN"][:2])))
            if r["ok"] and (best is None or r["vN"][2] < best["vN"][2]): best=r
    lat=[]
    for name,p in pats.items():
        for i in range(nstart if p is None else 1):
            R.init(rng, p)
            r = R.solve(lat=[0,0])
            lat.append((name, r["ok"], r["vN"][2]))
    okl=[l for l in lat if l[1]]
    V0 = min(l[2] for l in okl) if okl else np.nan
    return best, out, V0, lat
if __name__=="__main__":
    tf=float(sys.argv[1]); N=int(sys.argv[2]); term={"0":False,"1":True,"r":"rate"}[sys.argv[3]]
    gim = sys.argv[4] if len(sys.argv)>4 else "cone"
    rate = (sys.argv[5]=="1") if len(sys.argv)>5 else False
    best,out,V0,lat = run(tf,N,term,gim,rate)
    for o in out: print("free ", o)
    for l in lat: print("lat0 ", l)
    Vm=best["vN"][2]; L=np.hypot(*best["vN"][:2])
    print(f"tf={tf} N={N} term={term} gim={gim} rate={rate}: Vmin={Vm:.6f} lat@min={L:.6f}  Vmin(lat=0)={V0:.6f}  gap={V0-Vm:.3e}  maxtilt={tilt(best['X']).max():.2f}deg")
    np.save(f"best_{tf}_{N}_{int(term)}_{gim}_{int(rate)}.npy", dict(X=best["X"],U=best["U"]), allow_pickle=True)
