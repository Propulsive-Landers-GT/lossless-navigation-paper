"""Proof-agent sanity checks for math/02: ball bound, explicit gap, tent gap Q(beta)."""
import numpy as np
rng = np.random.default_rng(0)

def a1_fun(s, rho1, m0, alpha):
    return rho1/(m0 - alpha*rho1*s)

def G(tau, tf, w, dl, rho1, m0, alpha, n=4001):
    s = np.linspace(0, tf, n); return np.trapezoid(a1_fun(s,rho1,m0,alpha)*np.cos(dl+w*np.abs(s-tau)), s)

def Mz_free(tf, w, dl, rho1, m0, alpha, n=4001):
    s = np.linspace(0, tf, n); return np.trapezoid(a1_fun(s,rho1,m0,alpha)*np.cos(dl+w*s), s)

def Gamma_free(tf, w, dl, rho1, m0, alpha):
    return 4*a1_fun(tf/4,rho1,m0,alpha)/w*np.sin(dl+w*tf/2)*np.sin(w*tf/4)**2

def random_traj(tf, w, dl, rho1, rho2, m0, alpha, N=400):
    """Random admissible discretized M1 trajectory (b(0)=e_z free end); returns I = int a d."""
    h = tf/N
    b = np.array([0,0,1.0]); I = np.zeros(3); m = m0
    # random smooth-ish rotation: angular velocity perp to b with |.|<=w
    for k in range(N):
        T = rng.uniform(rho1, rho2) if rng.random()<0.5 else rho1
        # random d in cone(b,dl)
        v = rng.normal(size=3); v -= v.dot(b)*b; v/=np.linalg.norm(v)
        ang = dl*np.sqrt(rng.random()) if rng.random()<0.7 else dl
        d = np.cos(ang)*b + np.sin(ang)*v
        I += T/m*d*h; m -= alpha*T*h
        # rotate b by angle <= w h about axis perp to b
        ax = rng.normal(size=3); ax -= ax.dot(b)*b; ax/=np.linalg.norm(ax)
        th = w*h*(1 if rng.random()<0.6 else rng.random())
        b = np.cos(th)*b + np.sin(th)*np.cross(ax,b); b/=np.linalg.norm(b)
    return I

for (tf,w,dl,rho1,rho2,m0,alpha) in [(5,0.3,np.radians(15),400,1000,80,5.66e-4),
                                      (8.5,0.3,np.radians(15),400,1000,80,5.66e-4),
                                      (5,0.5,np.radians(15),400,1000,80,5.66e-4),
                                      (3,0.2,0.0,1,1,1,0.0)]:
    if dl + w*tf/2 > np.pi/2: print("out of regime"); continue
    g = G(tf/2,tf,w,dl,rho1,m0,alpha); mz = Mz_free(tf,w,dl,rho1,m0,alpha)
    norms = [np.linalg.norm(random_traj(tf,w,dl,rho1,rho2,m0,alpha)) for _ in range(300)]
    print(f"tf={tf} w={w} dl={dl:.3f}: G(tf/2)={g:.4f} |M|={mz:.4f} gap={g-mz:.4f} Gamma_explicit={Gamma_free(tf,w,dl,rho1,m0,alpha):.4f} min|I| random={min(norms):.4f}")

# Tent case: Q(beta) = max over lambda in [0,beta] of H_lambda(beta) - Mz cos(lambda)
def tent_gap(tf,w,dl,rho1,m0,alpha,nb=301,nl=61,n=3001):
    s = np.linspace(0,tf,n); a = a1_fun(s,rho1,m0,alpha)
    phi = w*np.minimum(s, tf-s)
    Mz = np.trapezoid(a*np.cos(dl+phi), s)
    best = np.inf; argb=None
    for beta in np.linspace(0, w*tf/2, nb):
        q = -np.inf
        for lam in np.linspace(0, beta, nl):
            A = np.minimum(phi+lam, w*np.abs(s-tf/2)+beta-lam)
            H = np.trapezoid(a*np.cos(dl+A), s)
            q = max(q, H - Mz*np.cos(lam))
        if q < best: best, argb = q, beta
    return best, argb, Mz
for (tf,w,dl,rho1,m0,alpha) in [(6,0.3,np.radians(15),400,80,5.66e-4),(6,0.3,np.radians(15),400,80,0.0),
                               (10,0.3,np.radians(15),400,80,5.66e-4),(6,0.3,np.radians(15),400,80,0.03),
                               (4,0.5,0.0,1,1,0.2)]:
    print("tent", (tf,w,dl,alpha), "min_beta Q =", tent_gap(tf,w,dl,rho1,m0,alpha))
