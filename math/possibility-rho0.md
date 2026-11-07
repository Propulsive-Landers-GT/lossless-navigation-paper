# ρ1 = 0 (thrust can switch off): is 5DOF powered descent convexifiable?

Author: [possibility-rho0]. Status: CLAIMED (CLAIMS rows P0-R, P0-F, P0-X, P0-T, P0-TVC). Numerics: `numerics/possibility-rho0/`.

**Verdict.** No. Switching the engine off makes the **velocity** set convex. That is [redteam-reform]'s RR-R0, re-proved here with the sharp threshold. It does **not** make the **landing** set $F_{t_f}$ convex. On an explicit exposed face of the two-moment set $K=\{(I,J)\}$, two different attitude strategies tie, and their midpoint is not reachable. This is proved for every $\delta\in[0,\pi/4)$ and every $0<\omega t_f<\pi/2-2\delta$, which covers most of the short-horizon regime. Numerics find the same ties on the rest of that regime, in the tent variant, and with large $\delta$. With an altitude constraint $r_z\ge0$ the result is proved when full-throttle thrust-to-weight is $\gtrsim 2$ (precise bound below). For pure TVC it is proved in a strong-torque/small-gimbal asymptotic regime. **So the hoped-for dichotomy "5DOF LCvx is possible iff ρ1 = 0" is false.** No uniform state-linear convex relaxation is lossless for 5DOF landing even with $\rho_1=0$ (Theorem A + Theorem P0-F). What remains open: altitude-constrained convexity at GTPL's $T/W\approx1.27$, and TVC at GTPL constants (§6).

Setting throughout (unless stated): model M1 of math/02 §1.2 with $\rho_1=0$, $\alpha=0$ (so $a(s)\in[0,a_2]$, $a_2=\rho_2/m_0$), $b(0)=e_z$, $b(t_f)$ free, $0\le\delta<\pi/2$, $0<\omega<\infty$. Write $u=a\,d$, $I=\int_0^{t_f}u$, $J=\int_0^{t_f}(t_f-s)u$, $K=\{(I,J)\}\subset\mathbb R^6$, $R=\{I\}$. $F_{t_f}=A^{-1}(K)$ for an affine bijection $A$ (math/02 Lemma 3.1), so **$F_{t_f}$ is convex iff $K$ is convex**. For fixed $b$, the pointwise control set $U(b)=\{u:\|u\|\le a_2,\ \langle u,b\rangle\ge\|u\|\cos\delta\}$ is convex and contains $0$. Its support function is
$$h_{U(b)}(p)=a_2\|p\|\,c\big(\angle(p,b)\big),\qquad c(x)=\begin{cases}1&x\le\delta\\ \cos(x-\delta)&\delta\le x\le\delta+\pi/2\\ 0&x\ge\delta+\pi/2.\end{cases}$$

## 0. Two structural facts

**Lemma 0.1 (star shape, compactness).** $K$ and $R$ are compact and star-shaped about $0$ (replace $a$ by $\lambda a$, $\lambda\in[0,1]$). *Proof of compactness:* the $b$'s are equi-Lipschitz (Arzelà–Ascoli). Take $u_n\overset{*}\rightharpoonup u$ in $L^\infty$. Since $U(\cdot)$ is convex, closed-valued and upper semicontinuous, Mazur's lemma gives $u(s)\in U(b(s))$ a.e. ∎

**Lemma 0.2 (face criterion).** Let $S\subset\mathbb R^n$ be compact and star-shaped about $0$. Then $S$ is convex iff every exposed face $\operatorname{conv}S\cap\{\langle n,\cdot\rangle=h_S(n)\}$ is contained in $S$. In particular, if every exposed face of $\operatorname{conv}S$ is a single point, $S$ is convex. *Proof (⇐):* every boundary point of $\operatorname{conv}S$ lies on some exposed face, hence in $S$. For $x\in\operatorname{conv}S\setminus\{0\}$, let $t^*=\max\{t:tx\in\operatorname{conv}S\}\ge1$. Then $t^*x\in\partial\operatorname{conv}S\subset S$, and $x=(1/t^*)(t^*x)\in S$. ∎

