"""Is the exact vertical 1D set K={(int a, int (tf-s) a)} with a=T/m, mdot=-alpha T convex? (3DOF w/ mass, d=e_z)
mu=m/m0, mu(0)=1, mudot in [-c2,-c1] (c_i=alpha rho_i/m0). alpha*I=-ln mu(tf), alpha*J=-int ln mu.
For fixed mu(tf), J ranges over [Jmin,Jmax] attained by the pointwise envelopes of W. K convex iff Jmax concave & Jmin convex in I."""
import numpy as np
def curves(c1,c2,tf,n=20001,nf=801):
    s=np.linspace(0,tf,n)
    out=[]
    for muf in np.linspace(1-c2*tf,1-c1*tf,nf):
        lo=np.maximum(1-c2*s, muf+c1*(tf-s)); hi=np.minimum(1-c1*s, muf+c2*(tf-s))
        out.append((-np.log(muf),np.trapezoid(-np.log(hi),s),np.trapezoid(-np.log(lo),s)))
    o=np.array(out); return o[np.argsort(o[:,0])]
for (c1,c2,tf) in [(0.024,0.06,10),(0.02,0.08,10),(0.003,0.007,10),(2.8e-3,7.1e-3,10)]:
    x,jmin,jmax=curves(c1,c2,tf).T
    d2max=np.diff(jmax,2); d2min=np.diff(jmin,2)
    print(f"c1={c1} c2={c2}: Jmax 2nd-diff max={d2max.max():.2e} (concave iff <=0); Jmin 2nd-diff min={d2min.min():.2e} (convex iff >=0)")
    k=np.argmax(d2max); print("   worst Jmax convexity at x=",x[k+1])

print("--- extreme burn cases (predicted: Jmin loses convexity when mu(s**)/mu_f > e roughly)")
for (c1,c2,tf) in [(0.01,0.098,10),(0.001,0.099,10),(0.05,0.0995,10)]:
    x,jmin,jmax=curves(c1,c2,tf,n=40001,nf=1601).T
    d2min=np.diff(jmin,2)
    k=np.argmin(d2min)
    print(f"c1={c1} c2={c2}: Jmin min 2nd diff={d2min.min():.3e} at x={x[k+1]:.3f}; Jmax max 2nd diff={np.diff(jmax,2).max():.3e}")
