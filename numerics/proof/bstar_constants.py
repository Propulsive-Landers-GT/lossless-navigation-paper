"""Explicit constants for Thm B* (dive-then-brake face) in math/02 §10."""
import numpy as np
def consts(rho1=400,rho2=1000,m0=80,alpha=5.66e-4,g0=9.81,dl=np.radians(15),w=0.4,tf=7.0,gs=np.radians(30)):
    amax=rho2/(m0-alpha*rho2*tf); a10=rho1/m0; Ab=rho2/m0-g0
    s_lim=[dl/w, g0 and Ab*tf/(g0+Ab)*0.999]
    # glide: tan(gs)*amax*s^2 <= Ab*(tf-s)^2  -> s/(tf-s) <= sqrt(Ab/(amax tan gs))
    k=np.sqrt(Ab/(amax*np.tan(gs))); s_lim.append(k*tf/(1+k))
    s=min(s_lim)
    theta=min(0.25,a10*np.sin(dl)/(4*amax))
    gX=5/32*a10*np.sin(dl)*s**2
    Wb=amax*(tf-s)**2/2
    c=1/(w*theta*s)
    # solve eta*(1+c)+sqrt(2 Wb eta)=gX
    A=1+c; B=np.sqrt(2*Wb)
    x=(-B+np.sqrt(B*B+4*A*gX))/(2*A); eta0=x*x
    return dict(s_star=s,limits=s_lim,theta=theta,gamma_X=gX,W_b=Wb,eps_B=eta0,dist_theta=eta0/np.sqrt(1+s*s))
for tf in [5,7,12]:
    print(tf,consts(tf=tf))