For $K$ the face in direction $n=(\psi,\chi)$ is governed by the **primer** $p(s)=\psi+(t_f-s)\chi$:
$$h_K(n)=\sup_b\int_0^{t_f}a_2\|p(s)\|\,c\big(\angle(p(s),b(s))\big)\,ds ,$$
and $K\cap\text{face}(n)$ is exactly the set of moments of maximizing controls. So **$K$ is nonconvex iff some primer has maximizers whose moment set is not convex** (e.g. two isolated maximizers).

## 1. The velocity set is convex (sharp)

**Proposition P0-R.** With $\rho_1=0$, $\alpha=0$, $b(t_f)$ free: $R$ is convex **iff** $\delta+\omega t_f\le\pi/2$. In that case
$$R=R_{env}:=\Big\{\int_0^{t_f}u:\ \|u(s)\|\le a_2,\ \angle(u(s),e_z)\le\delta+\omega s\Big\},$$
the 3DOF time-varying-envelope set. Tent variant ($b(t_f)=e_z$): convex iff $\delta+\omega t_f/2\le\pi/2$.

*Proof.* (⇐) Take a direction $\psi$ with $\theta=\angle(\psi,e_z)$. By the triangle inequality and (AL$_\omega$), $\angle(\psi,b(s))\ge\max(\theta-\omega s,0)$. Equality holds for the geodesic $b^*$ that runs from $e_z$ toward $\psi$ at rate $\omega$. Since $c$ is nonincreasing, $h_R(\psi)=a_2\int c(\max(\theta-\omega s,0))ds$. Every maximizer has $a\langle\psi,d\rangle=a_2c(\cdot)$ a.e. Consider where $\theta-\omega s\in(\delta,\delta+\pi/2)$. There $c$ is strictly decreasing, so $b(s)$ must realize the triangle equality. If $\theta<\pi$, the geodesic is unique and $b=b^*$ (rigidity, math/02 Lemma 4.5), so $d$ is unique. Where $\theta-\omega s\le\delta$, $d=\psi$. Where $\theta-\omega s>\delta+\pi/2$, $a=0$. So the face is a single point when $\theta<\pi$. For $\psi=-e_z$ ($\theta=\pi$), $\delta+\omega t_f\le\pi/2$ gives $c\equiv0$, and the face is $\{0\}$. Lemma 0.2 then gives convexity. $R_{env}$ is convex by Aumann's theorem (its cone sets are convex because $\delta+\omega s\le\pi/2$), and its support function is $a_2\int\cos(\max(\theta-\delta-\omega s,0))^+=h_R$. Also $R\subseteq R_{env}$. Two closed convex sets with the same support function are equal.
(⇒) This is math/02 Prop 8.1. At $\psi=-e_z$ every meridian is a geodesic, and the face $\{X_u:u\in S^1\}$ has a midpoint that rigidity forbids. ∎

This coincides with RR-R0 ([redteam-reform] §3.2). The new parts are the "only if" and the identification $R=R_{env}$. **Corollary:** for problems that constrain only the terminal *velocity* (position free), the 3DOF envelope SOCP is feasibility-exact. A certificate is recovered constructively: for boundary points, the unique geodesic maximizer above; for interior points, scale the throttle (Lemma 0.2). This is the only exact result I found at $\rho_1=0$. It does not extend to landing.

## 2. The landing set is not convex (main theorem)

### 2.1 The sign-change faces and an exact 1D reduction
Fix a unit $\hat p$ with $\phi_0=\angle(\hat p,e_z)\in(0,\pi)$ and $\sigma\in(0,t_f)$. Take $\psi=(t_f-\sigma)\hat p$ and $\chi=-\hat p$, so $p(s)=(s-\sigma)\hat p$. The face functional is
$$\ell_\sigma(X)=\Big\langle\hat p,\int_0^{t_f}(s-\sigma)\,a\,d\,ds\Big\rangle=\langle\hat p,\ r_0+\sigma v_0\rangle+\text{const}$$
(math/02 Lemma 10.1). Before $\sigma$ the primer is $-\hat p$; after $\sigma$ it is $+\hat p$.

