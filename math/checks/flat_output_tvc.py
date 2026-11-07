"""Symbolic check: for an axisymmetric TVC rigid body with zero roll rate, the point
y = r + eps*b (eps = J_t/(m L)) has acceleration exactly along the body axis b:
   y'' = (T cos(mu)/m - eps*|w|^2) b - g.
Engine at -L*b from CG, thrust T = T cos(mu) b + Tperp (Tperp ⊥ b, |Tperp| = T sin mu)."""
import sympy as sp
m,L,Jt,T,mu,g = sp.symbols('m L J_t T mu g', positive=True)
# body axis b and an orthonormal frame; generic orientation via symbols
b = sp.Matrix(sp.symbols('b1 b2 b3'))
p = sp.Matrix(sp.symbols('p1 p2 p3'))    # unit vector ⊥ b, direction of Tperp
w = sp.Matrix(sp.symbols('w1 w2 w3'))    # angular velocity, ⊥ b (zero roll)
cons = {}
eps = Jt/(m*L)
Tvec = T*sp.cos(mu)*b + T*sp.sin(mu)*p
tau = (-L*b).cross(Tvec)                      # torque about CG
wdot = tau/Jt                                 # axisymmetric, w ⊥ b: gyroscopic term w x (J w) = 0
bdot = w.cross(b)
bddot = wdot.cross(b) + w.cross(w.cross(b))
rddot = Tvec/m - sp.Matrix([0,0,g])
yddot = rddot + eps*bddot
claim = (T*sp.cos(mu)/m - eps*(w.dot(w)))*b - sp.Matrix([0,0,g])
diff = sp.simplify(yddot - claim)
# impose |b|=1, p.b=0, w.b=0, |p|=1 via substitution check numerically on random admissible data
import random, math
def rand_unit():
    v=[random.gauss(0,1) for _ in range(3)]; n=math.sqrt(sum(x*x for x in v)); return [x/n for x in v]
worst=0
for _ in range(200):
    bb=sp.Matrix(rand_unit()); q=sp.Matrix(rand_unit()); pp=(q-q.dot(bb)*bb); pp=pp/pp.norm()
    q2=sp.Matrix(rand_unit()); ww=(q2-q2.dot(bb)*bb)*random.uniform(0,3)
    subs={**{f'b{i+1}':bb[i] for i in range(3)},**{f'p{i+1}':pp[i] for i in range(3)},**{f'w{i+1}':ww[i] for i in range(3)},
          m:random.uniform(50,90),L:random.uniform(.3,.8),Jt:random.uniform(30,70),T:random.uniform(300,1200),mu:random.uniform(-.3,.3),g:9.81}
    val=diff.subs(subs).evalf()
    worst=max(worst,max(abs(x) for x in val))
print("max residual over 200 random admissible states:", worst)
