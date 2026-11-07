"""Leading-order (omega*tf -> 0) model of the sign-change face with axis angle phi0 = pi/2 + delta (late kink):
   maximize  P[beta] = -kappa int_0^sig (sig-s) beta ds + int_sig^1 (s-sig) beta^+ ds,  kappa = cos(2 delta) in (0,1],
   over 1-Lipschitz beta with beta(0)=0 (tf = omega = 1 after scaling).  (delta = 0 gives kappa=1 but then the
   early term is also kinked; the delta=0 case is handled in p5.)  Exact polynomial analysis."""
import sympy as sp
b, sg, k, t, s = sp.symbols('b sigma kappa t s', real=True)
s1 = (sg - b)/2
E = -k*(sp.integrate((sg - s)*(-s), (s, 0, s1)) + sp.integrate((sg - s)*(b - sg + s), (s, s1, sg)))
E = sp.expand(E)
tau = 1 - sg
Lpos = sp.integrate(t*(b + t), (t, 0, tau))                    # b >= 0
Lneg = sp.integrate(t*(b + t), (t, -b, tau))                   # -tau < b < 0
Vpos, Vneg, Vvneg = sp.expand(E + Lpos), sp.expand(E + Lneg), E  # b <= -tau: late part 0
print("E(b) =", sp.factor(E))
print("d2E/db2 =", sp.simplify(sp.diff(E, b, 2)))
print("V on b>=0:", sp.factor(Vpos), " d2:", sp.factor(sp.diff(Vpos, b, 2)))
print("V on -tau<b<0:", sp.factor(Vneg), " d2:", sp.factor(sp.diff(Vneg, b, 2)))
# Since E is concave (d2E = -kappa/2 < 0?) check, maxima: compare branch b = sigma (endpoint, V convex there?) etc.
import numpy as np
f = sp.lambdify((b, sg, k), sp.Piecewise((Vpos, b >= 0), (Vneg, b > -(1 - sg)), (Vvneg, True)), 'numpy')
for kv in [1.0, 0.866, 0.5, 0.2, 0.05]:
    prev = None; jumps = []
    for sv in np.linspace(0.01, 0.99, 981):
        bb = np.linspace(-sv, sv, 4001); v = f(bb, sv, kv); a = bb[np.argmax(v)]
        if prev is not None and abs(a - prev[1]) > 0.05: jumps.append((round(prev[0], 4), round(sv, 4), round(prev[1], 4), round(a, 4)))
        prev = (sv, a)
    print(f"kappa={kv}: jumps (sigma_before, sigma_after, argmax_before, argmax_after):", jumps)