**Lemma 2.1 (1D reduction).** Let $\theta(s)=\angle(\hat p,b(s))$ and $\beta=\phi_0-\theta$ (the tilt toward $\hat p$). Then $\beta$ is $\omega$-Lipschitz with $\beta(0)=0$, and
$$\ell_\sigma\le a_2P[\beta],\qquad P[\beta]=\int_0^\sigma(\sigma-s)\,c(\pi-\phi_0+\beta)\,ds+\int_\sigma^{t_f}(s-\sigma)\,c(|\phi_0-\beta|)\,ds .$$
Conversely, every such $\beta$ is realized with equality, by $b$ on the great circle through $e_z$ and $\hat p$ with $d$ the point of $\operatorname{cone}(b,\delta)$ closest to $\mp\hat p$. Hence $h_K(n)=a_2\sup_\beta P$. *Proof:* $|\theta(s)-\theta(s')|\le\angle(b(s),b(s'))$, and $\angle(-\hat p,b)=\pi-\theta$. ∎

The early integrand is nonincreasing in $\beta$ and the late one nondecreasing (for $\beta\le\phi_0$). So for fixed $\beta^*:=\beta(\sigma)$ the optimal path is: the **lower envelope** $L_{\beta^*}(s)=\max(-\omega s,\ \beta^*-\omega(\sigma-s))$ on $[0,\sigma]$, then the **upper envelope** $\beta^*+\omega(s-\sigma)$. Every maximizer coincides with these envelopes wherever the integrand is strictly monotone. On those arcs $\theta$ moves at full rate $\omega$, which forces $b$ onto the meridian through $\hat p$ (the gradient flow of $\angle(\hat p,\cdot)$; unique away from $\pm\hat p$). Where the integrand vanishes, $a=0$. Hence
$$h_K(n)=a_2\max_{\beta^*\in[-\omega\sigma,\omega\sigma]}V(\beta^*),\qquad V=E(\beta^*)+L_t(\beta^*).$$
The maximizers split by the value $\beta^*$.

### 2.2 Theorem P0-F (unconstrained landing set)
**Theorem P0-F.** Let $\rho_1=0$, $\alpha=0$, $b(t_f)$ free, $0\le\delta<\pi/4$, and $0<\omega t_f<\pi/2-2\delta$. Then $K$ and $F_{t_f}$ are **nonconvex**. Hence (Theorem A) no uniform convex relaxation of the 5DOF landing problem is lossless, even with the engine allowed to switch off. The witness is the face $\hat p=(\cos\delta,0,-\sin\delta)$ (pointing $\delta$ below the horizontal) at a tie value $\sigma_c\in(t_f/2,t_f)$.

*Proof.* Use units $\omega=1$, $a_2=1$, and write $T=\omega t_f$, $\tau=T-\sigma$. With $\phi_0=\pi/2+\delta$:
- early integrand $c(\pi/2-\delta+L)=\sin^+(2\delta-L)$, strictly decreasing in $L$ on $[-T,0]$, because $2\delta-L\in(0,\pi/2)$ there (this uses $T<\pi/2-2\delta$);
- late integrand $c(\pi/2+\delta-\beta)=\sin^+\beta$.

So $E(\beta^*)=\int_0^\sigma(\sigma-s)\sin^+(2\delta-L_{\beta^*})$ is nonincreasing, and $L_t(\beta^*)=\int_0^\tau t\sin^+(\beta^*+t)dt$ vanishes iff $\beta^*\le-\tau$.

