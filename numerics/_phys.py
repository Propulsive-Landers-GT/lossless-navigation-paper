import numpy as np
from runner import run_many
import models
P=models.gtpl()
if __name__=="__main__":
  for om in [30]:
    for tf in [3.0,5.0,8.0]:
        Pp=models.gtpl(omega=om*np.pi/180)
        N=40
        spec=("M1",Pp,dict(tf=tf,N=N,planar=False,use_r=True,alt=True))
        r=run_many(spec,dict(mode="lin",c=[0,0,1,0,0,0]),40)
        z=r["z"]; g=Pp['g']
        v0z=g*tf-z[2]; r0z=z[2]*tf-z[5]-g*tf**2/2
        W=np.array([1,1,1,0,0,0.])
        d3=run_many(spec,dict(mode="dist",target=[0,0,z[2],0,0,0],W=W),40)
        W6=np.array([1,1,1,1/tf**2,1/tf**2,1/tf**2])
        d6=run_many(spec,dict(mode="dist",target=[0,0,z[2],0,0,z[5]],W=W6),40)
        print(f"om {om} tf {tf}: z*={z[2]:.3f} lat_v={np.hypot(z[0],z[1]):.3f} lat_r={np.hypot(z[3],z[4]):.3f} v0z={v0z:.2f} r0z={r0z:.2f} | dist_v={np.sqrt(d3['f']):.4f} near {np.round(d3['z'][:3],3)} | dist_6w={np.sqrt(d6['f']):.4f}",flush=True)
