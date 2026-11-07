"""[adversary-6dof] Independent check of the centre-of-percussion identity  y = r + eps b,  eps = Jt/(m L):
   Delta ydot  ==  int (T cos mu/m - eps |w_perp|^2) b dt   (gravity-free part),
using the full 6DOF quaternion/Euler model of m3tvc.py (cone gimbal, random controls).
Reports the residual for: (a) alpha=0, no roll; (b) alpha=0 with roll spin (gyroscopic term); (c) GTPL alpha (eps varies with m)."""
import numpy as np
from m3tvc import gtpl
def qmul(p,q):
    pw,px,py,pz=p; qw,qx,qy,qz=q
    return np.array([pw*qw-px*qx-py*qy-pz*qz, pw*qx+px*qw+py*qz-pz*qy, pw*qy-px*qz+py*qw+pz*qx, pw*qz+px*qy-py*qx+pz*qw])
def rot(q,v): return qmul(qmul(q,np.r_[0,v]),q*np.array([1,-1,-1,-1]))[1:]
def run(P,roll,seed=0,tf=2.0,n=20000):
    rng=np.random.default_rng(seed); h=tf/n
    kn=rng.uniform(-1,1,(2,8))*np.sin(P["delta"])*0.95; Tk=rng.uniform(P["rho1"],P["rho2"],8)
    def ctrl(t):
        s=t/tf*7; i=min(int(s),6); f=s-i
        g=(1-f)*kn[:,i]+f*kn[:,i+1]; T=(1-f)*Tk[i]+f*Tk[i+1]
        return T,g,(3.0*np.sin(5*t) if roll else 0.0)
    def rhs(x,t):
        v,m,q,w=x[0:3],x[3],x[4:8],x[8:11]
        T,g,tr=ctrl(t); db=np.r_[g,np.sqrt(1-g@g)]
        tau=P["L"]*T*np.array([db[1],-db[0],0])+np.r_[0,0,tr]
        J=np.array([P["Jt"],P["Jt"],P["Ja"]]); wd=(tau-np.cross(w,J*w))/J
        return np.r_[T/m*rot(q,db), -P["alpha"]*T, 0.5*qmul(q,np.r_[0,w]), wd]
    x=np.r_[0,0,0,P["m0"],1,0,0,0,0,0,0.0]; I=np.zeros(3)
    def integrand(x,t):
        m,q,w=x[3],x[4:8],x[8:11]; T,g,_=ctrl(t); eps=P["Jt"]/(m*P["L"])
        b=rot(q,np.r_[0,0,1.0]); return (T*np.sqrt(1-g@g)/m-eps*(w[0]**2+w[1]**2))*b
    for k in range(n):
        t=k*h
        k1=rhs(x,t);k2=rhs(x+h/2*k1,t+h/2);k3=rhs(x+h/2*k2,t+h/2);k4=rhs(x+h*k3,t+h)
        i1=integrand(x,t);
        xn=x+h/6*(k1+2*k2+2*k3+k4); i2=integrand(x+h/2*k1,t+h/2); i3=integrand(xn,t+h)
        I+=h/6*(i1+4*i2+i3); x=xn; x[4:8]/=np.linalg.norm(x[4:8])
    m,q,w=x[3],x[4:8],x[8:11]; eps=P["Jt"]/(m*P["L"]); eps0=P["Jt"]/(P["m0"]*P["L"])
    bdot=rot(q,np.cross(w,[0,0,1.0]))
    dy=x[0:3]+eps*bdot          # ydot(tf)-ydot(0), bdot(0)=0
    return np.linalg.norm(dy-I), np.linalg.norm(x[0:3]), np.linalg.norm(eps*bdot)
for name,P,roll in [("alpha=0,no roll",gtpl(alpha=0.0),False),("alpha=0,roll spin",gtpl(alpha=0.0),True),("GTPL alpha, no roll (eps(m) varies)",gtpl(),False)]:
    r=run(P,roll); print(f"{name:40s} residual |dydot - int f b| = {r[0]:.3e}   (|dv|={r[1]:.3f}, |eps bdot(tf)|={r[2]:.3f})")