Let $\sigma\in[T/2,T]$, so that $-\sigma\le-\tau$. Put $A(\sigma)=\max_{[-\sigma,-\tau]}V=E(-\sigma)$ (there $V=E$, which is nonincreasing) and $B(\sigma)=\max_{[-\tau,\sigma]}V$. Both are continuous.
*At $\sigma=T$:* $\tau=0$ and $B=E(0)<E(-T)=A$. The inequality is strict because $L_0>L_{-T}$ on $(T/2,T)$ and $E$ is strictly decreasing.
*At $\sigma=T/2=:h$:* $B\ge V(h)=E(h)+L_t(h)$. Using $\sin(2\delta+s)-\sin^+(2\delta-s)\le2\sin s$,
$$A-V(h)=\int_0^h(h-s)[\sin(2\delta+s)-\sin^+(2\delta-s)]ds-\int_0^ht\sin(h+t)dt\ \le\ -f(h),$$
$$f(h)=\sin2h-h\cos2h+\sin h-2h .$$
By $\sin x\ge x-x^3/6$ and $\cos x\le1-x^2/2+x^4/24$, $f(h)\ge h^3(\tfrac12-\tfrac23h^2)>0$ for $0<h<\sqrt{3}/2$, which covers $h\le\pi/4$ (numerical check: `p7_C1_check.py`, $\min f/h^3=0.28$). Hence $B>A$.
By the IVT there is $\sigma_c\in(T/2,T)$ with $A=B=\max V$.

At $\sigma_c$ the maximizers lie in $[-\sigma_c,-\tau_c]$ (at least $-\sigma_c$) and in $(-\tau_c,\sigma_c]$. The point $-\tau_c$ is not a maximizer, because $V(-\tau_c)=E(-\tau_c)<E(-\sigma_c)$ (strict decrease, and $\sigma_c>\tau_c$).

Let $M_L$ and $M_R$ be the moment sets of maximizers in the two groups. They are compact: the set of maximizing controls is compact (Lemma 0.1), and $\beta(\sigma)$ is continuous in it. They are disjoint, separated by the linear functional $\langle\hat p,I\rangle=a_2(-\int_0^\sigma c_e+\int_\sigma^{t_f}c_\ell)$. Left maximizers have $c_\ell\equiv0$. Right maximizers have $c_\ell\not\equiv0$ and pointwise smaller $c_e$, since $L_{\beta^*}$ is increasing in $\beta^*$. So $\langle\hat p,I\rangle_L<\langle\hat p,I\rangle_R$.

If $K$ were convex, the face $=M_L\cup M_R$ would be a convex set that is a disjoint union of two nonempty compact sets. That is impossible, because convex sets are connected. ∎

*What the witness pair is.* Both maximize $\langle\hat p,r_0+\sigma_cv_0\rangle$ over $F$.
- (L) Tilt away from $\hat p$ at full rate while thrusting toward $-\hat p$. Then swing back, but the late primer is never reached, so the late phase is a coast.
- (R) A short left tilt with early thrust, reverse at $\approx\sigma_c/2$, then late thrust toward $\hat p$.

The midpoint would need "half of each", and rigidity forbids that.

**Remarks.**
1. Both witnesses steer by **coasting while rotating**. That is exactly what $\rho_1=0$ adds and what M1 allows.
2. The tie value is $\sigma_c/t_f\approx0.67$–$0.70$ (`face.py`). The NLP check (§5) confirms that $\theta_m$ is not reached.
3. *Robustness.* Nonconvexity at a positive distance $\gamma=\operatorname{dist}(\theta_m,F)>0$ survives small perturbations of the model that move $K$ by less than $\gamma/4$ in Hausdorff distance: small $\rho_1>0$, small $\alpha>0$, and fast gimbal-rate limits. That is all consistent with B/B*.

### 2.3 Theorem P0-X (altitude-constrained)
Witness (L) above ends with a coast, so it lands from below and is underground. The same defect as [adversary]'s BREAK on Thm B. The fix is the **early-kink face** $\hat p=(\cos\delta,0,+\sin\delta)$ ($\delta$ *above* the horizontal; the early primer $-\hat p$ points $\delta$ below the horizontal). Now both witnesses thrust throughout $[\sigma,t_f]$.

