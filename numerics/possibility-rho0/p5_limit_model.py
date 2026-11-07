"""Small-angle, delta=0 limit model of the lateral face (exact polynomial computation).
tf = 1, omega = 1 (scale-free).  Payoff  P[beta] = int_0^sig (sig-s)(-beta)^+ + int_sig^1 (s-sig) beta^+.
V(b) = value with beta(sig)=b (early: lower envelope max(-s, b-(sig-s)); late: b + (s-sig))."""
import sympy as sp
s, b, sig = sp.symbols('s b sigma', real=True)
def V(bv, sv):
    s1 = (sv - bv)/2
    if bv <= 0:
        E = sp.integrate((sv - s)*s, (s, 0, s1)) + sp.integrate((sv - s)*(sv - bv - s), (s, s1, sv))
    else:
        E = sp.integrate((sv - s)*s, (s, 0, s1)) + sp.integrate((sv - s)*(sv - bv - s), (s, s1, sv - bv))
    tau = 1 - sv
    if bv >= 0: Lt = sp.integrate(s*(bv + s), (s, 0, tau))
    elif -bv < tau: Lt = sp.integrate(s*(bv + s), (s, -bv, tau))
    else: Lt = 0
    return sp.nsimplify(sp.expand(E + Lt))
sv = sp.Rational(2, 3)
print("V(+sig) =", V(sv, sv), " V(-sig) =", V(-sv, sv))
# symbolic pieces on b in [-2/3, -1/3), [-1/3, 0], [0, 2/3]
bb = sp.symbols('bb', real=True)
s1 = (sv - bb)/2
E_neg = sp.integrate((sv - s)*s, (s, 0, s1)) + sp.integrate((sv - s)*(sv - bb - s), (s, s1, sv))
E_pos = sp.integrate((sv - s)*s, (s, 0, s1)) + sp.integrate((sv - s)*(sv - bb - s), (s, s1, sv - bb))
tau = 1 - sv
L_pos = sp.integrate(s*(bb + s), (s, 0, tau)); L_negsmall = sp.integrate(s*(bb + s), (s, -bb, tau))
pieces = {"[-2/3,-1/3]": sp.expand(E_neg), "[-1/3,0]": sp.expand(E_neg + L_negsmall), "[0,2/3]": sp.expand(E_pos + L_pos)}
top = sp.Rational(4, 81)
for k, p in pieces.items():
    lo, hi = [sp.Rational(x) for x in k.strip('[]').split(',')]
    crit = [r for r in sp.solve(sp.diff(p, bb), bb) if r.is_real and lo <= r <= hi]
    cand = [lo, hi] + crit
    vals = [(c, p.subs(bb, c)) for c in cand]
    print(k, sp.factor(p), " candidates:", [(str(c), float(v)) for c, v in vals], " top-max:", float(top - max(v for _, v in vals)))
