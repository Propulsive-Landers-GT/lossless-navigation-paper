"""Upright bang-bang (min then max throttle) hop limit: max v0z for which landing at the pad from r0=0,
v0=(0,0,v0z), tf=4 is possible with d=e_z (switch fixed by M_z = g tf^2/2). GTPL constants."""
import numpy as np
from scipy.optimize import brentq
m0,r1,r2,al,g,T=80.,400.,1000.,0.0005665090072099601,9.80665,4.0
def upright(ts,al):
    s=np.linspace(0,T,200001); Tq=np.where(s<ts,r1,r2)
    m=m0-al*np.concatenate([[0],np.cumsum((Tq[1:]+Tq[:-1])/2*np.diff(s))]); a=Tq/m
    return np.trapezoid(a,s),np.trapezoid(s*a,s)
for alpha in [0.0,al]:
    ts=brentq(lambda t: upright(t,alpha)[1]-0.5*g*T**2,0.5,3.9); Iz,_=upright(ts,alpha)
    print(f"alpha={alpha}: switch {ts:.4f} s, upright max v0z = {g*T-Iz:.4f} m/s")
