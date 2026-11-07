import numpy as np, sys
exec(open('exp5_tvc1check.py').read().split("rng=np.random")[0])
o.solver("ipopt",{"ipopt.print_level":3,"print_time":0,"ipopt.max_iter":400,"ipopt.tol":1e-10,"ipopt.sb":"yes"})
exec("wit=np.load('../proof-tvc/witness_cone_1.0_0.25.npy')\n"+open('exp5_tvc1check.py').read().split("wit=np.load(\"../proof-tvc/witness_cone_1.0_0.25.npy\")")[1].split("def dive")[0])
o.set_value(latpar,0)
wit_init(1.0)
Xi=np.array(o.debug.value(R.X,o.initial())); 
d=Xi[0:3,-1]; q=Xi[ir:ir+3,-1]
print("init gain", (-g*tf**2/2+tf*d[2]-q[2])+ss*(g*tf-d[2])-kappa-J0, "final quat", Xi[4:8,-1], "w",Xi[8:11,-1])
r=R.solve(lat=None)