The altitude constraint for a trajectory landing at $r=v=0$ reads $r_z(t)=\int_t^{t_f}(s-t)(a\,d_z-g)\,ds\ge0$ for all $t$. This is a family of linear constraints on $u$ that does not depend on $\theta$.

**Theorem P0-X.** Let $\rho_1=0$, $\alpha=0$, $b(t_f)$ free, $0<\delta<\pi/4$, $T=\omega t_f<\min(2\delta,\pi/2-2\delta)$. Let $x_*\in(0,1)$ be such that $\sigma=x_*T$ satisfies $\sigma-\sin\sigma>(T-\sigma)^2\sin\sigma$ (for small $T$ one can take $x_*\downarrow1/(1+6^{-1/2})=0.7101$). If
$$\frac{a_2}{g}\ \ge\ \frac{1}{\cos(\delta+T)\,(1-x_*^2)}\qquad(\approx2.1\ \text{for }\delta=15^\circ,\ T\ \text{small}),$$
then the altitude-constrained set $F^{X}_{t_f}=\{\theta\in F_{t_f}:r_z(t)\ge0\ \forall t\}$ is nonconvex.

*Proof.* $\phi_0=\pi/2-\delta$. The early integrand is $\sin^+(-L)$ (kink at $0$, nonincreasing). The late integrand is $\sin(2\delta+\beta)$, which is positive, unsaturated and strictly increasing, since $\beta\ge-T>-2\delta$ and $2\delta+T<\pi/2$.

*V increases near the right end.* $L_t'(\beta^*)\ge\tfrac12\cos(2\delta+T)\tau^2$. For $\beta^*\in[0,\sigma]$, $|E'(\beta^*)|\le\tfrac18(\sigma-\beta^*)(\sigma+3\beta^*)\le\tfrac12\sigma(\sigma-\beta^*)$. So $V'>0$ on $[\beta_0,\sigma]$ with $\beta_0=\sigma-\min(\sigma,\tau^2\cos(2\delta+T)/(2\sigma))$.

*IVT.* Put $A=V(\sigma)$ and $B=\max_{[-\sigma,\beta_0]}V$.
- For small $\sigma$: $B\le E(-\sigma)+L_t(0)\le\sigma^3/6+L_t(0)$ and $A-L_t(0)\ge\tfrac12\sigma\cos(2\delta+T)\tau^2$, so $A>B$.
- At $\sigma=x_*T$: $B\ge V(-\sigma)$ and $V(-\sigma)-V(\sigma)=(\sigma-\sin\sigma)-2\sin\sigma\int_0^\tau t\cos(2\delta+t)\,dt>0$, so $B>A$.

So a tie exists at some $\sigma_c<x_*T$. The maximizers are $\{\sigma_c\}$ and a nonempty set in $[-\sigma_c,\beta_0)$; note $V(\beta_0)<A$. They are separated in moment space by $\langle\hat p,I\rangle$, as in P0-F: the right witness has no early thrust and the largest late thrust. By connectedness the face is not in $K$, so $\theta_m\notin F\supseteq F^X$.

*Altitude.* Both witnesses have $a=a_2$ and $d_z\ge\kappa_0:=\cos(\delta+T)$ on $[\sigma_c,t_f]$, and $d_z>0$ everywhere. For $t\ge\sigma_c$, $r_z(t)\ge(a_2\kappa_0-g)(t_f-t)^2/2$. For $t<\sigma_c$, $r_z(t)\ge\tfrac12a_2\kappa_0(t_f-\sigma_c)(t_f+\sigma_c-2t)-\tfrac12g(t_f-t)^2$, and this is $\ge0$ whenever $g\le a_2\kappa_0(1-(\sigma_c/t_f)^2)$. Hence both witnesses lie in $F^X$. ∎

