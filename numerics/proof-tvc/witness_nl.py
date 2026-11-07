"""[proof-tvc] Exact (nonlinear) planar witness for the dive-then-brake face, pure TVC, upright at rest.
Planar meridian psi(s): eps*psi'' = -q (TVC torque), control n = psi'' piecewise constant.
Early [0,s*]: T = rho1, gimbal at full angle delta in the plane: p = a1 cos(delta), |q| = a1 sin(delta) => |n| <= K1
   (if |n| < K1 the remaining deflection is wasted by chattering; relaxed-admissible, ordinary if |n| = K1).
Late (s*,tf]: T = rho2, gimbal angle mu with a2 sin(mu) = eps|n|: p = sqrt(a2^2 - eps^2 n^2), |n| <= K2.
f = p - eps psi'^2 (centre-of-percussion thrust), W_z = int (s-s*) f cos(psi) ds, gain G = W_z - J0.
Also returns r(t) (physical) for the altitude / glide-slope check and the lateral data r0h, v0h.
"""
import os
os.environ.setdefault("OMP_NUM_THREADS","1")
import numpy as np, casadi as ca

def gtpl(m=79.88, rho1=400., rho2=1000., Jt=63.6, L=0.589, deg=15.):
    return dict(m=m,a1=rho1/m,a2=rho2/m,de=np.deg2rad(deg),eps=Jt/(m*L),g0=9.80665,Jt=Jt,L=L,rho1=rho1,rho2=rho2)

def J0(P,tf,ss):
    return -P['a1']*np.cos(P['de'])*ss**2/2 + P['a2']*(tf-ss)**2/2

def optimize(P,tf,ss,N=200,starts=8,seed=0,cap=None):
    a1,a2,de,eps=P['a1'],P['a2'],P['de'],P['eps']; K1=a1*np.sin(de)/eps; K2=a2*np.sin(de)/eps
    h=tf/N; tc=(np.arange(N)+.5)*h; early=tc<ss
    sub=8; best=None; rng=np.random.default_rng(seed)
    for st in range(starts):
        o=ca.Opti(); n=o.variable(N)
        psi=0; om=0; W=0
        for k in range(N):
            hh=h/sub
            for j in range(sub):
                s=k*h+(j+.5)*hh
                pm=psi+om*hh/2+n[k]*hh**2/8; omm=om+n[k]*hh/2
                if early[k]: p=a1*np.cos(de)
                else: p=ca.sqrt(a2**2-eps**2*n[k]**2)
                W+=hh*(s-ss)*(p-eps*omm**2)*ca.cos(pm)
                psi=psi+om*hh+n[k]*hh**2/2; om=om+n[k]*hh
                if cap is not None and j==sub-1: o.subject_to(o.bounded(-cap,psi,cap))
        o.subject_to(psi==0); o.subject_to(om==0)
        o.subject_to(o.bounded(-np.where(early,K1,K2*0.999),n,np.where(early,K1,K2*0.999)))
        o.minimize(-W)
        o.set_initial(n,rng.uniform(-1,1,N)*np.where(early,K1,K2)*0.5)
        o.solver('ipopt',{'ipopt.print_level':0,'print_time':0,'ipopt.sb':'yes','ipopt.max_iter':3000})
        try: sol=o.solve()
        except RuntimeError: continue
        v=float(sol.value(W)); nv=np.array(sol.value(n)).ravel()
        if best is None or v>best[0]: best=(v,nv)
    return best

