"""[adversary-6dof] Small-tf limit problems (tf=1, K=1), flat tangent-plane coordinates B in R^2.
LP1 pure TVC, attitude free at tf : max  int <n,B>,   B''=-n, |n|<=1, B(0)=B'(0)=0
LP2 pure TVC, rest-to-rest attitude: LP1 + B(1)=B'(1)=0
LP3 decoupled torque, rest-to-rest  : max int |B|, |B''|<=1, B(0)=B'(0)=B(1)=B'(1)=0   (no spin)
Reports optimum, int n, int B, planarity.  Exact integration of piecewise-constant n (double integrator)."""
import numpy as np, casadi as ca, sys
def solve(lp, N=200, starts=30, seed=1):
    rng=np.random.default_rng(seed); h=1.0/N
    res=[]
    for st in range(starts):
        o=ca.Opti(); n=o.variable(2,N)
        o.subject_to(ca.sum1(n**2)<= 1)
        B=[ca.DM.zeros(2)]; V=[ca.DM.zeros(2)]; J=0; intB=0
        for k in range(N):
            a=-n[:,k]
            Bk,Vk=B[-1],V[-1]
            # integrals over the interval of B(t) = Bk + Vk t + a t^2/2
            IB = Bk*h + Vk*h**2/2 + a*h**3/6
            if lp in (1,2): J += ca.dot(n[:,k], IB)
            else:
                Bm = Bk + Vk*h/2 + a*h**2/8
                J += h*ca.sqrt(ca.sumsqr(Bm)+1e-12)
            intB += IB
            B.append(Bk+Vk*h+a*h**2/2); V.append(Vk+a*h)
        if lp in (2,3):
            o.subject_to(B[-1]==0); o.subject_to(V[-1]==0)
        o.minimize(-J)
        th=rng.uniform(0,2*np.pi,N)*(rng.random()<0.5) + rng.uniform(0,2*np.pi)
        init=np.vstack([np.cos(th),np.sin(th)])*rng.uniform(0.3,1,N)
        if st%3==0:  # planar random sign pattern
            sg=np.sign(rng.normal(size=N)); init=np.vstack([sg,0*sg])
        o.set_initial(n,init)
        o.solver("ipopt",{"ipopt.print_level":0,"print_time":0,"ipopt.sb":"yes","ipopt.max_iter":3000})
        try: s=o.solve()
        except RuntimeError: continue
        nv=np.array(s.value(n)); Jv=float(s.value(J)); iB=np.array(s.value(intB)).ravel()
        # planarity: singular values of n
        sv=np.linalg.svd(nv,compute_uv=False)
        res.append((Jv, nv.sum(1)*h, iB, sv[1]/sv[0], nv))
    res.sort(key=lambda r:-r[0])
    return res
if __name__=="__main__":
    for lp in (1,2,3):
        r=solve(lp)
        print(f"LP{lp}: best J={r[0][0]:.6f}  int n={r[0][1]}  |int B|={np.linalg.norm(r[0][2]):.6f}  nonplanarity={r[0][3]:.2e}")
        print("   top-5 J:", [round(x[0],6) for x in r[:5]])
        nv=r[0][4]; ang=np.unwrap(np.arctan2(nv[1],nv[0])); mag=np.linalg.norm(nv,axis=0)
        idx=np.linspace(0,nv.shape[1]-1,9).astype(int)
        print("   |n| samples", np.round(mag[idx],3), " dir(deg)", np.round(np.degrees(ang[idx]-ang[0]),1))
        np.save(f"lp{lp}.npy", r[0][4])