*Numerical sharpening* (`p12_face2_gcrit.py`, exact $g_{crit}=\min_t\int_t^{t_f}(s-t)u_z/((t_f-t)^2/2)$ for both witnesses):

| δ | ωt_f | required T/W |
|---|---|---|
| 15° | 0.1 | 1.83 |
| 15° | 0.3 | 1.93 |
| 15° | 0.5 | 2.10 |
| 30° | 0.3 | 1.95 |
| 15° | 0.8 | 2.54 (outside proof regime; tie still present) |

**GTPL ($T/W=1.27$ wet, full throttle) is NOT covered.** A random-primer DP search for ties (`p11_tie_gcrit.py`) found 68 ties (T = 0.6, δ = 15°); the best one has both witnesses above ground for $g/a_2\le0.59$ (T/W ≥ 1.71). Glide-slope constraints were not checked (the witnesses move laterally by $O(a_2\omega t_f^3)$).

## 3. Tent variant and large δ (numerical)
- *Tent ($b(t_f)=e_z$).* The planar DP with terminal constraint (`p13_tent.py`; $T=0.6$, $\delta=15^\circ$) finds moment jumps of 23–25× the median step on the faces $\phi_0=75^\circ$ and $105^\circ$, i.e. non-singleton faces. The 1D reduction still bounds 3D from above, with $\theta(t_f)=\phi_0$ realized in-plane. So these are 3D faces. Not proved.
- *δ ≥ π/4.* Theorem P0-F needs $\delta<\pi/4$. Scans with $\delta=40^\circ$ (`axisface.py`) find ties at $\phi_0\approx45^\circ$ and $128$–$158^\circ$ (ωt_f = 0.2, 0.6). Not proved.
- *Rest of the short-horizon regime* ($\pi/2-2\delta\le\omega t_f\le\pi/2-\delta$). Scans find ties on the lateral face (`p2_jumpscan.py`: argmax jumps 0.4–0.97 for $\delta\le25^\circ$). Not proved.
- No-tie region of the *lateral* face ($\hat p=e_x$): $\delta\gtrsim0.65\,\omega t_f$. There the payoff stays in the concave branch of $c$. Ties need the convex kink of $c$ at $\angle=\delta+\pi/2$ (thrust on/off boundary) to be reachable. This is the mechanism: **switching off is itself the source of nonconvexity** for the two-moment set.

## 4. Pure TVC (6DOF, gimbal = torque input), ρ1 = 0
Model: $\ddot r=(T/m)d-g$, $d=\cos\mu\,b+\sin\mu\,n$ ($n\perp b$, $|\mu|\le\bar\mu$), transverse angular acceleration of magnitude $\le\kappa T$ with $\kappa=L\sin\bar\mu/J_t$ (direction tied to the gimbal), roll rate $0$, body-rate cap $\|\omega_\perp\|\le\bar\omega$, $\omega(0)=0$, $b(0)=e_z$, terminal attitude free, $T\in[0,\rho_2]$, $\alpha=0$. With $T=0$, $\omega$ is constant: the vehicle can coast-rotate but cannot change its rate.

**Proposition P0-TVC.** Fix $\bar\omega t_f<\pi/2$. There are $\mu_0>0$ and $\kappa_0<\infty$ such that for $\bar\mu<\mu_0$ and $\kappa\rho_2>\kappa_0$, $F^{TVC}_{t_f}$ is nonconvex.
*Proof.*
(i) $K_{TVC}\subseteq K_{M1}(\delta=\bar\mu,\omega=\bar\omega)$, since $b$ is $\bar\omega$-Lipschitz and $\angle(d,b)\le\bar\mu$.
(ii) $K_{M1}(\delta)\downarrow K_{M1}(0)$ as $\delta\downarrow0$ (nested compacts with intersection $K_{M1}(0)$ by closedness), so $\operatorname{dist}(X_m,K_{M1}(\bar\mu))>\gamma_0/2$ for small $\bar\mu$. Here $X_m$ is the P0-F midpoint at $\delta=0$, with $\gamma_0=\operatorname{dist}(X_m,K_{M1}(0))>0$.
(iii) The two $\delta=0$ witnesses are piecewise constant-rate rotations with finitely many rate changes. TVC reproduces them within $\eta=O(\bar\mu+a_2\bar\omega/(\kappa\rho_2))$:
   - thrusting arcs use sign-chattered gimbal (mean torque 0, thrust $\cos\bar\mu$ along $b$);
   - coasting arcs keep $\omega$ constant for free;
   - each rate change costs a thrust pulse of length $\le2\bar\omega/(\kappa\rho_2)$.