def evaluate(P,tf,ss,nv,M=40000):
    """High-resolution exact evaluation of a piecewise-constant n profile (midpoint rule on M sub-steps,
    psi integrated exactly). Returns gain, lateral data, altitude margins."""
    a1,a2,de,eps,g0=P['a1'],P['a2'],P['de'],P['eps'],P['g0']
    N=len(nv); h=tf/N; t=np.linspace(0,tf,M+1); dt=tf/M
    k=np.minimum((t[:-1]+dt/2)//h,N-1).astype(int); nn=nv[k]
    psi=np.zeros(M+1); om=np.zeros(M+1)
    for j in range(M):
        psi[j+1]=psi[j]+om[j]*dt+nn[j]*dt**2/2; om[j+1]=om[j]+nn[j]*dt
    tm=t[:-1]+dt/2; pm=psi[:-1]+om[:-1]*dt/2+nn*dt**2/8; omm=om[:-1]+nn*dt/2
    p=np.where(tm<ss,a1*np.cos(de),np.sqrt(np.maximum(a2**2-eps**2*nn**2,0)))
    f=p-eps*omm**2
    W=np.sum(dt*(tm-ss)*f*np.cos(pm))
    G=W-J0(P,tf,ss)
    # y-accel (vertical/lateral), physical position via y: r = y - eps b
    az=f*np.cos(pm)-g0; ax=f*np.sin(pm)
    # integrate backwards from y(tf) = eps e_z, ydot(tf)=0
    vz=np.zeros(M+1); vx=np.zeros(M+1); yz=np.zeros(M+1); yx=np.zeros(M+1); yz[-1]=eps
    for j in range(M-1,-1,-1):
        vz[j]=vz[j+1]-az[j]*dt; vx[j]=vx[j+1]-ax[j]*dt
        yz[j]=yz[j+1]-(vz[j]+vz[j+1])/2*dt; yx[j]=yx[j+1]-(vx[j]+vx[j+1])/2*dt
    rz=yz-eps*np.cos(psi); rx=yx-eps*np.sin(psi)
    v0=np.array([vx[0],vz[0]]); r0=np.array([rx[0],rz[0]])   # v0 = ydot(0) since bdot(0)=0
    rh=np.abs(rx); 
    return dict(G=G,W=W,v0=v0,r0=r0,minrz=rz[:-1].min(),maxvz=vz[:-1].max(),rzrel=np.min(rz[:-1]/(np.abs(rx[:-1])+1e-300)),glide=np.min(rz[:-1]-np.abs(rx[:-1])*np.tan(np.deg2rad(30))),
                maxtilt=np.abs(psi).max(),latmom=(np.sum(dt*f*np.sin(pm)),np.sum(dt*tm*f*np.sin(pm))))

if __name__=="__main__":
    import sys
    P=gtpl()
    for tf,ss in [(1.0,0.25),(1.5,0.4),(2.0,0.5)]:
        b=optimize(P,tf,ss,N=100,starts=6)
        ev=evaluate(P,tf,ss,b[1])
        print(f"tf={tf} s*={ss}: G_w={ev['G']:.4e}  maxtilt={np.degrees(ev['maxtilt']):.2f}deg  min r_z={ev['minrz']:.3f} m  glide30 margin={ev['glide']:.3f}  v0={ev['v0']} r0={ev['r0']} lat moments={ev['latmom']}",flush=True)
        np.save(f"witness_{tf}_{ss}.npy",b[1])

def segments_bangbang(P, tf, ss, nv, tol=1e-12):
    """Ordinary-control realization (fix of [adversary-6dof] finding (1)): every early cell with |n| < K1 is
    flown as exact full-deflection bang-bang (+K1, -K1, +K1) (or the mirror) with switch times
    a = (h-d)/2, b = (h+d)/2, d = h(1-|m|)/2, m = n/K1, which reproduces the cell-end (psi, psi') exactly.
    Returns a list of segments (t0, dt, n, early_flag)."""
    a1, de, eps = P['a1'], P['de'], P['eps']; K1 = a1*np.sin(de)/eps
    N = len(nv); h = tf/N; segs = []
    for k in range(N):
        t0 = k*h; early = (t0 + h/2) < ss
        n = nv[k]
        if early and abs(n) < K1*(1-tol):
            m = n/K1; sg = 1.0 if m >= 0 else -1.0; mm = abs(m)
            d = h*(1-mm)/2; a = (h-d)/2
            segs += [(t0, a, sg*K1, True), (t0+a, d, -sg*K1, True), (t0+a+d, h-a-d, sg*K1, True)]
        else:
            segs.append((t0, h, float(np.clip(n, -K1, K1)) if early else n, early))
    return segs

def evaluate_segments(P, tf, ss, segs, sub_per_unit=40000):
    """Exact closed-form psi on each constant-n segment; midpoint quadrature (sub-steps ~ 1/sub_per_unit s).
    Early segments: p = a1 cos(delta) (full deflection, |n| = K1 required); late: p = sqrt(a2^2 - eps^2 n^2)."""
    a1, a2, de, eps, g0 = P['a1'], P['a2'], P['de'], P['eps'], P['g0']; K1 = a1*np.sin(de)/eps
    psi = 0.0; om = 0.0; W = 0.0; T = []; AZ = []; AX = []; PS = []; DT = []
    for (t0, dt, n, early) in segs:
        if dt <= 0: continue
        if early: assert abs(abs(n) - K1) < 1e-9*K1, "early segment not at full deflection"
        p = a1*np.cos(de) if early else np.sqrt(max(a2**2 - eps**2*n**2, 0.0))
        M = max(4, int(np.ceil(dt*sub_per_unit))); h = dt/M
        tau = (np.arange(M)+0.5)*h
        ps = psi + om*tau + n*tau**2/2; omm = om + n*tau
        f = p - eps*omm**2
        W += np.sum(h*(t0+tau-ss)*f*np.cos(ps))
        T.append(t0+tau); AZ.append(f*np.cos(ps)-g0); AX.append(f*np.sin(ps)); PS.append(ps); DT.append(np.full(M, h))
        psi = psi + om*dt + n*dt**2/2; om = om + n*dt
    T = np.concatenate(T); AZ = np.concatenate(AZ); AX = np.concatenate(AX); PS = np.concatenate(PS); DT = np.concatenate(DT)
    # landing data from y: ydot(0) = g0 tf e_z - int f b  (+ lateral), r0 = int s f b - g0 tf^2/2
    v0 = np.array([-np.sum(DT*AX), -np.sum(DT*AZ)])
    r0 = np.array([np.sum(DT*T*AX), np.sum(DT*T*(AZ+g0)) - g0*tf**2/2])
    # v_z(t) = v0z + int_0^t az  (y-velocity; r_z>0 on [0,tf) follows from v_z<0, see math/06 §3)
    vz = v0[1] + np.cumsum(DT*AZ)
    return dict(G=W - J0(P, tf, ss), end=(psi, om), v0=v0, r0=r0, maxvz=vz[:-1].max(), maxtilt=np.abs(PS).max())
