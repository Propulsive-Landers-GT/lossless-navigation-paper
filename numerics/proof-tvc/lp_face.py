"""[proof-tvc] Small-angle (LP) level test of the dive-then-brake face for pure TVC, upright at rest.
Scalar/vector tangent-plane tilt B(s), piecewise-constant angular acceleration n=B''.
G(B) = int_E (s*-s)[al1 B^2 + eps B'^2] - int_L (s-s*)[al2 B^2 + eps B'^2 + gam B''^2]
Witness: max G over |n|<=K1 (early), |n|<=K2 (late), rest-to-rest  (scalar, planar).
Bound for zero-lateral competitors: S-procedure  sup G <= min int lam K^2  s.t. G - int lam n^2 <= 0 on
{rest-to-rest, int f0 B = 0, int s f0 B = 0}  (vector case reduces to scalar: separable).
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np, cvxpy as cp, sys

def gtpl():
    m=79.88; return dict(a1=400/m, a2=1000/m, de=np.deg2rad(15), eps=63.6/(m*0.589), g0=9.80665)

def build(P, tf, ss, N=120, sub=6):
    h=tf/N; a1,a2,de,eps=P['a1'],P['a2'],P['de'],P['eps']
    K1=a1*np.sin(de)/eps; K2=a2*np.sin(de)/eps
    # fine grid
    M=N*sub; t=np.linspace(0,tf,M+1); hh=tf/M
    k_of=np.minimum((t[:-1]+hh/2)//h, N-1).astype(int)
    # B, V on fine grid as linear maps of n
    Bm=np.zeros((M+1,N)); Vm=np.zeros((M+1,N))
    for j in range(M):
        k=k_of[j]; Vm[j+1]=Vm[j]; Vm[j+1,k]+=hh
        Bm[j+1]=Bm[j]+Vm[j]*hh; Bm[j+1,k]+=hh*hh/2
    # Simpson weights
    wq=np.ones(M+1); wq[1:-1:2]=4; wq[2:-1:2]=2; wq*=hh/3
    early=(t<=ss); w=t-ss
    al1=a1*np.cos(de)/2; al2=a2/2; gam=eps**2/(2*a2)
    WB=np.where(early,-w*al1,-w*al2)*wq     # early: (s*-s)al1 ; late: -(s-s*)al2
    WV=np.where(early,-w*eps,-w*eps)*wq
    G=Bm.T@(WB[:,None]*Bm)+Vm.T@(WV[:,None]*Vm)
    tc=(np.arange(N)+0.5)*h
    lateN=tc>ss
    # gamma term (piecewise const n): int_L (s-s*) gam n^2
    wn=np.array([max(0,((min(tf,(k+1)*h)-ss)**2-max(0,k*h-ss)**2)/2) if (k+1)*h>ss else 0 for k in range(N)])
    G-=np.diag(gam*wn)
    G=(G+G.T)/2
    Kv=np.where(lateN,K2,K1)
    rest=np.vstack([Bm[-1],Vm[-1]])
    f0=np.where(early,a1*np.cos(de),a2)
    mom=np.vstack([(f0*wq)@Bm,(t*f0*wq)@Bm])
    return dict(G=G,Kv=Kv,rest=rest,mom=mom,h=h,N=N,tc=tc,Bm=Bm,t=t,wq=wq,f0=f0)

def witness(D, starts=12, seed=0):
    import casadi as ca
    G,Kv,rest,N=D['G'],D['Kv'],D['rest'],D['N']
    best=None; rng=np.random.default_rng(seed)
    for st in range(starts):
        o=ca.Opti(); n=o.variable(N)
        o.subject_to(o.bounded(-Kv,n,Kv)); o.subject_to(ca.mtimes(ca.DM(rest),n)==0)
        o.minimize(-ca.mtimes([n.T,ca.DM(G),n]))
        o.set_initial(n,rng.uniform(-1,1,N)*Kv)
        o.solver('ipopt',{'ipopt.print_level':0,'print_time':0,'ipopt.sb':'yes','ipopt.max_iter':3000})
        try: s=o.solve(); v=-float(s.value(o.f)); nv=np.array(s.value(n)).ravel()
        except RuntimeError: continue
        if best is None or v>best[0]: best=(v,nv)
    return best

def dual(D, with_mom=True, pieces=None):
    G,Kv,h,N=D['G'],D['Kv'],D['h'],D['N']
    A=np.vstack([D['rest'],D['mom']]) if with_mom else D['rest']
    # null space basis
    u,s,vt=np.linalg.svd(A); Z=vt[np.sum(s>1e-12*s[0]):].T
    lam=cp.Variable(N,nonneg=True)
    Mx=Z.T@G@Z - Z.T@cp.diag(lam*h)@Z
    prob=cp.Problem(cp.Minimize(cp.sum(cp.multiply(lam*h,Kv**2))),[ (Mx+Mx.T)/2 << 0])
    prob.solve(solver='CLARABEL')
    return prob.value, lam.value

if __name__=="__main__":
    P=gtpl()
    for tf in [float(x) for x in sys.argv[1:]] or [1.0,2.0]:
        for frac in [0.25,0.35,0.5]:
            ss=frac*tf
            D=build(P,tf,ss)
            w=witness(D); dm=dual(D,True)[0]; df=dual(D,False)[0]
            print(f"tf={tf} s*={ss:.2f}: witness(planar Linf)={w[0]:.4e}  dual(no mom)={df:.4e}  dual(zero-lat)={dm:.4e}  ratio={dm/w[0]:.3f}",flush=True)