For $\eta<\gamma_0/8$, the TVC midpoint is at distance $>\gamma_0/4$ from $K_{TVC}$. ∎

At GTPL constants, the pulse cost $\bar\omega J_t/(mL\sin\bar\mu)=\varepsilon\bar\omega/\sin\bar\mu\approx2$ m/s per rate change ($\varepsilon=1.35$ m, $\bar\mu=15^\circ$, $\bar\omega=0.4$). That is not small, so **TVC at GTPL constants is OPEN**.

A symmetric (rotation-invariant) face cannot help TVC. The $-e_z$ face rewards spinning through the centre-of-percussion term $\varepsilon\|\omega\|^2$ (FLAT). But the gain/cost ratio is $\le\sin\bar\mu\cdot(\text{angle}\cdot\bar b_z)/4<1$, so do-nothing is optimal there.

## 5. Numerical confirmation (3D, inner discretization, ipopt)
`p8_nlp_gap.py`: M1 3D. The nodes $b_k\in S^2$ satisfy $\langle b_k,b_{k+1}\rangle\ge\cos\omega h$. The per-interval $u_k$ is constrained to the gimbal caps at both ends, which are geodesically convex, so every NLP point is admissible and the NLP value is an **upper** bound on $\operatorname{dist}(\theta_m,F)$. Parameters: $a_2=12.5$, $\omega=0.4$ rad/s, $\delta=15^\circ$, $t_f=1.5$ s ($T=0.6$, P0-F regime). Witnesses $\theta_1,\theta_2$: separation 10.8 (m, m/s). Their face values agree to $8\cdot10^{-9}$, and $\langle\hat p,I\rangle$ is $-8.54$ vs $-6.94$ (disjoint, as proved).

| N | starts | min dist(θ_m, F) found |
|---|---|---|
| 30 | 26 | 0.066 |
| 60 | 22 | 0.045 |
| 120 | 12 | 0.78 (not converged: too few starts at this size; local minima) |

Like B*, the dent is real but **thin**: about 0.2–0.6 % of the witness separation. Witness (L) is underground ($r_{z,\min}=-5.3$ m), as §2.3 predicts. Independent planar DP (`dp.py`, validated against the closed form: jump at σ/T = 0.687 vs 0.688) reproduces every tie.

## 6. Status and open items
- P0-R (velocity set convex iff $\delta+\omega t_f\le\pi/2$; $R=R_{env}$): proved.
- P0-F (landing set nonconvex, $\delta<\pi/4$, $\omega t_f<\pi/2-2\delta$): proved. The rest of the short-horizon regime and $\delta\ge\pi/4$: numerical.
- P0-X (with $r_z\ge0$): proved for $T/W\ge[\cos(\delta+T)(1-x_*^2)]^{-1}\approx2.1$; numerically down to about 1.7. **GTPL T/W 1.27: open.** Glide slope: open.
- P0-T (tent): numerical.
- P0-TVC: asymptotic regime proved. GTPL constants: open.
- Not attempted: quantitative lower bound on $\operatorname{dist}(\theta_m,F)$ (needs a stability estimate for the tie); $\alpha>0$ beyond perturbation.
- **"Is LCvx lossless where F is convex?"** The only convex object found is $R$, where the envelope SOCP is exact (§1). For landing there is no convex regime to check, so the question is moot.
