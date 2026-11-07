# Impossibility of uniform lossless convexification for 5DOF powered descent: rigorous proofs and extensions

Author: [proof] agent. Status: CLAIMED (see `comms/CLAIMS.md` rows P-*). Source sketch: `math/00` §§2–4.
Companion: `math/03-lean-blueprint.md` (lemma list for Lean). Numerical sanity checks: `numerics/proof/`.

---

## 0. Summary of results

| # | Statement | Regime | Status |
|---|---|---|---|
| Thm A | A lossless uniform convex relaxation forces $F_{t_f}$ to be convex | any problem | proved (§2) |
| Lem 3.1 | $F_{t_f}$ convex $\Rightarrow$ $R$ convex; $\operatorname{dist}(\theta_M,F)\ge\operatorname{dist}(M,R)$ | M1 and all models here | proved (§3) |
| Thm B | $M\in\operatorname{conv}R\setminus R$ (rigidity route) | free: $\delta+\omega t_f\le\pi/2$; tent: $\delta+\omega t_f/2\le\pi/2$ | proved (§4) |
| Thm Q | **Ball bound** $\|I\|\ge G(\tau)$ for every $I\in R$; $\operatorname{dist}(M,R)\ge\Gamma_F>0$ explicit | free: $\delta+\omega t_f/2\le\pi/2$ (+ sign condition) | proved (§5) |
| Thm Q_T | Tent variant: $\operatorname{dist}(M,R)\ge\gamma_T>0$ | $\alpha=0$ proved; $\alpha>0$ under a checkable condition (verified numerically) | proved / conditional (§5) |
| Cor ε | No $\varepsilon$-lossless uniform convex relaxation for $\varepsilon<\operatorname{dist}(M,R)$ | as Thm Q | proved (§5) |
| Thm E | Envelope models: M3a (torque-limited, independent transverse torque, axisymmetric, $\Omega(0)=0$), rate+torque limits, 6DOF M4 | free terminal attitude | proved (§6) |
| Conj B3b | Gimbal-torque-coupled M3b | — | **open**: the extreme arcs are not realizable (§6.4) |
| Thm L | Free terminal attitude, **every** $t_f>0$, $0\le\delta<\pi$, $\alpha\ge 0$ | M1 | proved (§7) |
| Thm L_T | Tent variant, $\delta+\omega t_f/2\le\pi$, $\omega t_f/2<\pi$ | M1 | proved (§7); the witness fails for $\omega t_f\ge 2\pi$ |
| **Thm B\*** | **Dive-then-brake exposed face: $F^{\mathcal X}_{t_f}$ nonconvex WITH altitude + glide-slope constraints, every $t_f>0$, upright-landing variant, free $t_f$ on compact windows; explicit (tiny) quantitative gap for $\delta\le\pi/4$** | $\rho_1>0$, $0<\delta<\pi/2$, $\rho_2/m_0>g_0$ | **proved (§10); main theorem** |
| Thm D / D.1 | Per-instance: every state-linear relaxation (Def. 11.1) is lossy at $\operatorname{conv}\mathrm{Reach}\setminus\operatorname{cl}\mathrm{Reach}$; unconditional instance with terminal-error cost and altitude constraints | — | proved (§11) |
| Lemma S | Hard soft-landing per-instance version ⇔ a nonconvex $r_{0h}$-slice of $F$ | — | **open**; exact reduction (Prop 11.2) |
| Prop 11.3 | Trivial exact convex reformulation exists (convex hull of lifted graph) but is not state-linear | — | proved |
| Lemma 6.4 | TVC center-of-percussion flat output: lateral gimbal force cancels exactly when roll rate is 0 | pure TVC | proved; completing M3b is pending |
| Prop tf | Free final time: joint $(\theta,t_f)$ relaxations impossible; union over a window is nonconvex under an explicit condition | M1 | proved (§7) |
| §8 | $\omega\in(0,\infty)$ is essential. $\rho_1>0$ is essential for the method only when $\delta+\omega t_f\le\pi/2$; for $\delta+\omega t_f>\pi/2$, nonconvexity holds even with $\rho_1=0$ ($\alpha=0$). $\delta$ is inessential ($\delta=0$ works). Exact 3DOF with mass and free $d$: $F$ is convex | — | proved / open items marked |

**Read first:** Theorems B/Q/L are about the state-*unconstrained* problem. Their witnesses start underground for GTPL ([adversary] BREAK). The theorem that covers the real (altitude/glide-slope constrained) problem is **Theorem B\*** (§10), and its per-instance form is **Theorem D** (§11). **Quantitative caveat:** every altitude-feasible face found so far (B\*, its envelope version, and [adversary]/[numerics] runs) has a *thin* gap. The rigorous gap is about 1e-5 m; the heuristic/numerical gap is at most about 1 cm ([adversary] a6, corrected rerun). The m/s gaps of Thms Q/Q_T live at underground faces. So **nonconvexity of the real constrained problem is proven, but a practically significant ε-impossibility for GTPL is not established.** The **simplest complete proof** of nonconvexity is Thm Q (§5). It needs only the spherical triangle inequality (without its equality case), monotonicity of the integral, and one explicit integral. It is the recommended primary Lean target. Thm B (§4) is the route in the orchestrator's sketch. It needs the equality case and rigidity, but covers the tent variant for all $\alpha$.

---

## 1. Model and definitions

### 1.1 Notation
$\langle\cdot,\cdot\rangle$ and $\|\cdot\|$ are Euclidean on $\mathbb R^3$. $S^2=\{x:\|x\|=1\}$. $e_z=(0,0,1)$. For $x\in\mathbb R^3$, $x_z=\langle x,e_z\rangle$ and $x_h=x-x_z e_z$ (the "horizontal" part). A *horizontal unit vector* is $u\in S^2$ with $u_z=0$. For $x,y\in S^2$, $\angle(x,y)=\arccos\langle x,y\rangle\in[0,\pi]$. All functions are on $[0,t_f]$, $t_f>0$, with Lebesgue measure. "a.e." means Lebesgue-a.e. on $[0,t_f]$.

Since $\arccos$ is decreasing, for $x,y\in S^2$ and $\gamma\in[0,\pi]$ we have $\angle(x,y)\le\gamma\iff\langle x,y\rangle\ge\cos\gamma$. All hypotheses below are stated in the inner-product form.

### 1.2 Model M1 (5DOF, kinematic rate-limited thrust axis)
**Parameters.** $0<\rho_1\le\rho_2$ (thrust bounds; §8 discusses $\rho_1=0$), $\alpha\ge0$ (mass depletion rate), $m_0>0$ with
$$\text{(H}_m)\qquad m_0-\alpha\rho_2 t_f>0,$$
$\omega\in(0,\infty)$ (rate limit of the body axis), $\delta\in[0,\pi/2)$ (gimbal half-angle; some results allow $\delta<\pi$), and $g\in\mathbb R^3$ (gravity, arbitrary). The initial body axis is $b_0=e_z$ without loss of generality: rotate coordinates. The direction of $g$ relative to $b_0$ is **never used**.

**Admissible controls** $\mathcal U$: triples $(T,d,b)$ such that
1. $T:[0,t_f]\to[\rho_1,\rho_2]$ is Lebesgue measurable (thrust magnitude);
2. $d:[0,t_f]\to S^2$ is measurable (thrust direction);
3. $b:[0,t_f]\to S^2$ is continuous (body / thrust axis) and **angle-Lipschitz**:
$$\text{(AL}_\omega)\qquad \langle b(s),b(s')\rangle\ \ge\ \cos(\omega|s-s'|)\quad\text{for all } s,s'\in[0,t_f]\text{ with }\omega|s-s'|\le\pi;$$
4. gimbal: $\langle d(s),b(s)\rangle\ge\cos\delta$ for a.e. $s$;
5. attitude boundary conditions: $b(0)=e_z$. Two variants: **(F)** $b(t_f)$ free; **(T)** $b(t_f)=e_z$.

*Mass and acceleration.* $m(t)=m_0-\alpha\int_0^tT$ satisfies $m(t)\ge m_0-\alpha\rho_2t_f>0$ by (H$_m$). $m$ is Lipschitz with $\dot m=-\alpha T$ a.e. The thrust acceleration is $a(t)=T(t)/m(t)$, which is measurable with $0<\rho_1/m_0\le a\le\rho_2/(m_0-\alpha\rho_2t_f)$. *Optional dry-mass constraint* $m(t_f)\ge m_{dry}$, where $m_0-\alpha\rho_1t_f\ge m_{dry}$: every result below holds verbatim with it, because the witnesses use minimum throttle and §7 uses only convexity and weak-* closedness of the throttle set.

*Translational dynamics.* $r,v$ are absolutely continuous, with $\dot r=v$ and $\dot v=a\,d+g$ a.e., $r(0)=r_0$, $v(0)=v_0$. *Landing:* $r(t_f)=0$, $v(t_f)=0$.

**Feasible boundary-data set.**
$$F_{t_f}=\{\theta=(r_0,v_0)\in\mathbb R^3\times\mathbb R^3:\ \exists (T,d,b)\in\mathcal U \text{ whose trajectory from }\theta\text{ lands at }t_f\}.$$
The data $m_0$, $b(0)$ (and $b(t_f)$ in variant T), $t_f$ are fixed. **Crucially, $\mathcal U$ does not depend on $\theta$** (there are no state constraints). Adding state constraints such as glide slope changes $F$ and is not covered (see the adversary's §B* for a face argument that does cover them).

**Lemma 1.1 (solution formula).** For $(T,d,b)\in\mathcal U$ and $\theta=(r_0,v_0)$,
$$v(t_f)=v_0+g t_f+I,\qquad r(t_f)=r_0+v_0t_f+\tfrac12 g t_f^2+J,$$
$$I:=\int_0^{t_f}a(s)d(s)\,ds,\qquad J:=\int_0^{t_f}(t_f-s)a(s)d(s)\,ds .$$
*Proof.* $ad$ is bounded and measurable, hence integrable. FTC for absolutely continuous functions gives $v(t)=v_0+gt+\int_0^tad$. Integrating once more and applying Fubini, $\int_0^{t_f}\!\int_0^t ad\,ds\,dt=\int_0^{t_f}(t_f-s)ad\,ds$. ∎

### 1.3 Angle-Lipschitz versus the ODE formulation
**Proposition 1.2.** Let $b:[0,t_f]\to S^2$. The following are equivalent:
(i) $b$ satisfies (AL$_\omega$);
(ii) $b$ is absolutely continuous and there is a measurable $\Omega:[0,t_f]\to\mathbb R^3$ with $\dot b=\Omega\times b$ a.e. and $\|\Omega_\perp\|\le\omega$ a.e., where $\Omega_\perp:=\Omega-\langle\Omega,b\rangle b$. The roll component $\langle\Omega,b\rangle$ is unrestricted.

*Proof.* (ii)⇒(i). $\|\Omega\times b\|=\|\Omega_\perp\times b\|=\|\Omega_\perp\|$, since $\Omega_\perp\perp b$ and $\|b\|=1$. Hence $\|\dot b\|\le\omega$ a.e. Fix $s<s'$ with $\omega(s'-s)\le\pi$, and a partition $s=t_0<\dots<t_N=s'$ of mesh $h$. Then $\|b(t_{i+1})-b(t_i)\|\le\int_{t_i}^{t_{i+1}}\|\dot b\|\le\omega h$. For unit vectors, $\angle(x,y)=2\arcsin(\|x-y\|/2)$. Iterating the spherical triangle inequality (Lemma 4.1(a), valid while partial sums stay $\le\pi$; otherwise the claim is trivial since $\angle\le\pi$) gives
$$\angle(b(s),b(s'))\le\sum_i 2\arcsin\!\big(\tfrac{\|b(t_{i+1})-b(t_i)\|}{2}\big)\le N\cdot2\arcsin(\omega h/2)\xrightarrow[h\to0]{}\omega(s'-s),$$
because $2\arcsin(x/2)/x\to1$ and $Nh=s'-s$. Hence $\langle b(s),b(s')\rangle\ge\cos(\omega|s-s'|)$.
(i)⇒(ii). For $\gamma=\angle(b(s),b(s'))$, $\|b(s)-b(s')\|=2\sin(\gamma/2)\le\gamma\le\omega|s-s'|$. So $b$ is $\omega$-Lipschitz in $\mathbb R^3$, hence absolutely continuous and differentiable a.e. with $\|\dot b\|\le\omega$. Its derivative is measurable as an a.e. limit of difference quotients. Differentiating $\|b\|^2=1$ gives $\langle\dot b,b\rangle=0$. Put $\Omega:=b\times\dot b$. Then $\Omega\times b=(b\times\dot b)\times b=\dot b\langle b,b\rangle-b\langle b,\dot b\rangle=\dot b$, $\Omega\perp b$, and $\|\Omega_\perp\|=\|\Omega\|=\|\dot b\|\le\omega$. ∎

So (AL$_\omega$) is exactly the class of thrust-axis motions with transverse body rate at most $\omega$ and arbitrary roll rate. The inner-product form needs no derivatives, which is why it is the definition used for formalization. **Envelope generalization** (used in §6): if $\|\dot b(t)\|\le\kappa(t)$ a.e. with $\kappa\ge0$ integrable, then the same partition argument gives $\angle(b(s),b(s'))\le\int_s^{s'}\kappa$.

### 1.4 Uniform convex relaxations and losslessness
Let $\Theta=\mathbb R^6$ (boundary data) and let $Y$ be any real vector space (lifted variables, discretized controls, slacks, possibly infinite-dimensional).

**Definition 1.3.** A *uniform convex relaxation* is a convex set $C\subseteq\Theta\times Y$. Its slice at $\theta$ is $C_\theta=\{y:(\theta,y)\in C\}$. The relaxed problem at $\theta$ is $\min\{J(\theta,y):y\in C_\theta\}$ for any cost $J$. "Uniform" means one convex set serves all boundary data, with the data entering **jointly convexly**. In all LCvx formulations in the literature, $(r_0,v_0)$ enter through linear equality constraints $x(0)=x_0$ on top of a convex constraint set for the remaining variables, so this holds.

**Definition 1.4.** $C$ is *lossless (feasibility form)* for $F\subseteq\Theta$ if $C_\theta\neq\emptyset\iff\theta\in F$ for every $\theta\in\Theta$. It is *$\varepsilon$-lossless* if $F\subseteq\pi_\Theta(C)\subseteq F^\varepsilon:=\{\theta:\operatorname{dist}(\theta,F)\le\varepsilon\}$.

**Proposition 1.5 (optimization-form LCvx ⇒ feasibility form).** Suppose that (R) for every $\theta\in F$, $C_\theta\ne\emptyset$ (true whenever every original feasible solution maps into $C_\theta$), and that (L) for every $\theta$ with $C_\theta\ne\emptyset$, some point of $C_\theta$ (e.g. an optimizer, when one is attained) certifies a feasible solution of the original problem at $\theta$. Then $C$ is lossless in the feasibility form. *Proof.* (R) gives ⇐ and (L) gives ⇒. ∎
Standard LCvx theorems ("every relaxed optimum is original-feasible") give (L) whenever relaxed optima exist on nonempty slices. A relaxation whose optimum is lossless only for $\theta\in F$, while $C_\theta\neq\emptyset$ for some $\theta\notin F$, fails (L). Such a relaxation would then report false feasibility, which is precisely the failure mode Theorem A forces.

**Reparametrizations.** If the data enter through an affine bijection $\psi:\Theta\to\Theta$, i.e. $C\subseteq\Theta\times Y$ is lossless for $\psi(F)$, then Theorem A gives $\psi(F)$ convex, hence $F$ convex. A *nonlinear* reparametrization $\psi$ is not excluded by Theorem A. All obstructions below concern data entering affinely, as $(r_0,v_0)$ do in every LCvx formulation.

---

## 2. Theorem A

**Theorem A.** If a uniform convex relaxation $C$ is lossless for $F$, then $F=\pi_\Theta(C)$. In particular $F$ is convex.
*Proof.* $\theta\in\pi_\Theta(C)\iff C_\theta\ne\emptyset\iff\theta\in F$. The projection $\pi_\Theta$ is linear, and a linear image of a convex set is convex. ∎

**Corollary A.1.** If $F$ is not convex, no uniform convex relaxation is lossless for $F$, whatever the cost function.
**Corollary A.2.** If $C$ satisfies (R) (i.e. $F\subseteq\pi_\Theta(C)$), then $\pi_\Theta(C)\supseteq\operatorname{conv}F$. So $C$ reports feasibility on all of $\operatorname{conv}F\setminus F$.

---

## 3. Reduction to velocity increments

Define $K=\{(I,J)\}$ and $R=\{I\}$ over all $(T,d,b)\in\mathcal U$ (notation of Lemma 1.1). $R$ is the *velocity-increment set*.

**Lemma 3.1.**
(a) $\theta=(r_0,v_0)\in F_{t_f}$ iff some $(T,d,b)\in\mathcal U$ has $I=-v_0-gt_f$ and $J=-r_0-v_0t_f-\tfrac12gt_f^2$. Equivalently, $F_{t_f}=A^{-1}(K)$ for the affine bijection $A(r_0,v_0)=(-v_0-gt_f,\,-r_0-v_0t_f-\tfrac12gt_f^2)$.
(b) $\pi_{v}(F_{t_f})=-gt_f-R$. Hence if $F_{t_f}$ is convex, then $R$ is convex.
(c) For $P_\pm\in R$ realized by controls $c_\pm$, let $\theta_\pm\in F$ be the data landed by $c_\pm$, and $\theta_M=\frac12(\theta_++\theta_-)$. Then $\theta_M\in\operatorname{conv}F$, its velocity component is $-gt_f-M$ with $M=\frac12(P_++P_-)$, and
$$\operatorname{dist}(\theta_M,F_{t_f})\ \ge\ \operatorname{dist}(M,R).$$
In particular $M\notin R\Rightarrow\theta_M\notin F_{t_f}$, so $F_{t_f}$ is not convex.
*Proof.* (a) follows from Lemma 1.1, since landing means both expressions vanish. (b): $v_0\in\pi_v(F)$ iff $-v_0-gt_f\in R$ (choose $r_0$ from (a)). A linear image of a convex set is convex. (c): the velocity components are affine in the data, so $v_{0,M}=-gt_f-M$. For $\theta=(r_0,v_0)\in F$, $\|\theta-\theta_M\|\ge\|v_0-v_{0,M}\|=\|(-v_0-gt_f)-M\|\ge\operatorname{dist}(M,R)$, because $-v_0-gt_f\in R$. ∎

Gravity enters only through the affine shift $-gt_f$. Only the direction "$\theta\in F\Rightarrow -v_0-gt_f\in R$" is needed for nonconvexity.

---

## 4. Theorem B (rigidity route)

### 4.1 Lemmas

**Lemma 4.1 (spherical triangle inequality, inner-product form, with equality case).** Let $x,y,z\in S^2$, $\alpha,\beta\in[0,\pi]$, $\alpha+\beta\le\pi$, $\langle x,y\rangle\ge\cos\alpha$, $\langle y,z\rangle\ge\cos\beta$.
(a) $\langle x,z\rangle\ge\cos(\alpha+\beta)$.
(b) If moreover $\langle x,z\rangle=\cos(\alpha+\beta)$ and $\alpha+\beta<\pi$, then $\langle x,y\rangle=\cos\alpha$ and $\langle y,z\rangle=\cos\beta$. If in addition $\beta\in(0,\pi)$, then
$$x=\cos\alpha\,y-\frac{\sin\alpha}{\sin\beta}\,\big(z-\cos\beta\,y\big).$$

*Proof.* Write $p=\langle x,y\rangle$, $q=\langle y,z\rangle$, $x'=x-py$, $z'=z-qy$. Then $x',z'\perp y$, $\|x'\|^2=1-p^2$, $\|z'\|^2=1-q^2$, and $\langle x,z\rangle=pq+\langle x',z'\rangle\ge pq-\sqrt{1-p^2}\sqrt{1-q^2}$ by Cauchy–Schwarz. Put $p=\cos a$, $q=\cos c$ with $a,c\in[0,\pi]$; then $\sqrt{1-p^2}=\sin a$, $\sqrt{1-q^2}=\sin c$. Since $\cos$ is decreasing on $[0,\pi]$, $p\ge\cos\alpha$ gives $a\le\alpha$, and likewise $c\le\beta$. So $\langle x,z\rangle\ge\cos a\cos c-\sin a\sin c=\cos(a+c)\ge\cos(\alpha+\beta)$, as $0\le a+c\le\alpha+\beta\le\pi$. This proves (a).
(b) Equality forces equality in both steps. First, $\cos(a+c)=\cos(\alpha+\beta)$ with $a+c\le\alpha+\beta<\pi$; since $\cos$ is strictly decreasing on $[0,\pi]$, $a+c=\alpha+\beta$, and with $a\le\alpha$, $c\le\beta$ this gives $a=\alpha$, $c=\beta$. Second, $\langle x',z'\rangle=-\|x'\|\|z'\|$. If $\beta\in(0,\pi)$ then $\|z'\|=\sin\beta>0$, and for $\lambda=\|x'\|/\|z'\|$ we get $\|x'+\lambda z'\|^2=\|x'\|^2+2\lambda\langle x',z'\rangle+\lambda^2\|z'\|^2=0$. So $x'=-(\sin\alpha/\sin\beta)z'$ and $x=\cos\alpha\,y+x'$. ∎

**Corollary 4.2 (extremal thrust direction).** Let $b,d\in S^2$, $\varphi\in(0,\pi)$, $\delta\in[0,\pi)$ with $\delta+\varphi<\pi$, $\langle d,b\rangle\ge\cos\delta$, $\langle b,e_z\rangle\ge\cos\varphi$. Then $d_z\ge\cos(\delta+\varphi)$. If $d_z=\cos(\delta+\varphi)$, then $b_z=\cos\varphi$, the vector $u:=(b-\cos\varphi\,e_z)/\sin\varphi$ is a horizontal unit vector, $b=\cos\varphi\,e_z+\sin\varphi\,u$, and
$$d=\cos(\delta+\varphi)\,e_z+\sin(\delta+\varphi)\,u .$$
*Proof.* Apply Lemma 4.1 with $x=d$, $y=b$, $z=e_z$, $\alpha=\delta$, $\beta=\varphi$. Then $u_z=(\cos\varphi-\cos\varphi)/\sin\varphi=0$ and $\|u\|^2=(1-2\cos^2\varphi+\cos^2\varphi)/\sin^2\varphi=1$. Moreover $e_z-\cos\varphi\,b=\sin\varphi(\sin\varphi\,e_z-\cos\varphi\,u)$, so Lemma 4.1(b) gives $d=\cos\delta(\cos\varphi e_z+\sin\varphi u)-\sin\delta(\sin\varphi e_z-\cos\varphi u)=\cos(\delta+\varphi)e_z+\sin(\delta+\varphi)u$. ∎

**Lemma 4.3 (mass bound).** For every admissible $T$, $a(s)\ge a_1(s):=\rho_1/(m_0-\alpha\rho_1 s)$ for all $s$. Here $a_1$ is continuous, positive and nondecreasing ($a_1\equiv\rho_1/m_0$ if $\alpha=0$), and it is the acceleration of the constant-minimum-throttle control $T\equiv\rho_1$.
*Proof.* $T\ge\rho_1$ gives $m(s)=m_0-\alpha\int_0^sT\le m_0-\alpha\rho_1s$, and $m(s)>0$ by (H$_m$). Hence $a(s)=T(s)/m(s)\ge\rho_1/m(s)\ge\rho_1/(m_0-\alpha\rho_1s)$. For $T\equiv\rho_1$ both inequalities are equalities. ∎

**Lemma 4.4 (a.e. ⇒ everywhere).** Let $f:[0,t_f]\to\mathbb R$ be continuous with $f=0$ a.e. Then $f\equiv0$.
*Proof.* $U=\{f\ne0\}$ is relatively open in $[0,t_f]$. A nonempty relatively open subset of a nondegenerate interval contains a nondegenerate interval, which has positive measure. So $U=\emptyset$. ∎

**Lemma 4.5 (rigidity).** Let $b(s),b(s')\in S^2$ with $b_z(s)=\cos\psi$, $b_z(s')=\cos\psi'$, $\psi,\psi'\in(0,\pi)$, and suppose $\langle b(s),b(s')\rangle\ge\cos(\psi-\psi')$. Write $b(s)=\cos\psi\,e_z+\sin\psi\,u$ and $b(s')=\cos\psi'\,e_z+\sin\psi'\,u'$ with $u,u'$ horizontal unit vectors. Then $u=u'$.
*Proof.* $\langle b(s),b(s')\rangle=\cos\psi\cos\psi'+\sin\psi\sin\psi'\langle u,u'\rangle$ and $\cos(\psi-\psi')=\cos\psi\cos\psi'+\sin\psi\sin\psi'$. Subtracting gives $\sin\psi\sin\psi'(\langle u,u'\rangle-1)\ge0$. As $\sin\psi\sin\psi'>0$, $\langle u,u'\rangle\ge1$, so $\|u-u'\|^2=2-2\langle u,u'\rangle\le0$. ∎

**Lemma 4.6 (tilt envelope).** Let $(T,d,b)\in\mathcal U$ and set $\varphi_F(s)=\omega s$ and $\varphi_T(s)=\omega\min(s,t_f-s)$. In variant F with $\omega t_f\le\pi$, $b_z(s)\ge\cos\varphi_F(s)$ for all $s$. In variant T with $\omega t_f\le\pi$, $b_z(s)\ge\cos\varphi_T(s)$ for all $s$.
*Proof.* Apply (AL$_\omega$) with $s'=0$, and in variant T also with $s'=t_f$. Since $\cos$ is decreasing on $[0,\pi]$, $\max(\cos\omega s,\cos\omega(t_f-s))=\cos\varphi_T(s)$. ∎

**Lemma 4.7 (extreme arcs are admissible).** Let $\varphi\in\{\varphi_F,\varphi_T\}$ with $\delta+\max\varphi\le\pi$, and let $u$ be any horizontal unit vector. Put $b_u(s)=\cos\varphi(s)e_z+\sin\varphi(s)u$, $d_u(s)=\cos(\delta+\varphi(s))e_z+\sin(\delta+\varphi(s))u$, $T\equiv\rho_1$. This triple is admissible in the corresponding variant, and its increment is
$$P_u=\Big(\int_0^{t_f}a_1\sin(\delta+\varphi)\Big)u+\Big(\int_0^{t_f}a_1\cos(\delta+\varphi)\Big)e_z .$$
*Proof.* $b_u$ is continuous, with $b_u(0)=e_z$ and, in variant T, $b_u(t_f)=e_z$. Next, $\langle b_u(s),b_u(s')\rangle=\cos(\varphi(s)-\varphi(s'))$, and $|\varphi(s)-\varphi(s')|\le\omega|s-s'|$ because $\varphi$ is $\omega$-Lipschitz. When $\omega|s-s'|\le\pi$, monotonicity of $\cos$ on $[0,\pi]$ gives (AL$_\omega$). Finally $\langle d_u,b_u\rangle=\cos\delta$, and $a=a_1$ by Lemma 4.3. ∎

### 4.2 Statement and proof

**Theorem B.** Assume $\rho_1>0$, $\omega>0$, $\delta\in[0,\pi/2)$, (H$_m$), and either
- **(F)** $b(t_f)$ free and $\delta+\omega t_f\le\pi/2$, with $\varphi=\varphi_F$; or
- **(T)** $b(t_f)=e_z$ and $\delta+\omega t_f/2\le\pi/2$, with $\varphi=\varphi_T$.

Let $M=\tfrac12(P_u+P_{-u})=\big(\int_0^{t_f}a_1\cos(\delta+\varphi)\big)e_z$. Then $M\in\operatorname{conv}R\setminus R$. Consequently $R$ and $F_{t_f}$ are nonconvex, and by Theorem A **no uniform convex relaxation is lossless**. Explicitly, $\theta_\pm\in F$ and $\theta_M\notin F$ (Lemma 3.1(c)). The same conclusion holds for any $b_0\in S^2$, after replacing $e_z$ by $b_0$ throughout, and for any $g$.

*Proof.* By Lemma 4.7, $P_{\pm u}\in R$, so $M\in\operatorname{conv}R$. Suppose $M=I=\int_0^{t_f}a\,d$ for some $(T,d,b)\in\mathcal U$. In both variants $\omega t_f\le\pi$ and $0\le\delta+\varphi(s)\le\pi/2$.

*Step 1 (pointwise vertical bound).* By Lemma 4.6 and Lemma 4.1(a), with $\alpha=\delta$, $\beta=\varphi(s)$, $\alpha+\beta\le\pi/2$: $d_z(s)\ge\cos(\delta+\varphi(s))\ge0$ for a.e. $s$. With Lemma 4.3,
$$a(s)d_z(s)\ \ge\ a_1(s)d_z(s)\ \ge\ a_1(s)\cos(\delta+\varphi(s))\qquad\text{a.e.}\tag{4.1}$$

*Step 2 (equality a.e.).* Integrating, $I_z\ge\int a_1\cos(\delta+\varphi)=M_z$. Since $I_z=M_z$, the nonnegative integrable function $a d_z-a_1\cos(\delta+\varphi)$ has integral zero and so vanishes a.e. Both inequalities in (4.1) are then equalities a.e. Since $a_1>0$, the second one gives $d_z(s)=\cos(\delta+\varphi(s))$ a.e. Let $E\subseteq(0,t_f)$ be the full-measure set where this and the gimbal condition hold.

*Step 3 (equality in the triangle inequality).* For $s\in E$ we have $\varphi(s)\in(0,\pi/2]$ and $\delta+\varphi(s)\le\pi/2<\pi$. Corollary 4.2 gives $b_z(s)=\cos\varphi(s)$, and with $u(s):=(b(s)-\cos\varphi(s)e_z)/\sin\varphi(s)$,
$$d(s)=\cos(\delta+\varphi(s))e_z+\sin(\delta+\varphi(s))u(s)\qquad(s\in E).\tag{4.2}$$

*Step 4 (a.e. ⇒ everywhere).* $f(s)=b_z(s)-\cos\varphi(s)$ is continuous and vanishes on $E$, so by Lemma 4.4, $b_z=\cos\varphi$ on $[0,t_f]$. Hence $u(s)$ is defined and continuous on $(0,t_f)$ (on $(0,t_f]$ in variant F).

*Step 5 (rigidity).* (F): for $0<s<s'\le t_f$, (AL$_\omega$) gives $\langle b(s),b(s')\rangle\ge\cos(\omega(s'-s))=\cos(\varphi(s')-\varphi(s))$, with $\varphi\in(0,\pi/2]\subset(0,\pi)$. Lemma 4.5 gives $u(s)=u(s')$. (T): the same argument works for pairs in $(0,t_f/2]$, where $\varphi(s')-\varphi(s)=\omega(s'-s)$, and for pairs in $[t_f/2,t_f)$, where $\varphi(s)-\varphi(s')=\omega(s'-s)$. Both pieces contain $t_f/2$, so $u(s)=u(t_f/2)$ for all $s\in(0,t_f)$. In both variants $u\equiv u_0$ is constant.

*Step 6 (lateral contradiction).* By (4.2), $I_h=\int_E a(s)\sin(\delta+\varphi(s))\,ds\;u_0$. The scalar factor is $\ge\int_0^{t_f}a_1\sin(\delta+\varphi)>0$, because $a\ge a_1>0$ and $\delta+\varphi(s)\in(0,\pi/2]$ for $s\in(0,t_f)$. But $M_h=0$, a contradiction. ∎

**Parameter regime covered by Theorem B.** $0<\rho_1\le\rho_2$; $\alpha\ge0$ with (H$_m$); $0<\omega<\infty$; $0\le\delta<\pi/2$; any $g$, $m_0$, $b_0$; (F) $\delta+\omega t_f\le\pi/2$ or (T) $\delta+\omega t_f/2\le\pi/2$. Thm Q extends (F) to $\delta+\omega t_f/2\le\pi/2$. §7 extends (F) to all $t_f$ and (T) to $\delta+\omega t_f/2\le\pi$.

*Remark (Lean-friendly variant of Steps 4–5).* Continuity in Step 4 can be avoided in variant F. For any $s,s'\in E$, Step 5 applies directly, since both points have $b_z=\cos\varphi$ by Step 3. Then $u$ is constant on $E$, which suffices for Step 6. In variant T, pairs straddling $t_f/2$ need a common good point on both monotone pieces, which only $t_f/2$ is. So either use continuity (Step 4), or note that $u$ is constant on $E\cap(0,t_f/2]$ and on $E\cap[t_f/2,t_f)$ and is continuous at $t_f/2$.

---

## 5. Quantitative gap: the ball bound

### 5.1 The support inequality
**Lemma 5.1 (support bound).** Let $(T,d,b)$ satisfy items 1–4 of §1.2 (no boundary condition on $b$ is needed). Let $\tau\in[0,t_f]$ satisfy $\delta+\omega\max(\tau,t_f-\tau)\le\pi/2$, and set $c=b(\tau)$. Then
$$\|I\|\ \ge\ \langle I,b(\tau)\rangle\ \ge\ G(\tau):=\int_0^{t_f}a_1(s)\cos\big(\delta+\omega|s-\tau|\big)\,ds .$$
*Proof.* For a.e. $s$, $\langle d(s),b(s)\rangle\ge\cos\delta$ and, by (AL$_\omega$), $\langle b(s),c\rangle\ge\cos(\omega|s-\tau|)$. Lemma 4.1(a) gives $\langle d(s),c\rangle\ge\cos(\delta+\omega|s-\tau|)\ge0$. Lemma 4.3 then gives $a\langle d,c\rangle\ge a_1\cos(\delta+\omega|s-\tau|)$. Integrate, and use $\langle I,c\rangle=\int a\langle d,c\rangle$ (linearity of the Bochner integral) and $\langle I,c\rangle\le\|I\|\|c\|=\|I\|$. ∎

So **$R$ avoids the open ball $B(0,\sup_\tau G(\tau))$**, and every $I\in R$ has $\langle I,b(\tau)\rangle\ge G(\tau)$ for its own $b(\tau)$.

### 5.2 Variant F
**Theorem Q (explicit gap, free terminal attitude).** Assume $\rho_1>0$, $\omega>0$, $\delta\ge0$, (H$_m$), $b(0)=e_z$, $b(t_f)$ free, and
$$\delta+\omega t_f/2\le\pi/2,\qquad M_z:=\int_0^{t_f}a_1(s)\cos(\delta+\omega s)\,ds\ \ge 0 .\tag{5.1}$$
The sign condition holds automatically if $\alpha=0$ or if $\delta+\omega t_f\le\pi/2$. Let $M=M_ze_z$ be the midpoint of the arcs of Lemma 4.7 with $\varphi=\varphi_F$; these arcs are admissible because $\delta+\omega t_f\le\pi-\delta\le\pi$. Then
$$\operatorname{dist}(M,R)\ \ge\ G(t_f/2)-M_z\ \ge\ \Gamma_F:=\frac{4\,a_1(t_f/4)}{\omega}\,\sin\!\Big(\delta+\frac{\omega t_f}{2}\Big)\sin^2\!\Big(\frac{\omega t_f}{4}\Big)>0,$$
with equality in the second inequality when $\alpha=0$. Hence $\operatorname{dist}(\theta_M,F_{t_f})\ge\Gamma_F$ and $F_{t_f}$ is nonconvex.

*Proof.* For $I\in R$, $\|I-M\|\ge\|I\|-\|M\|\ge G(t_f/2)-M_z$ by Lemma 5.1 with $\tau=t_f/2$. Write $c(x)=\cos(\delta+\omega x)$, strictly decreasing on $[0,t_f]$ because $\delta+\omega t_f\le\pi$. Put $h(s)=c(|s-t_f/2|)-c(s)$. For $s\ge t_f/4$ we have $|s-t_f/2|\le s$, so $h\ge0$; for $s<t_f/4$, $h<0$. Since $a_1$ is nondecreasing, $(a_1(s)-a_1(t_f/4))h(s)\ge0$ for all $s$ (Chebyshev). Hence
$$G(t_f/2)-M_z=\int a_1h\ \ge\ a_1(t_f/4)\int_0^{t_f}h .$$
Next, $\int_0^{t_f}c(|s-t_f/2|)ds=2\int_0^{t_f/2}c=\frac2\omega(\sin(\delta+\frac{\omega t_f}2)-\sin\delta)$ and $\int_0^{t_f}c=\frac1\omega(\sin(\delta+\omega t_f)-\sin\delta)$. Using $\sin x+\sin(x+2k)=2\sin(x+k)\cos k$ with $x=\delta$, $k=\omega t_f/2$,
$$\int_0^{t_f}h=\frac{2}{\omega}\sin\!\Big(\delta+\frac{\omega t_f}{2}\Big)\Big(1-\cos\frac{\omega t_f}{2}\Big)=\frac4\omega\sin\!\Big(\delta+\frac{\omega t_f}2\Big)\sin^2\frac{\omega t_f}4>0 ,$$
since $\delta+\omega t_f/2\in(0,\pi/2]$. Sign condition: if $\delta+\omega t_f\le\pi/2$ the integrand of $M_z$ is $\ge0$. If $\alpha=0$, $M_z=\frac{a_1}{\omega}(\sin(\delta+\omega t_f)-\sin\delta)\ge0$, because $\delta\le\delta+\omega t_f\le\pi-\delta$. The last statement follows from Lemma 3.1(c). ∎

*Without the sign condition*, the proof gives $\operatorname{dist}(M,R)\ge G(t_f/2)-|M_z|$, which is positive iff $G(t_f/2)+M_z>0$.

*Asymptotics.* For small $\omega t_f$, $\Gamma_F\approx\frac14a_1\omega t_f^2\sin\delta$ if $\delta>0$, and $\Gamma_F\approx\frac18a_1\omega^2t_f^3$ if $\delta=0$. The gap vanishes as $\omega\to0$ (fixed attitude, which is 3DOF with a pointing cone, where LCvx works). It is linear in $\omega$ when $\delta>0$.

*Numbers* (`numerics/proof/gap_check.py`; $\rho_1=400$ N, $m_0=80$ kg, $\alpha=5.66\cdot10^{-4}$ s/m, $\delta=15^\circ$):

| $\omega$ [rad/s] | $t_f$ [s] | $G(t_f/2)$ | $M_z$ | gap $G-M_z$ | $\Gamma_F$ |
|---|---|---|---|---|---|
| 0.3 | 5 | 19.77 | 12.10 | 7.67 m/s | 7.61 m/s |
| 0.5 | 5 | 14.89 | 1.06 | 13.83 m/s | 13.72 m/s |
| 0.3 | 8.5 | 24.99 | 0.91 | 24.08 m/s | 23.75 m/s |

In 300 random admissible discretized trajectories per row, $\|I\|\ge G(t_f/2)$ always held, as it must.

### 5.3 Variant T
For the tent variant with $\alpha=0$, $G(t_f/2)=M_z$, so the plain ball bound gives only $M\notin\operatorname{int}$. Refine it with two reference directions.

**Theorem Q_T.** Assume variant T, $\rho_1>0$, $\omega>0$, (H$_m$), and $\delta+\omega t_f/2\le\pi/2$. Put $\varphi=\varphi_T$, $M=M_ze_z$ with $M_z=\int a_1\cos(\delta+\varphi)$, and for $0\le\lambda\le\beta\le\omega t_f/2$
$$A_{\lambda,\beta}(s)=\min\big(\varphi(s)+\lambda,\ \omega|s-t_f/2|+\beta-\lambda\big),\qquad H(\lambda,\beta)=\int_0^{t_f}a_1\cos(\delta+A_{\lambda,\beta}),$$
$$Q(\beta)=\max_{\lambda\in[0,\beta]}\big[H(\lambda,\beta)-M_z\cos\lambda\big],\qquad \gamma_T=\min_{\beta\in[0,\omega t_f/2]}Q(\beta).$$
Then $\operatorname{dist}(M,R)\ge\gamma_T$. Moreover:
(i) if $\alpha=0$, then $\gamma_T\ge\min\big(\kappa/2,\ M_z(1-\cos\frac{\kappa}{2A_1})\big)>0$, where $A_1=\int_0^{t_f}a_1=a_1t_f$ and $\kappa=H(0,0)-M_z=\frac{8a_1}{\omega}\sin(\delta+\frac{\omega t_f}4)\sin^2\frac{\omega t_f}8$;
(ii) for $\alpha>0$, $\gamma_T$ is an explicit one-dimensional min–max of explicit integrals. Since it depends continuously on $\alpha$, $\gamma_T>0$ for all sufficiently small $\alpha$. Numerically, $\gamma_T>0$ in every case tested, including $\alpha$ fifty times the GTPL value (table below).

*Proof.* Let $I\in R$ come from $(T,d,b)$. Let $c=b(t_f/2)$ and $\beta=\angle(c,e_z)\le\omega t_f/2$ (Lemma 4.6). For $\lambda\in[0,\beta]$ let $v_\lambda$ be the point of the minor great-circle arc from $e_z$ to $c$ with $\angle(e_z,v_\lambda)=\lambda$ and $\angle(v_\lambda,c)=\beta-\lambda$ ($v_\lambda=e_z$ if $\beta=0$). By the angle triangle inequality (Lemma 4.1(a) in angle form), $\angle(b(s),v_\lambda)\le\min(\angle(b(s),e_z)+\lambda,\ \angle(b(s),c)+\beta-\lambda)\le A_{\lambda,\beta}(s)$. Since $\varphi(s)+\omega|s-t_f/2|=\omega t_f/2$ for all $s$, $A_{\lambda,\beta}\le\frac12(\omega t_f/2+\beta)\le\omega t_f/2$, so $\delta+A\le\pi/2$. As in Lemma 5.1, $\langle I,v_\lambda\rangle\ge H(\lambda,\beta)$. Also $\langle M,v_\lambda\rangle=M_z\cos\lambda$. Hence $\|I-M\|\ge\langle I-M,v_\lambda\rangle\ge H(\lambda,\beta)-M_z\cos\lambda$ for every $\lambda$, so $\|I-M\|\ge Q(\beta)\ge\gamma_T$.
(i) Take $\lambda\in\{0,\beta\}$. *Case $\lambda=\beta$:* $A_{\beta,\beta}\le\omega|s-t_f/2|$, so $H(\beta,\beta)\ge G(t_f/2)=M_z$. The equality uses $\alpha=0$ and the symmetry $\int_0^{t_f}c(|s-t_f/2|)=2\int_0^{t_f/2}c=\int_0^{t_f}c(\varphi_T)$. Hence $Q(\beta)\ge M_z(1-\cos\beta)$. *Case $\lambda=0$:* $|\cos x-\cos y|\le|x-y|$ and $|A_{0,\beta}-A_{0,0}|\le\beta$ give $H(0,\beta)\ge H(0,0)-\beta A_1$, so $Q(\beta)\ge\kappa-\beta A_1$. Here $A_{0,0}(s)=\omega\min(s,|s-t_f/2|,t_f-s)$, a double tent with peaks $\omega t_f/4$, so $H(0,0)=\frac{4a_1}\omega(\sin(\delta+\frac{\omega t_f}4)-\sin\delta)$. Also $M_z=\frac{2a_1}\omega(\sin(\delta+\frac{\omega t_f}2)-\sin\delta)$. The identity of §5.2 with $k=\omega t_f/4$ gives the stated $\kappa>0$. If $\beta\le\kappa/(2A_1)$ then $Q\ge\kappa/2$; otherwise $Q\ge M_z(1-\cos\frac{\kappa}{2A_1})$. Finally $M_z>0$. ∎

| $(t_f,\omega,\delta,\alpha)$ | $\gamma_T$ (numerical) | $M_z$ |
|---|---|---|
| (6, 0.3, 15°, 0) | 3.24 | 21.96 |
| (6, 0.3, 15°, 5.66e-4) | 3.27 | 22.15 |
| (6, 0.3, 15°, 0.03) | 3.85 | 59.78 |
| (10, 0.3, 15°, 5.66e-4) | 10.77 | 24.45 |

(units m/s; $\rho_1=400$ N, $m_0=80$ kg.) The qualitative statement $M\notin R$ holds for **all** $\alpha$ by Theorem B(T). Only the explicit lower bound is conditional for $\alpha>0$.

### 5.4 Consequences for relaxations
**Corollary 5.2 (no ε-lossless uniform relaxation).** In the setting of Theorem Q (resp. Q_T), no uniform convex relaxation is $\varepsilon$-lossless (Def. 1.4, Euclidean norm on $\mathbb R^6$) for $\varepsilon<\Gamma_F$ (resp. $\gamma_T$).
*Proof.* $\pi_\Theta(C)$ is convex and contains $F$, hence contains $\theta_M$. So $\operatorname{dist}(\theta_M,F)\le\varepsilon$. Lemma 3.1(c) and Thm Q give $\operatorname{dist}(\theta_M,F)\ge\Gamma_F$. ∎
Any norm on $\Theta$ that dominates the $v_0$-norm gives the same bound. For a weighted norm $\|(\Delta r,\Delta v)\|_W\ge w_v\|\Delta v\|$, the bound is $w_v\Gamma_F$.

**Proposition 5.3 (sketch: false feasibility on a set of positive measure).** If $\operatorname{int}F_{t_f}\ne\emptyset$, then $\operatorname{conv}F\setminus F$ contains a nonempty open set. So a uniform convex relaxation containing $F$ is wrong on a set of positive Lebesgue measure, and "lossless for a.e. $\theta$" is also impossible.
*Proof.* $\operatorname{conv}F$ is convex with nonempty interior, so interior points $\theta'$ exist with $\|\theta'-\theta_M\|<\Gamma/2$, and some ball $B(\theta',r)\subseteq\operatorname{conv}F$ with $r<\Gamma/2$. Every point of that ball is at distance $>0$ from $F$. ∎
*Sketch that $\operatorname{int}K\neq\emptyset$ (not fully written):* hold $b$ at a fixed tilt-free motion and perturb $d$ inside the open gimbal cone and $T$ inside $(\rho_1,\rho_2)$. The linear map $u\mapsto(\int u,\int(t_f-s)u)$ is onto $\mathbb R^6$, and the inverse function theorem in finitely many parameters applies. If $\rho_1=\rho_2$, use a time-varying base direction. Marked **sketch**.

---

## 6. Second-order attitude dynamics (M3) and 6DOF (M4)

### 6.1 Angle-envelope classes
Let $\Psi:[0,t_f]\to[0,\infty)$ be continuous and nondecreasing, with $\Psi(0)=0$ and $\Psi(s)>0$ for $s>0$. Define
$$\mathcal B(\Psi)=\{b\in C([0,t_f];S^2):\ b(0)=e_z,\ \langle b(s),b(s')\rangle\ge\cos(\Psi(s')-\Psi(s))\ \ \forall s\le s'\text{ with }\Psi(s')-\Psi(s)\le\pi\},$$
and the *planar max-tilt arcs* $b^\Psi_u(s)=\cos\Psi(s)e_z+\sin\Psi(s)u$ for horizontal unit vectors $u$, assuming $\Psi\le\pi$. M1 is $\mathcal B(\omega s)$.

**Theorem E (sandwich principle).** Consider a model whose thrust, gimbal and mass constraints are those of M1. Assume its set $\mathcal B$ of realizable body-axis curves satisfies
$$\{b^\Psi_u: u\text{ horizontal unit}\}\ \subseteq\ \mathcal B\ \subseteq\ \mathcal B(\Psi)$$
(free terminal attitude). Let $M^\Psi=\big(\int a_1\cos(\delta+\Psi)\big)e_z$. Then:
(i) if $\delta+\Psi(t_f)\le\pi/2$: $M^\Psi\in\operatorname{conv}R\setminus R$, so $F_{t_f}$ is nonconvex and no uniform convex relaxation is lossless;
(ii) if $\delta+\Psi(t_f)<\pi$: $F_{t_f}$ is nonconvex (by the argument of Thm L, §7, with $\cos(\delta+\Psi)$ in place of $\cos\psi_d$);
(iii) quantitative: if $\delta+\max_s|\Psi(s)-\Psi(\tau)|\le\pi/2$ and $M^\Psi_z\ge0$, then $\operatorname{dist}(M^\Psi,R)\ge G_\Psi(\tau)-M^\Psi_z$ with $G_\Psi(\tau)=\int a_1\cos(\delta+|\Psi(s)-\Psi(\tau)|)$. For $x_0=\Psi(\tau)$,
$$G_\Psi(\tau)-G_\Psi(0)\ \ge\ x_0\Big[\int_\tau^{t_f}a_1\sin(\delta+\Psi(s)-x_0)\,ds-\sin(\delta+x_0)\int_0^\tau a_1\Big],$$
which is $>0$ for all small $\tau>0$ since the bracket tends to $\int a_1\sin(\delta+\Psi)>0$. Note $G_\Psi(0)=M^\Psi_z$.

*Proof.* (i): this is the proof of Theorem B(F) verbatim, with $\varphi=\Psi$. Lemma 4.6 becomes $b_z(s)\ge\cos\Psi(s)$, from $s=0$. Rigidity (Lemma 4.5) for $s<s'$ uses $\langle b(s),b(s')\rangle\ge\cos(\Psi(s')-\Psi(s))$, which is exactly the class inequality; $\Psi(s)>0$ for $s>0$ provides $\sin\Psi>0$. (ii): §7. (iii): Lemma 5.1 with the class inequality in place of (AL$_\omega$) gives $\|I\|\ge G_\Psi(\tau)$. For the lower bound, split the integrand $c(|\Psi(s)-x_0|)-c(\Psi(s))$ (with $c(x)=\cos(\delta+x)$) at $\Psi(s)\ge x_0$, where it is $\ge x_0\sin(\delta+\Psi(s)-x_0)$ by the mean value theorem, and $\Psi(s)<x_0$ (i.e. $s<\tau$), where it is $\ge c(x_0)-c(0)\ge-x_0\sin(\delta+x_0)$. ∎

**Corollary E.1 (combined rate and torque limits, kinematic part).** If the body-axis speed satisfies an a-priori bound $\|\dot b(t)\|\le\kappa(t)$, and the maximal profile is realizable along every fixed horizontal rotation axis, then $\Psi=\int_0^\cdot\kappa$ satisfies the sandwich (Prop. 1.2, envelope form). Examples: $\kappa=\omega$ (M1); $\kappa(t)=\varepsilon t$ (torque limit from rest); $\kappa(t)=\min(\varepsilon t,\omega)$ (torque and rate limit from rest: accelerate at the torque limit until reaching the rate limit, then hold).

### 6.2 M3a: torque-limited rigid body with independent transverse torque
**Model M3a.** Attitude $\mathsf R\in SO(3)$ (or a unit quaternion $q$ with $\mathsf R=\mathsf R(q)$), body axis $b=\mathsf Re_3$, kinematics $\dot{\mathsf R}=\mathsf R[\Omega]_\times$. Euler dynamics $J\dot\Omega+\Omega\times J\Omega=\tau$ with **axisymmetric** $J=\operatorname{diag}(J_t,J_t,J_a)$. Measurable torque with transverse part $\|\tau_\perp\|=\|(\tau_1,\tau_2)\|\le\tau_t$ (pitch/yaw actuators independent of the main engine, e.g. RCS or vanes) and roll torque $|\tau_3|\le\tau_a$, $\tau_a\ge0$ arbitrary. Initial conditions $\mathsf R(0)=\mathsf R_0$ with $\mathsf R_0e_3=e_z$, and **$\Omega(0)=0$**. Final attitude and rate are free. Thrust, gimbal ($\langle d,b\rangle\ge\cos\delta$) and mass are as in M1.

**Proposition 6.1.** Let $\varepsilon=\tau_t/J_t$ and $\Psi(s)=\varepsilon s^2/2$. The M3a body-axis curves satisfy the sandwich of Theorem E:
(a) every realizable $b$ satisfies $\|\dot b(t)\|\le\varepsilon t$, hence $b\in\mathcal B(\Psi)$;
(b) for every horizontal $u$, $b^\Psi_u$ is realized by $\Omega(t)=\varepsilon t\,k_B$ and $\tau=J_t\varepsilon k_B$, with $k_B=\mathsf R_0^{\top}(e_z\times u)$ and zero roll.

*Proof.* (a) $\dot b=\mathsf R(\Omega\times e_3)$, so $\|\dot b\|=\|\Omega_\perp\|$ with $\Omega_\perp=(\Omega_1,\Omega_2)$. Axisymmetric Euler equations: $J_t\dot\Omega_1=\tau_1-(J_a-J_t)\Omega_2\Omega_3$ and $J_t\dot\Omega_2=\tau_2+(J_a-J_t)\Omega_1\Omega_3$. Hence $\frac{d}{dt}\frac12\|\Omega_\perp\|^2=\langle\Omega_\perp,\tau_\perp\rangle/J_t$: the gyroscopic terms cancel, so roll does not matter. With $N=\|\Omega_\perp\|^2$ and $\eta>0$, $\frac{d}{dt}\sqrt{N+\eta}=\frac{\langle\Omega_\perp,\tau_\perp\rangle}{J_t\sqrt{N+\eta}}\le\varepsilon$, so $\sqrt{N(t)+\eta}\le\sqrt\eta+\varepsilon t$. Let $\eta\to0$. Then apply Prop. 1.2 (envelope form): $\angle(b(s),b(s'))\le\int_s^{s'}\varepsilon t\,dt=\Psi(s')-\Psi(s)$.
(b) $k_B\perp e_3$ because $\mathsf R_0e_3=e_z\perp e_z\times u$. Every transverse vector is a principal axis of $J$, so $\Omega\times J\Omega=0$ and $J\dot\Omega=J_t\varepsilon k_B=\tau$, with $\|\tau_\perp\|=\tau_t$ and $\tau_3=0$. The attitude is the rotation about the fixed inertial axis $k=e_z\times u$ by angle $\Psi(t)$, so $b(t)=\cos\Psi\,e_z+\sin\Psi\,(k\times e_z)=b^\Psi_u(t)$, because $(e_z\times u)\times e_z=u$. ∎

Hence Theorem E applies to M3a (free terminal attitude), with regimes $\delta+\varepsilon t_f^2/2\le\pi/2$ (rigidity, explicit midpoint) and $<\pi$ (§7). The same holds with an additional rate limit, using $\kappa=\min(\varepsilon t,\omega)$.

**What is not covered in M3 (precisely):**
- $\Omega_\perp(0)\ne0$. The envelope $\|\Omega_\perp(0)\|t+\varepsilon t^2/2$ is achieved only in the direction of the initial rate, so the symmetric pair $\pm u$ is lost. Open.
- Prescribed terminal attitude $b(t_f)=e_z$ (with or without $\Omega(t_f)=0$). The pointwise envelope $\min(\Psi_{fwd},\Psi_{bwd})$ is not achieved by a single trajectory under second-order dynamics. Moreover, non-planar (spiralling) curves can reach tilt profiles that planar curves cannot, since centripetal terms enter $\ddot\theta$. Rigidity of minimizers is therefore unproven. **Conjecture.**
- Non-axisymmetric $J$: the energy bound $\sqrt{\Omega^\top J\Omega}(t)\le\tau_{\max}t/\sqrt{J_{\min}}$ gives a valid envelope, but it need not be tight. Open.
- Agreement: [adversary] item 2 on `comms/threads/6dof-models.md` derived the same envelope independently.

### 6.3 M4: 6DOF
**Model M4.** State $(r,v,m,\mathsf R,\Omega)$ (or a quaternion). Thrust direction is constrained relative to the body, $\langle d,\mathsf Re_3\rangle\ge\cos\delta$. Roll is commanded by RCS. Two attitude-actuation sub-models:
- **M4-kin** (rate as control): $\Omega$ measurable with $\|\Omega_\perp\|\le\omega$ (or $\|\Omega\|\le\omega$) and $|\Omega_3|\le\omega_r$ for any $\omega_r\ge0$. $\mathsf R(0)=\mathsf R_0$, and $\mathsf R(t_f)$ is free, or $\mathsf R(t_f)e_3=e_z$, or $\mathsf R(t_f)=\mathsf R_0$.
- **M4-dyn** (torque as control): as M3a, i.e. axisymmetric, transverse torque independent of thrust, $\Omega(0)=0$, terminal attitude free.

**Theorem 6.2 (transfer to 6DOF).** Let $\pi_5:(\mathsf R,\Omega,T,d)\mapsto(b=\mathsf Re_3,T,d)$.
(a) $\pi_5(\mathcal U_{M4\text{-kin}})\subseteq\mathcal U_{M1}$, with the same $\omega$ and in the matching attitude-boundary variant. Also $\pi_5(\mathcal U_{M4\text{-dyn}})\subseteq\mathcal U_{\mathcal B(\varepsilon s^2/2)}$.
(b) The witness arcs lift. M1 extreme arcs (both variants) lift to M4-kin via $\Omega(t)=\pm\omega k_B$ with $k_B=\mathsf R_0^\top(e_z\times u)$; the sign is $+$ on $[0,t_f]$ in variant F, and $+$ then $-$ (switching at $t_f/2$) in variant T. Zero roll is used. In variant T the attitude returns to $\mathsf R(t_f)=\mathsf R_0$ **exactly**, since it is a rotation about one fixed axis by $\varphi_T(t_f)=0$. M3a arcs lift to M4-dyn by Prop. 6.1(b).
(c) Hence $R_{6}\subseteq R_{5}$, and $P_{\pm u}\in R_6$. So $M\in\operatorname{conv}R_6\setminus R_6$, and $\operatorname{dist}(M,R_6)\ge\operatorname{dist}(M,R_5)$. With fixed attitude data, $F^{6DOF}_{t_f}\subseteq\mathbb R^6$ is nonconvex in the regimes of Theorems B, Q, Q_T, L, L_T (M4-kin) and Theorem E (M4-dyn). No uniform convex relaxation of the 6DOF problem is lossless.
*Proof.* (a) $b=\mathsf Re_3$ satisfies $\dot b=\mathsf R(\Omega\times e_3)$, so $\|\dot b\|=\|\Omega_\perp\|\le\omega$; then apply Prop. 1.2. The gimbal constraint is identical. The translational dynamics depend on attitude only through $d$, and the attitude data $\mathsf R(0)=\mathsf R_0$ give $b(0)=e_z$. (b) is a direct check, as in Prop. 6.1(b). (c): the increment of a 6DOF control equals the increment of its projection, so $R_6=R_5(\pi_5(\mathcal U_6))\subseteq R_5$, and the lifted witnesses lie in $R_6$. ∎

*Caveats.* (1) If $\Omega$ is a *state* (torque control), the instantaneous rate $\omega$ at $t=0^+$ in the M1 arc is not realizable. That is why M4-dyn uses the envelope $\varepsilon s^2/2$, not $\omega s$ (cf. [adversary] item 1). (2) **Box gimbal** ($\pm\delta$ per axis, as on GTPL). Per [adversary-6dof], the kinematic proof goes through with $\delta$ replaced by the corner angle of the box ($\approx21^\circ$ for $\pm15^\circ$; the exact value depends on the gimbal parametrization, e.g. $\arccos(1/\sqrt{1+2\tan^2\delta})$ for independent tangent deflections), $u$ restricted to the diagonals, and only $\pi$-rotation symmetry used. I have not re-derived this; cite their report. (3) Aerodynamic or CoM-offset couplings are not modeled.

### 6.4 M3b: gimbal-generated torque (the physically relevant case for GTPL), open
If pitch/yaw torque is produced by the gimbal itself, $\tau_\perp=-\ell T\,(b\times d)$ (body frame), then deflecting $d$ beyond $b$ toward $u$ accelerates $b$ toward $-u$. So the M1/M3a extreme arcs, with $d$ tilted further than $b$ in the same azimuth, are **not realizable**, and Theorem E does not apply. The structural ingredients that survive are:
- the rotational symmetry about $e_z$, when the initial state is axisymmetric ($b(0)=e_z$, $\Omega(0)=0$). Hence $R$ is invariant under rotations about $e_z$;
- an a-priori envelope $\|\dot b\|\le(\ell\rho_2\sin\delta/J_t)t$, which gives Lemma 5.1 with $\Psi=\ell\rho_2\sin\delta\,t^2/(2J_t)$.

**Lemma 6.3 (axis test, for any rotation-invariant $R$).** If $R$ is invariant under rotation by $\pi$ about $e_z$, then $R$ is nonconvex as soon as $\min_{I\in R}I_z<\inf\{I_z: I\in R,\ I_h=0\}$. Also, if $\|I\|\ge G$ on $R$ and some $P\in R$ has $|P_z|<G$, then $R$ is nonconvex.
*Proof.* For $P\in R$, the rotated copy $P'$ is in $R$ and $\frac12(P+P')=P_ze_z$. ∎

**Lemma 6.4 (center-of-percussion flat output; orchestrator's suggestion, verified here).** Pure TVC, axisymmetric $J=\operatorname{diag}(J_t,J_t,J_a)$, gimbal point at $r-Lb$, $d=\cos\mu\,b+\sin\mu\,n$ with $n\perp b$ a unit vector, gimbal torque $\tau=-LT\,b\times d$, an RCS roll torque along $b$, and $r=\langle\Omega,b\rangle$ (roll rate), $\Omega_\perp=\Omega-rb$ (inertial frame). Then
$$\ddot b=-\frac{LT\sin\mu}{J_t}\,n-\|\Omega_\perp\|^2b+\frac{J_a}{J_t}\,r\,\Omega_\perp ,$$
and the point $y=r_{cm}+k\,b$ with $k=J_t/(mL)$ satisfies
$$\ddot y=\Big(\frac{T\cos\mu}{m}-k\|\Omega_\perp\|^2\Big)b+g+\frac{J_a}{mL}\,r\,\Omega_\perp .$$
**With zero roll rate ($r\equiv0$, RCS holds roll), the lateral gimbal force cancels exactly**, and $y$ is driven by a thrust *along $b$* (effective gimbal $\delta_{\rm eff}=0$) with magnitude $T\cos\mu/m-k\|\Omega_\perp\|^2$. The body axis has $\|\dot\Omega_\perp\|\le LT\sin|\mu|/J_t$.
*Proof.* Angular momentum $H=J_t\Omega+(J_a-J_t)rb$, and $\dot H=\tau+\tau_rb$, so $J_t\dot\Omega=\tau+\tau_rb-(J_a-J_t)(\dot rb+r\dot b)$. Next, $\dot b=\Omega_\perp\times b$, and $\ddot b=\dot\Omega\times b+\Omega\times\dot b$. Using $\Omega\times\dot b=-\|\Omega_\perp\|^2b+r\Omega_\perp$, $\dot b\times b=-\Omega_\perp$ and $(b\times d)\times b=\sin\mu\,n$, we get $\dot\Omega\times b=-\frac{LT\sin\mu}{J_t}n+\frac{(J_a-J_t)r}{J_t}\Omega_\perp$, and summing gives the formula for $\ddot b$. Then $\ddot y=\frac Tm(\cos\mu\,b+\sin\mu\,n)+g+k\ddot b$, and the $n$-terms cancel because $kLT/J_t=T/m$. ∎
The roll-rate term $\frac{J_a}{mL}r\Omega_\perp$ is **not** zero in general. The exact reduction needs $r\equiv0$, or must carry this term (for GTPL $J_a/J_t\approx0.06$). Boundary data map affinely: $y_0=r_0+kb_0$, $\dot y_0=v_0+k\dot b_0$. For the landing to be a fixed affine condition on $(y,\dot y)$ one needs **$b(t_f)=e_z$ and $\Omega(t_f)=0$** (upright at rest), so that $y(t_f)=ke_z$ and $\dot y(t_f)=0$. The reduced problem is a zero-gimbal, torque-limited model with a prescribed terminal attitude, i.e. the "tent" case of M3, which §6.2 lists as open. The planar-comparison lemma that would complete it is being checked by [adversary-6dof]. **Status: reduction proved (for $r\equiv0$); the obstruction for the reduced problem is pending.**

**Conjecture B3b.** For M3b with $\Omega(0)=0$ and small $t_f$, $F_{t_f}$ is nonconvex. A proof needs either an explicit admissible $P$ with $|P_z|<G$ (numerics, owned by [adversary-6dof]) or a rigidity analysis of the minimizers of $I_z$ under the coupled dynamics. Both are open here.

---

## 7. Longer horizons and free final time

### 7.1 Free terminal attitude: every horizon
Let $\psi_d(s)=\min(\delta+\omega s,\pi)$.

**Theorem L.** In M1 with $\rho_1>0$, $0<\omega<\infty$, $0\le\delta<\pi$, $\alpha\ge0$, (H$_m$), and $b(t_f)$ free, $F_{t_f}$ is nonconvex **for every $t_f>0$**. No uniform convex relaxation is lossless.

*Proof.* (1) *Pointwise bound.* For a.e. $s$, $d_z(s)\ge\cos\psi_d(s)$. If $\delta+\omega s\le\pi$, this is Lemma 4.1(a) with $\beta=\omega s\le\pi$ (by (AL$_\omega$), $b_z(s)\ge\cos\omega s$). Otherwise the bound reads $d_z\ge-1$. (2) *Inner minimization.* For a fixed throttle $T$, the acceleration $a_T=T/m_T>0$ is fixed, and $I_z=\int a_Td_z\ge V(T):=\int a_T\cos\psi_d$. *No sign condition is needed*, since $a_T$ does not depend on $(b,d)$. Equality is attained by the **capped arcs** $b_u=\cos\chi\,e_z+\sin\chi\,u$ and $d_u=\cos\psi_d\,e_z+\sin\psi_d\,u$, with $\chi(s)=\min(\omega s,\pi-\delta)$. These are admissible: $|\chi(s)-\chi(s')|\le\omega|s-s'|$, $\chi\in[0,\pi]$, and $\psi_d-\chi=\delta$. (3) *Outer minimization.* $\mathcal T=\{T\in L^\infty:\rho_1\le T\le\rho_2\}$ (intersected with $\{\alpha\int T\le m_0-m_{dry}\}$ if the dry-mass constraint is used) is convex and weak-* compact, and weak-* sequentially compact since $L^1$ is separable. If $T_n\overset{*}\rightharpoonup T$, then $m_{T_n}\to m_T$ uniformly (pointwise convergence plus a common Lipschitz constant $\alpha\rho_2$), with $m\ge m_0-\alpha\rho_2t_f>0$. So $V(T_n)=\int T_n\frac{\cos\psi_d}{m_{T_n}}\to V(T)$. Hence $V$ attains its minimum $V^*$ at some $T^*$. (If $\alpha=0$, $T^*$ is explicit: $\rho_1$ where $\cos\psi_d>0$ and $\rho_2$ where $\cos\psi_d<0$.) (4) The arcs $P^*_{\pm u}$ (throttle $T^*$, capped arcs $\pm u$) lie in $R$, and their midpoint is $M^*=V^*e_z$. (5) Suppose $M^*=I$ for some $(T,d,b)$. Then $V^*=I_z\ge V(T)\ge V^*$, so $\int a_T(d_z-\cos\psi_d)=0$ with a nonnegative integrand. Since $a_T\ge\rho_1/m_0>0$, $d_z=\cos\psi_d$ a.e. (6) Let $s^*=\min(t_f,(\pi-\delta)/\omega)>0$. For a.e. $s\in(0,s^*)$: $\beta=\omega s\in(0,\pi)$ and $\delta+\beta<\pi$. Corollary 4.2 then gives $b_z(s)=\cos\omega s$ and $d(s)=\cos(\delta+\omega s)e_z+\sin(\delta+\omega s)u(s)$. By Lemma 4.4, $b_z=\cos\omega s$ on $[0,s^*]$. By Lemma 4.5 (pairs in $(0,s^*)$, $\omega(s'-s)<\pi$), $u\equiv u_0$. For a.e. $s\in[s^*,t_f]$, $d_z=-1$, so $d=-e_z$ and $d_h=0$. (7) Then $I_h=\big(\int_0^{s^*}a_T\sin(\delta+\omega s)\,ds\big)u_0\ne0$, because $\delta+\omega s\in(0,\pi)$ on $(0,s^*)$. This contradicts $M^*_h=0$. ∎

Theorem L is qualitative: no explicit gap for $\delta+\omega t_f/2>\pi/2$, and it relies on weak-* compactness when $\alpha>0$. Physically, the regime $\delta+\omega s>\pi/2$ means downward thrust, so the relevant content is Thm B/Q. Theorem L shows that the obstruction is **not an artefact of short horizons**.

### 7.2 Tent variant: longer horizons
**Theorem L_T.** Variant T with $\rho_1>0$, $0<\omega<\infty$, $\delta\ge0$, $\delta+\omega t_f/2\le\pi$, $\omega t_f/2<\pi$, $\alpha\ge0$, (H$_m$): $F_{t_f}$ is nonconvex.
*Proof.* As in Theorem L, with $\psi_d=\delta+\varphi_T\le\pi$ and witnesses the tent arcs (tilt $\varphi_T\le\pi-\delta$). Equality gives $b_z=\cos\varphi_T$ a.e. on $\{\delta+\varphi_T<\pi\}$, which is dense, so it holds everywhere (Lemma 4.4). Rigidity holds on $(0,t_f/2]$ and on $[t_f/2,t_f)$; tilts lie in $(0,\pi)$ because $\omega t_f/2<\pi$. Chaining through $t_f/2$ gives $u\equiv u_0$, and $I_h=(\int a_T\sin(\delta+\varphi_T))u_0\ne0$. ∎

**Proposition 7.1 (the tent witness fails for very long horizons).** If $\alpha=0$ and $\omega t_f\ge2\pi$, then $M^*_T\in R$. *Proof.* Ascend toward $u$ at rate $\omega$ to tilt $\pi-\delta$, keeping $d=-e_z$ on the plateau. Pass through $-e_z$ to tilt $\pi-\delta$ on the $-u$ side; this takes $2\delta/\omega$ with $\angle(b,-e_z)\le\delta$ throughout. Then descend from $-u$. The schedule fits iff $t_f\ge2\pi/\omega$. With $\alpha=0$ and the time-symmetric $T^*$, the two lateral contributions cancel. ∎
So the tent-variant obstruction *by this witness* holds for $\delta+\omega t_f/2\le\pi$ and fails for $\omega t_f\ge2\pi$. In between it is open. Whether $F_{t_f}$ becomes convex for long tent horizons is **open** (I conjecture it does not: nonconvexity near other faces should persist).

### 7.3 Free final time
Let $F_{[t_a,t_b]}=\bigcup_{t\in[t_a,t_b]}F_t$.
**Proposition 7.2 (joint relaxations).** If $C\subseteq\Theta\times\mathbb R\times Y$ is convex and $C_{(\theta,t)}\ne\emptyset\iff\theta\in F_t$ for all $t\in[t_a,t_b]$ (time as a jointly convex decision variable, e.g. via dilation), then every $F_t$ is a slice of a convex set and is therefore convex. This contradicts Thm B/Q/L. *Proof.* Slices of convex sets are convex. ∎
**Proposition 7.3 (window).** Let $g=-g_0e_z$, $t^*\in[t_a,t_b]$, $\delta+\omega t_b/2\le\pi/2$, and let $M_{t^*}$ be the Thm Q midpoint at horizon $t^*$. If
$$\big|M_{t^*,z}+g_0(t-t^*)\big|\ <\ G_t(t/2)\qquad\forall t\in[t_a,t_b],$$
then $\theta_M\in\operatorname{conv}F_{[t_a,t_b]}\setminus F_{[t_a,t_b]}$. In that case no relaxation that is lossless for the free-final-time problem on that window and uniform in $\theta$ exists, even with line search hidden inside $Y$. *Proof.* If $\theta_M\in F_t$, then $I=-v_{0,M}-gt=M_{t^*}+g(t^*-t)\in R_t$. Its norm is $|M_{t^*,z}+g_0(t-t^*)|<G_t(t/2)$, contradicting Lemma 5.1 at horizon $t$. ∎
The condition holds at $t=t^*$ by Thm Q and, by continuity, on a window around $t^*$ of width $\gtrsim\Gamma_F/(g_0+\max_t|\partial_tG_t|)$. **Not proven:** nonconvexity of $\bigcup_{t\ge0}F_t$ with unbounded free final time. [adversary] reports a "dive-then-brake" face argument claimed to cover every $t_f$ and free $t_f$ (math/01 §B*). I have not verified it.

**Practical reading.** LCvx line search over $t_f$ (one convex problem per fixed $t_f$) is a family of convex relaxations, and each member is subject to Theorem B/Q at its own $t_f$.

---

## 8. Necessity of the ingredients; 3DOF consistency

**8.1 $\omega=\infty$ (no rate limit).** Then $b$ (hence $d$) is effectively free and the problem is 3DOF with $d\in S^2$. Rigidity (Lemma 4.5) has no analogue, and the witness $M$ *is* reachable: put $b=d$ equal to $d_u$ on a measurable set $E$ and to $d_{-u}$ on its complement, with $\int_Ea_1\sin(\delta+\varphi)=\int_{E^c}a_1\sin(\delta+\varphi)$ (possible by continuity of $s\mapsto\int_0^s$). $R$ is convex (Prop. 8.2). The argument correctly does **not** apply to 3DOF LCvx.
**8.2 $\omega=0$.** Then $b\equiv e_z$ and $d\in\operatorname{cone}(e_z,\delta)$ (3DOF with a pointing constraint): $\varphi\equiv0$, $u$ is undefined, $\Gamma_F\to0$, and $M\in R$ by chattering of the azimuth of $d$ on the cone boundary. Convex for $\alpha=0$ (Aumann). **So $\omega\in(0,\infty)$ is essential.**
**8.3 $\delta$.** It is not needed: $\delta=0$ ($d=b$, no gimbal) gives $\Gamma_F=\frac{4a_1}{\omega}\sin\frac{\omega t_f}{2}\sin^2\frac{\omega t_f}{4}>0$. Theorem L works for all $\delta<\pi$. At $\delta\ge\pi$ the gimbal constraint disappears and we are back in 8.1. The gimbal only shrinks the regime ($\delta+\omega t_f/2\le\pi/2$).
**8.4 $\rho_1=0$.**
- Short horizon ($\delta+\omega t_f\le\pi/2$): the method fails. With $\alpha=0$, $R$ contains the whole axis segment $\{ze_z:0\le z\le\rho_2t_f/m_0\}$ (vertical thrust at variable throttle), and $\min_RI_z=0$. So the axis test (Lemma 6.3) cannot detect nonconvexity. Whether $R$ is convex is **open** (passed to [numerics]).
- Long horizon: **Proposition 8.1.** If $\rho_1=0$, $\alpha=0$ and $\delta+\omega t_f>\pi/2$, $F_{t_f}$ is still nonconvex (variant F). *Proof.* As in Theorem L, $T^*=0$ on $\{\cos\psi_d>0\}$ and $T^*=\rho_2$ on $\{\cos\psi_d<0\}$. Equality forces $a_T=a_2>0$ and $d_z=\cos\psi_d$ on $(s_0,\min(s^*,t_f))$ with $s_0=(\pi/2-\delta)/\omega$, which is a nondegenerate interval. Rigidity holds there. Elsewhere either $a_T=0$ or $d=-e_z$. So $I_h=(\int_{s_0}^{\min(s^*,t_f)}a_2\sin(\delta+\omega s))u_0\ne0$. ∎
So $\rho_1>0$ is essential only in the physically relevant short-horizon regime, and only for this method.
**8.5 Mass depletion $\alpha$, gravity $g$, $b_0$.** None is essential: $\alpha\ge0$ is arbitrary, $g$ enters as an affine shift, and $b_0$ is arbitrary. Lemma 5.1 does not use $b(0)$ at all, so Thm Q also holds if the initial attitude is a free decision variable, since $P_{\pm u}$ with $b(0)=e_z$ are still in $R$. **What is essential is that the attitude constraint couples times**, through continuity with a rate bound. Pointwise (measurable) attitude constraints never obstruct, by Aumann.

**Proposition 8.2 (exact 3DOF feasible sets).**
(a) $\alpha=0$, with any measurable compact-valued control set $U(s)\subseteq\mathbb R^3$ for $u=ad$ (e.g. annulus ∩ pointing cone): $K=\{(\int u,\int(t_f-s)u)\}$ is convex. This is Aumann's theorem: for a nonatomic measure, the integral of a multifunction equals that of its convex hull, and is convex.
(b) $\alpha\ge0$, $d\in S^2$ free (no pointing cone): $K=\{(\int u,\int(t_f-s)u):\|u(s)\|\le a_{\max}(s)\}$ with $a_{\max}(s)=\rho_2/(m_0-\alpha\rho_2s)$, which is convex. So **the exact 3DOF problem with mass depletion has convex $F_{t_f}$**. Proof: every admissible $a$ satisfies $a\le a_{\max}$ (as in Lemma 4.3), so $K\subseteq S$. Conversely, by Aumann's theorem every point of $S$ is $\int(1,t_f-s)a_{\max}(s)d(s)\,ds$ for some measurable $d\in S^2$, and that is realized with $T\equiv\rho_2$.
(c) $\alpha>0$ with a pointing cone: **open**. For the degenerate case $d\equiv e_z$ (1D), $K\subset\mathbb R^2$ is bounded by $J_{\max}(I)$ and $J_{\min}(I)$, attained by the pointwise envelopes of $\mu=m/m_0$. One computes $J_{\max}''(x)=-\frac{\mu_f}{c_1}\big[\ln r+\frac{k}{r}-1\big]\le0$ with $r=\mu(s^*)/\mu_f\ge1$, $k=\frac{c_2}{c_2-c_1}\ge1$ (concave). Likewise $J_{\min}''(x)=-\frac{\mu_f}{c_2}\big[\ln r-\frac{k'}{r}-1\big]$ with $k'=\frac{c_1}{c_2-c_1}$, which is $\ge0$ whenever $r\le e$. Numerically $K$ is convex in all tested cases, including 95% burn (`numerics/proof/mass3dof_check.py`). Exact LCvx with mass (Açıkmeşe–Ploen 2007) is lossless for a problem that is nonconvex in $z=\ln m$. The convex SOCP uses a conservative Taylor inner approximation. **Consistency:** Theorem A does not contradict 3DOF LCvx in any case where we can decide convexity.

---

## 9. Weaknesses and scope (honest list)
1. **Uniformity is essential.** Per-instance convex relaxations (fixed attitude profile, Thm C; occupation measures with data entering as $\delta_\theta$, which is not jointly convex, cf. [lit-review]) are not excluded, and some are positive results.
2. **Affine data entry.** A nonlinear change of boundary variables is not excluded by Theorem A (§1.4). No LCvx in the literature does this.
3. **M1 is kinematic.** For the actual GTPL actuation (pitch/yaw torque from the gimbal, M3b) the obstruction is **unproven** (§6.4); M3a assumes independent transverse torque.
4. **Free final time** is covered only for joint relaxations and for windows (§7.3).
5. **State constraints.** Thms B/Q/L have none. Their witnesses are underground for GTPL. Altitude and glide slope are covered by Thm B\* (§10), whose quantitative gap is rigorous but tiny ($\sim10^{-5}$ m in $\Lambda$-units for GTPL; Rem. 10.2).
8. **Per-instance, hard soft-landing (Lemma S) is open.** Pure-TVC M3b/M4 (GTPL actuation) is open; Lemma 6.4 reduces it to a zero-gimbal torque-limited tent problem.
9. **Class boundary.** The impossibility is for the state-linear class. Moment-lifted costs and occupation-measure LPs are outside it and are not refuted (§11.1).
6. Theorem L uses weak-* compactness when $\alpha>0$ (standard, but heavier for Lean). Prop. 5.3 is a sketch.
7. Theorem Q_T for $\alpha>0$ is conditional on an explicit, numerically verified inequality.

## Change log
- v2 (2026-11-07): after [adversary] BREAK (witnesses underground under $r_z\ge0$): added Theorem B\* (rigorous, $\omega s^*\le\delta$ version of the adversary's dive-then-brake face) with state constraints, an upright variant, free-$t_f$ windows and a quantitative bound; Theorem D, the state-linear class definition, the exclusions, Lemma S (open, reduced); Prop 11.3 (trivial possibility); Lemma 6.4 (TVC flat output, with the roll-rate correction term the orchestrator's version omits). Summary and weaknesses updated. Thm B/Q/L statements unchanged and still correct for the unconstrained model.
- v1 (2026-11-06): initial. Changes relative to the math/00 sketch: (i) free-variant regime extended from $\delta+\omega t_f\le\pi/2$ to $\delta+\omega t_f/2\le\pi/2$ via the ball bound; (ii) added the explicit gap $\Gamma_F$; (iii) all-horizon Theorem L; (iv) M3/6DOF transfer stated with the precise hypotheses $\Omega(0)=0$, axisymmetric $J$, independent transverse torque, free terminal attitude. The sketch's remark that "planar arcs are 6DOF-realizable" holds only for kinematic attitude (M4-kin) or with the $\varepsilon s^2/2$ envelope (M4-dyn), and **fails** for gimbal-coupled torque (agrees with [adversary-6dof]).

---

## 10. Main theorem with state constraints: the dive-then-brake exposed face (Theorem B*)

*Context.* [adversary] (BOARD 23:50) observed that the witnesses $P_{\pm u}$ of §§4–5 run at minimum throttle. For GTPL, $\rho_1/(m_0g_0)=0.51<1$, so they start underground, and Theorems B/Q are vacuous once $r_z\ge0$ is imposed. Their repair (math/01 §B*) uses an exposed face of a rotation-invariant functional. Below is a rigorous version. I restrict the switch time to $\omega s^*\le\delta$. This makes the late-phase optimum decouple from the dive, so no envelope-replacement argument is needed, and it also yields an explicit quantitative bound with no equality case.

### 10.1 Setting
M1 (§1.2) with $g=-g_0e_z$, $g_0>0$, $b(0)=e_z$, and **state constraints**: $(r(t),v(t))\in\mathcal X$ for all $t\in[0,t_f]$, where
$$\mathcal X=\{(r,v):\ r_z\ge0,\ \ r_z\ge\tan\gamma_{gs}\,\|r_h\|\}\qquad(\gamma_{gs}\in[0,\pi/2);\ \gamma_{gs}=0\text{ gives altitude only}).$$
Any further closed constraint that is invariant under $R_\pi=\operatorname{diag}(-1,-1,1)$ (acting on $r$ and $v$) and satisfied by the witness trajectory may be added, e.g. a tilt cap $b_z\ge\cos\theta_{\max}$ with $\theta_{\max}\ge\omega s^*$. Let $F^{\mathcal X}_{t_f}\subseteq F_{t_f}$ be the constrained feasible set, where $F_{t_f}$ is unconstrained. Both are $R_\pi$-invariant (and invariant under all rotations about $e_z$), since the model and $\mathcal X$ are.

Notation: $a_{10}=\rho_1/m_0$, $a_{\max}=\rho_2/(m_0-\alpha\rho_2t_f)$, $A_b=\rho_2/m_0-g_0$. For $s^*\in(0,t_f)$ let $w(s)=s-s^*$, and for a control $c$ let
$$W(c)=\int_0^{t_f}w\,a\,d\,ds,\qquad X(c)=\int_0^{s^*}(s^*-s)\,a\,d\,ds,\qquad B(c)=\int_{s^*}^{t_f}(s-s^*)\,a\,d\,ds,\qquad W=-X+B .$$

**Lemma 10.1 (exact identity).** Let $\Lambda(\theta):=r_0+s^*v_0\in\mathbb R^3$ (a linear map $\mathbb R^6\to\mathbb R^3$ with operator norm $\sqrt{1+s^{*2}}$). If $c$ lands from $\theta$ (unconstrained), then
$$\Lambda(\theta)=W(c)+\kappa e_z,\qquad \kappa=g_0t_f(s^*-t_f/2).$$
*Proof.* By Lemma 3.1(a), $v_0=g_0t_fe_z-I$ and $r_0=-v_0t_f+\frac12g_0t_f^2e_z-J=It_f-J-\frac12g_0t_f^2e_z=\int s\,a\,d-\frac12g_0t_f^2e_z$. Hence $r_0+s^*v_0=\int(s-s^*)ad+(s^*g_0t_f-\frac12g_0t_f^2)e_z$. ∎

So $\ell(\theta):=\Lambda_z(\theta)=r_{0z}+s^*v_{0z}$ is a rotation-invariant linear functional, and $\Lambda_h(\theta)=r_{0h}+s^*v_{0h}$.

### 10.2 Statement
**Theorem B\*.** Assume $\rho_1>0$, $0<\omega<\infty$, $0<\delta<\pi/2$, (H$_m$), $A_b>0$ (full-throttle thrust-to-weight $>1$), and $s^*\in(0,t_f)$ with
$$\text{(S1)}\ \omega s^*\le\delta,\qquad\text{(S2)}\ g_0s^*<A_b(t_f-s^*),\qquad\text{(S3)}\ \tan\gamma_{gs}\,a_{\max}s^{*2}\le A_b(t_f-s^*)^2 .$$
(With a dry-mass constraint, also assume $m_0-\alpha\rho_2t_f\ge m_{dry}$.) Then there are $\theta^*\in F^{\mathcal X}_{t_f}$ and $R_\pi\theta^*\in F^{\mathcal X}_{t_f}$ whose midpoint $\theta_m$ (zero lateral components) satisfies $\theta_m\notin F_{t_f}\supseteq F^{\mathcal X}_{t_f}$. Hence **$F^{\mathcal X}_{t_f}$ is nonconvex for every $t_f>0$** (for every $t_f$ one can choose $s^*$ small enough that (S1)–(S3) hold), and by Theorem A no uniform convex relaxation of the altitude/glide-slope-constrained problem is lossless.
If moreover $\delta\le\pi/4$, then quantitatively
$$\operatorname{dist}(\theta_m,F_{t_f})\ \ge\ \frac{\eta_0}{\sqrt{1+s^{*2}}},\qquad (1+c_1)\eta_0+\sqrt{2W_b\eta_0}=\gamma_X,$$
$$\gamma_X=\tfrac{5}{32}a_{10}\sin\delta\,s^{*2},\quad c_1=\frac{1}{\omega\vartheta s^*},\quad \vartheta=\frac{a_{10}\sin\delta}{4a_{\max}},\quad W_b=\tfrac12a_{\max}(t_f-s^*)^2 .$$
**Variants covered by the same proof:** (T') upright landing $b(t_f)=e_z$, if $t_f\ge2s^*$; free final time on any compact window (Cor. 10.4); 6DOF and torque-limited attitude with independent transverse torque (Rem. 10.5).

### 10.3 Proof
*Step 1 (direction bound for fixed throttle).* Fix $T$, hence $a=a_T>0$. For a.e. $s\in[0,s^*]$: $b_z(s)\ge\cos\omega s$ by (AL$_\omega$), and $\delta+\omega s\le2\delta<\pi$, so Lemma 4.1(a) gives $d_z\ge\cos(\delta+\omega s)$. On $(s^*,t_f]$, $d_z\le1$. Since $w<0$ on $[0,s^*)$ and $w>0$ on $(s^*,t_f]$,
$$W_z(c)\ \le\ V(T):=-\int_0^{s^*}(s^*-s)a_T\cos(\delta+\omega s)\,ds+\int_{s^*}^{t_f}(s-s^*)a_T\,ds .\tag{10.1}$$
Define the deficits $\eta_{dive}=X_z-Z_0(T)\ge0$ and $\eta_{brake}=B_0(T)-B_z\ge0$, where $Z_0(T)=\int_0^{s^*}(s^*-s)a_T\cos(\delta+\omega s)$ and $B_0(T)=\int_{s^*}^{t_f}(s-s^*)a_T$. Then $V(T)-W_z(c)=\eta_{dive}+\eta_{brake}$.

*Step 2 (equality is attained, for every $T$).* The dive-brake control $c_u^T$: on $[0,s^*]$, $b=\cos(\omega s)e_z+\sin(\omega s)u$ and $d=\cos(\delta+\omega s)e_z+\sin(\delta+\omega s)u$; on $(s^*,t_f]$, $b\equiv b(s^*)$ and $d=e_z$. It is admissible: $\angle(b(s),b(s'))=\omega|\min(s,s^*)-\min(s',s^*)|\le\omega|s-s'|$; the gimbal angle is $\delta$ on the dive and $\angle(e_z,b(s^*))=\omega s^*\le\delta$ by (S1) on the brake. It attains equality in (10.1). In variant T', replace $b$ on $[s^*,2s^*]$ by the meridional return $\cos(\omega(2s^*-s))e_z+\sin(\omega(2s^*-s))u$ and set $b=e_z$ after. The gimbal angle stays $\le\delta$, so equality still holds.

*Step 3 (late throttle).* Let $T^\sharp=T$ on $[0,s^*]$ and $T^\sharp=\rho_2$ on $(s^*,t_f]$. Then $a_{T^\sharp}=a_T$ on $[0,s^*]$, and for $s>s^*$, $a_T(s)=T(s)/(m(s^*)-\alpha\int_{s^*}^sT)\le\rho_2/(m(s^*)-\alpha\rho_2(s-s^*))=a_{T^\sharp}(s)$, strictly wherever $T(s)<\rho_2$. So $V(T)\le V(T^\sharp)$, with strict inequality unless $T=\rho_2$ a.e. on $(s^*,t_f]$.

*Step 4 (outer maximum).* $V^*:=\sup_TV(T)$ is attained at some $T^*$, and $T^*=\rho_2$ a.e. on $(s^*,t_f]$ by Step 3. If $\alpha=0$, $T^*=\rho_1$ on $[0,s^*)$ and $\rho_2$ after, explicitly. If $\alpha>0$, existence follows from weak-* compactness of $\{T|_{[0,s^*]}\}$ and weak-* continuity of $V$, exactly as in the proof of Theorem L. (For the quantitative part, a near-maximizer suffices; see Remark 10.3.)

*Step 5 (the witnesses satisfy the state constraints).* Take $c^*=c^{T^*}_u$, landing from $\theta^*$. *Brake phase:* $d=e_z$, so $v_h(t)=v_h(t_f)-\int_t^{t_f}ad_h=0$ and $r_h=0$ on $[s^*,t_f]$. Vertically, $\dot v_z=a-g_0\ge\rho_2/m_0-g_0=A_b>0$, so $v_z(t)\le-A_b(t_f-t)$ and $r_z(t)=-\int_t^{t_f}v_z\ge\frac12A_b(t_f-t)^2$. *Dive phase:* $\dot v_z=ad_z-g_0\ge-g_0$, so $v_z(t)\le v_z(s^*)+g_0(s^*-t)\le-A_b(t_f-s^*)+g_0s^*<0$ by (S2). Hence $r_z$ is decreasing on $[0,t_f]$, and $r_z(t)\ge r_z(s^*)\ge\frac12A_b(t_f-s^*)^2$ on $[0,s^*]$. Laterally, $\|v_h(t)\|\le a_{\max}(s^*-t)$, so $\|r_h(t)\|\le\frac12a_{\max}s^{*2}$, and (S3) gives the glide-slope inequality. The tilt is $\le\omega s^*$. So $\theta^*\in F^{\mathcal X}$, and by invariance $R_\pi\theta^*\in F^{\mathcal X}$ (it is landed by $c^{T^*}_{-u}$).

*Step 6 (the midpoint is not even unconstrained-feasible).* $\theta_m=\frac12(\theta^*+R_\pi\theta^*)$ has $\Lambda(\theta_m)=\Lambda_z(\theta^*)e_z=(V^*+\kappa)e_z$, by Lemma 10.1 and Step 2. Suppose $\theta_m\in F$ via a control $c=(T,b,d)$. Then $W(c)=V^*e_z$, so $V^*=W_z(c)\le V(T)\le V^*$. All inequalities in Step 1 are then equalities a.e. Since $(s^*-s)a_T>0$ on $[0,s^*)$, $d_z=\cos(\delta+\omega s)$ a.e. on $[0,s^*]$. Corollary 4.2, Lemma 4.4 and Lemma 4.5 (as in Theorem B, Steps 3–5, now on $(0,s^*]$ where $\omega s\in(0,\delta]$) give a constant $u_0$ with $d=\cos(\delta+\omega s)e_z+\sin(\delta+\omega s)u_0$ a.e. on $[0,s^*]$. On $(s^*,t_f]$, $(s-s^*)a_T>0$ forces $d_z=1$, so $d_h=0$. Therefore $W_h(c)=-\big(\int_0^{s^*}(s^*-s)a_T\sin(\delta+\omega s)ds\big)u_0\ne0$, because $\delta>0$. But $W_h(c)=\Lambda_h(\theta_m)=0$, a contradiction. ∎(qualitative)

*Step 7 (quantitative: no equality case, no rigidity, no compactness).* Assume $\delta\le\pi/4$. Let $c=(T,b,d)$ land from $\theta\in F$ and put $\eta:=V^*-W_z(c)\ge\eta_{dive}+\eta_{brake}$. Fix $\tau=\vartheta s^*$ and $c_\tau=b(\tau)$, with tilt $\beta\le\omega\tau$.
(i) As in Lemma 5.1, for $s\in[0,s^*]$: $\langle d(s),c_\tau\rangle\ge\cos(\delta+\omega|s-\tau|)\ge0$, because $\delta+\omega s^*\le2\delta\le\pi/2$. So $\langle X,c_\tau\rangle\ge G(T):=\int_0^{s^*}(s^*-s)a_T\cos(\delta+\omega|s-\tau|)$.
(ii) Write $c_\tau=\cos\beta\,e_z+\sin\beta\,n$ with $n$ a horizontal unit vector. Since $X_z\ge0$: $\sin\beta\,\|X_h\|\ge\langle X,c_\tau\rangle-X_z\cos\beta\ge G(T)-X_z=G(T)-Z_0(T)-\eta_{dive}$.
(iii) $G(T)-Z_0(T)=\int_0^{s^*}(s^*-s)a_Th_\tau$ with $h_\tau(s)=\cos(\delta+\omega|s-\tau|)-\cos(\delta+\omega s)$. For $s\ge\tau$, $h_\tau\ge\omega\tau\sin\delta$ by the mean value theorem, with all angles in $[\delta,\pi/2]$. For $s\in[\tau/2,\tau]$, $h_\tau\ge0$. For $s<\tau/2$, $h_\tau\ge-\omega\tau$. Using $a_{10}\le a_T\le a_{\max}$:
$G-Z_0\ge\omega\tau\big[a_{10}\sin\delta\,\tfrac{(s^*-\tau)^2}{2}-a_{\max}\tfrac{s^*\tau}{2}\big]\ge\omega\tau\cdot\gamma_X$, by the choice of $\vartheta$: $(1-\vartheta)^2-\tfrac14\ge\tfrac{5}{16}$ since $\vartheta\le\tfrac14$.
(iv) If $\omega\tau\gamma_X-\eta_{dive}>0$, then $\sin\beta>0$ and, since $\sin\beta\le\omega\tau$, $\|X_h\|\ge(\omega\tau\gamma_X-\eta_{dive})/\sin\beta\ge\gamma_X-\eta_{dive}/(\omega\tau)=\gamma_X-c_1\eta_{dive}$. Otherwise this bound is $\le0$ and holds trivially.
(v) $\|d_h\|=\sqrt{1-d_z^2}\le\sqrt{2(1-d_z)}$. By Cauchy–Schwarz, $\|B_h\|\le\int_{s^*}^{t_f}(s-s^*)a\sqrt{2(1-d_z)}\le\sqrt{B_0(T)}\sqrt{2\eta_{brake}}\le\sqrt{2W_b\eta}$.
(vi) $\|\Lambda(\theta)-\Lambda(\theta_m)\|^2=\|W_h(c)\|^2+\eta^2$, and $\|W_h\|\ge\|X_h\|-\|B_h\|\ge\gamma_X-c_1\eta-\sqrt{2W_b\eta}$. So $\|\Lambda(\theta)-\Lambda(\theta_m)\|\ge\max(\eta,\gamma_X-c_1\eta-\sqrt{2W_b\eta})\ge\eta_0$. Finally $\|\theta-\theta_m\|\ge\|\Lambda(\theta-\theta_m)\|/\sqrt{1+s^{*2}}$. ∎

**Remark 10.2 (what the quantitative bound says).** For GTPL ($\rho_1=400$ N, $\rho_2=1000$ N, $m_0=80$ kg, $\alpha=5.66\cdot10^{-4}$, $\delta=15^\circ$, $\omega=0.4$ rad/s, $\gamma_{gs}=30^\circ$), $s^*=\delta/\omega=0.654$ s, and `numerics/proof/bstar_constants.py` gives $\gamma_X=0.087$ m and $\eta_0\approx1.3\cdot10^{-5}$ m at $t_f=7$ s. The bound is rigorous but **tiny**. The reason is real, not an artefact of sloppiness. A competitor can cancel the weighted lateral moment by tilting slightly during the long brake, at a cost quadratic in the tilt, $\sim\|X_h\|^2/(2W_b)$. So the nonconvexity exposed by this face is genuine but thin. The large gaps of Thm Q live at the (state-infeasible) min-throttle face.

**Remark 10.3 (Lean-friendly route).** Step 7 needs neither the equality case of Lemma 4.1, nor Lemmas 4.4–4.5, nor the existence of $T^*$. Use any throttle $\hat T$ with $\hat T=\rho_2$ late, put $\hat V=V(\hat T)$, and replace $V^*$ by $\hat V$. Every competitor has $W_z\le V(T)\le V(T^\sharp)\le V^*$, but the bound needs $\eta$ measured from $V(T)$: use $\eta_{dive}+\eta_{brake}\le V^*-W_z$, with the explicit $T^*$ for $\alpha=0$. For $\alpha>0$, replace $V^*$ by the sup and the witness by a near-maximizer with $V^*-V(\hat T)<\eta_0/2$. This is the recommended formal target for the *constrained* problem (blueprint §B*).

**Corollary 10.4 (free final time on a window).** Let $0<t_a\le t_b<\infty$ and choose $s^*<t_a$ with (S1)–(S3) at $t_f=t_a$ (they are monotone in $t_f$; use $a_{\max}$ at $t_b$). Then $\bigcup_{t\in[t_a,t_b]}F^{\mathcal X}_t$ is nonconvex.
*Proof.* $\ell^*(t):=\sup_{F_t}\ell=V^*_t+\kappa(t)$. $V^*_t$ is nondecreasing in $t$ (extend with $\rho_2$, $d=e_z$) and Lipschitz, since $V^*_{t'}\le V^*_t+(t'-t)(t'-s^*)a_{\max}$ by restriction. So $\ell^*$ is continuous and attains its max on $[t_a,t_b]$ at some $t^\circ$. Its witness pair is in $F^{\mathcal X}_{t^\circ}$. If the union were convex, $\theta_m(t^\circ)\in F_{t'}$ for some $t'\in[t_a,t_b]$ with $\ell(\theta_m)=\ell^*(t^\circ)\ge\ell^*(t')$. Then $\theta_m$ would be a maximizer at horizon $t'>s^*$, and Step 6 at horizon $t'$ forces $\Lambda_h\ne0$ ($\Lambda$ does not depend on the horizon). Contradiction. ∎ Unbounded free time: $\ell^*(t)\to\infty$, so this face does not exist. The dry-mass constraint gives $t\le(m_0-m_{dry})/(\alpha\rho_1)$, which makes the window compact automatically.

**Remark 10.5 (6DOF / torque-limited attitude).** For M4-kin, Steps 1–7 are unchanged (Theorem 6.2's projection and lift; the dive is a rotation about a fixed horizontal axis). For M3a/M4-dyn (independent transverse torque, axisymmetric, $\Omega(0)=0$), replace $\omega s$ by $\Psi(s)=\varepsilon s^2/2$ and (S1) by $2\Psi(s^*)\le\delta$. After $s^*$, decelerating at $\varepsilon$ adds at most $\Psi(s^*)$ of tilt, so $d=e_z$ stays admissible for *every* dive history, and the decoupling of Step 1 holds. Upright landing at rest ($b(t_f)=e_z$, $\Omega(t_f)=0$) is reachable within the brake phase when $t_f-s^*\ge4\sqrt{\delta/\varepsilon}$. This agrees with [adversary-6dof]'s Thm D*. **Gimbal-torque-coupled M3b (the GTPL actuation) remains open**: outward gimbal decelerates the tilt (see [adversary-6dof] BREAK 00:40).

**Answers to [adversary]'s check-list.** (1) Strictness when $\Phi+\delta$ hits $\pi$: excluded, since tilts are $\le2\delta<\pi$. (2) Late window with $b(t_f)=e_z$: fine for $t_f\ge2s^*$ (variant T'). (3) "Late $T=\rho_2$ forced" with relaxed throttle: not needed. Step 3 is a pointwise comparison for ordinary controls; a relaxed throttle measure can be replaced by its mean, since $\dot m$ and $a\,d$ (for fixed $m$) are linear in $T$. Relaxed $d$ is never needed, because $d$ is optimized pointwise in closed form.

### 10.6 Envelope version (no (S1)), qualitative, following [adversary] math/01 §B*
(S1) caps $s^*$ at $\delta/\omega$ (0.65 s for GTPL), and the gap scales roughly like $s^{*4}$. [adversary]'s heuristic `numerics/adversary/a6_gap_heuristic.py` (corrected rerun) gives $\approx|X_h-\text{tail}|^2/(2B_0)$: $2\cdot10^{-4}$ m at $s^*=0.654$, $1.4\cdot10^{-3}$ m at $1.0$, $7.4\cdot10^{-3}$ m at $1.5$, $1.2\cdot10^{-2}$ m at the (S2) limit ($t_f=8$), and $1.0\cdot10^{-2}$ m at $t_f=12$, $s^*=2.58$. So altitude-feasible gaps at these faces are $\lesssim1$ cm.

**Theorem B\*-env.** Assume the hypotheses of Theorem B\* except (S1); instead assume $\delta+\omega s^*<\pi$. Assume also the witness conditions
(S2') $\rho_2\cos(\omega s^*)/m_0>g_0$ and $s^*(a_{\max}+g_0)<(t_f-2s^*)(\rho_2\cos(\omega s^*)/m_0-g_0)$, and
(S3') $\tan\gamma_{gs}\,2a_{\max}s^{*2}\le\frac12(\rho_2\cos(\omega s^*)/m_0-g_0)(t_f-2s^*)^2$.
Then $F^{\mathcal X}_{t_f}$ is nonconvex.

*Proof.* (1) *Tilt profile.* Let $\Phi(s)=\angle(b(s),e_z)$. By the angle triangle inequality and (AL$_\omega$), $\Phi$ is $\omega$-Lipschitz with $\Phi(0)=0$. (2) *Pointwise direction bound for fixed $T$.* On the dive, Lemma 4.1(a) gives $d_z\ge\cos(\Phi+\delta)$. Late, apply Lemma 4.1(a) to $(d,b,-e_z)$ to get $d_z\le\cos((\Phi-\delta)^+)$. Hence $W_z\le J_T(\Phi):=\int_0^{s^*}w\,a_T\cos(\Phi+\delta)+\int_{s^*}^{t_f}w\,a_T\cos((\Phi-\delta)^+)$. Equality holds iff, a.e., $d$ is the unique extremal: on the dive $d=\cos(\Phi+\delta)e_z+\sin(\Phi+\delta)u(s)$ (Cor. 4.2); late, $d=\cos(\Phi-\delta)e_z+\sin(\Phi-\delta)u(s)$ where $\Phi>\delta$ (Lemma 4.1(b) with $z=-e_z$, $\beta=\pi-\Phi$), and $d=e_z$ where $\Phi\le\delta$. Here $u(s)$ is the azimuth of $b(s)$. (3) *Profile bound.* With $p=\Phi(s^*)\in[0,\omega s^*]$, Lipschitz continuity gives $\Phi\le E_p(s):=\min(\omega s,p+\omega(s^*-s))$ on $[0,s^*]$ and $\Phi\ge L_p(s):=(p-\omega(s-s^*))^+$ on $[s^*,t_f]$. The dive integrand is strictly increasing in $\Phi$ (since $w<0$, $a_T>0$, and $\cos$ is strictly decreasing on $[\delta,\pi]$). The late integrand is nonincreasing, and strictly decreasing where $\Phi>\delta$. So $J_T(\Phi)\le j_T(p):=J_T(E_p\text{ on dive},L_p\text{ late})$. Equality forces $\Phi=E_p$ on $[0,s^*]$ (a.e., hence everywhere by Lemma 4.4) and $\Phi=L_p$ on $\{s>s^*:L_p(s)>\delta\}$. (4) *Outer maximum.* $j_T(p)$ is continuous in $p$, and $T\mapsto\max_pj_T(p)$ is weak-* continuous on the throttle set (as in Thm L), so a maximizer $(T^*,p^*)$ exists. Late $T^*=\rho_2$ by the pointwise comparison of Step 3 of §10.3. This needs the extremal late $d_z=\cos((\Phi-\delta)^+)\ge0$, i.e. $\omega s^*-\delta\le\pi/2$. That does **not** follow from $\delta+\omega s^*<\pi$ alone, but it is implied by (S2'), since $\cos(\omega s^*)>m_0g_0/\rho_2>0$ forces $\omega s^*<\pi/2$ (GTPL: $\omega s^*<0.67$ rad). (Pointed out by [adversary].) (5) *Witness.* The meridional curve with tilt $E_{p^*}$ then $L_{p^*}$, with extremal $d$ and throttle $T^*$, is admissible. It attains $j_{T^*}(p^*)$. Its lateral motion stops at $q=s^*+(p^*-\delta)^+/\omega\le2s^*$. Brake acceleration satisfies $\ge\rho_2\cos(\omega s^*)/m_0-g_0>0$ for $s\ge s^*$. As in Step 5 of §10.3, (S2')/(S3') give $r_z>0$ and the glide slope. (6) *Midpoint.* If $\theta_m$ were in $F$ via $c$, then $W_z(c)=\max$, and (2)–(3) force $\Phi$ to be piecewise linear with slope $\pm\omega$ on $(0,q)$, positive there, with at most one peak. Lemma 4.5 on each monotone piece, chained through the peak, makes $u\equiv u_0$ on $(0,q)$. So $I_h(c)=\big(\int_0^{s^*}a_T\sin(\Phi+\delta)+\int_{s^*}^{q}a_T\sin(\Phi-\delta)\big)u_0\neq0$. Both integrands are $\ge0$ and the first is $>0$. Use the **unweighted** increment $I_h=-v_{0h}$ here: in the weighted $W_h$ the dive and late contributions have opposite signs and could cancel. But $v_{0h}(\theta_m)=0$, a contradiction. ∎
*Status:* qualitative and rigorous. A quantitative version of Step 7 near the (S2') limit is **not** done. The adversary's heuristic scale above is numerical evidence, not a bound.

---

## 11. Per-instance obstruction (Theorem D), the state-linear class, and its boundary

### 11.1 Definitions
Fix one instance: data $\theta_0=(r_0,v_0)$, $m_0$, $b(0)$, $t_f$, and the constraint set $\mathcal X$. Let $\mathrm{Reach}(\theta_0)\subseteq\mathbb R^6$ be the set of terminal states $x_f=(r(t_f),v(t_f))$ of genuine admissible trajectories from $\theta_0$ that stay in $\mathcal X$.

**Definition 11.1 (state-linear relaxation of an instance).** A tuple $(Y,C,\rho,P)$ with $Y$ a real vector space, $C\subseteq Y$ convex, $\rho:Y\to\mathbb R^6$ affine (the *physical readout* of the terminal state; more generally of $r(\cdot),v(\cdot)$ at any finite set of times), and $P:Y\to[0,\infty]$ convex (a penalty), such that
**(E) embedding:** for every genuine trajectory with terminal state $x_f$ there is $y\in C$ with $\rho(y)=x_f$ and $P(y)=0$.
For a convex terminal-error function $\varphi:\mathbb R^6\to(-\infty,\infty]$ (e.g. $\varphi(x)=\|x_r-q\|+\iota_{\{x_v=0\}}(x)$ for min-landing-error with hard $v(t_f)=0$, or $\varphi(x)=\|x-x^\circ\|$), the **relaxed problem** is $\inf_{y\in C}\varphi(\rho(y))+P(y)$ and the **original** is $\inf_{x\in\mathrm{Reach}}\varphi(x)$.
This is the LCvx paradigm: the physical states are decision variables entering linearly; the dynamics $\dot r=v$, $\dot v=u+g$ are linear; the control set is convexified; and the cost is evaluated on the physical variables, plus convex slack penalties such as $\int\Gamma$ replacing $\int\|T\|$, which vanish on genuine points.

**Excluded explicitly (the boundary of the impossibility class).**
(i) *Costs on lifted moments of the readout.* For instance $R\succeq r(t_f)r(t_f)^\top$ with cost $\operatorname{tr}R-2q^\top r+\|q\|^2$ ([adversary], thread theorem-D (4)): on mixtures this is an *average* error, not a function of the mean readout.
(ii) *Occupation-measure / Young-measure LPs.* Their terminal conditions are imposed on the *support* of a lifted terminal measure ($\mu_T(\mathbb R^6\setminus Q)=0$), and costs are $\int\varphi\,d\mu_T$. Both are linear in $\mu$ but are not functions of the mean readout $\int x\,d\mu_T$. These relaxations are convex and value-exact under Vinter-type conditions. They are **not** excluded by our results, and they are the honest boundary: the obstruction is about the class where convexity acts on the physical state itself.
(iii) *Inner restrictions* (fixed attitude profile, Thm C; planar maneuvers; Taylor-approximated mass) violate (E). They may be exact on their own domain, and they are the positive side.

### 11.2 Theorem D
**Theorem D.** For any state-linear relaxation of an instance, $\rho(\{y\in C:P(y)=0\})\supseteq\operatorname{conv}\mathrm{Reach}(\theta_0)$. Hence the relaxed value is at most $\inf_{\operatorname{conv}\mathrm{Reach}}\varphi$. In particular, if $x^\circ\in\operatorname{conv}\mathrm{Reach}\setminus\operatorname{cl}\mathrm{Reach}$ and $\varphi=\|\cdot-x^\circ\|$, the relaxed value is $0$ while the original value is $\operatorname{dist}(x^\circ,\mathrm{Reach})>0$. The relaxation is **lossy at a feasible instance**, with no joint convexity in data and no frame dependence.
*Proof.* Let $x=\sum\lambda_ix_i$ be a convex combination of points of Reach, with embedded $y_i$. Then $y=\sum\lambda_iy_i\in C$, $\rho(y)=x$ since $\rho$ is affine, and $0\le P(y)\le\sum\lambda_iP(y_i)=0$. So the objective at $y$ equals $\varphi(x)$. ∎
*Theorem A as the feasibility counterpart:* with $\varphi=\iota_Q$ and $Q$ convex, the relaxation reports feasibility whenever $Q\cap\operatorname{conv}\mathrm{Reach}\ne\emptyset$.

**Corollary D.1 (unconditional instance; altitude-type constraints).** Let $\mathcal X$ consist of constraints depending only on the vertical state $(r_z,v_z)$ (e.g. $r_z\ge0$, descent-rate limits) and be $R_\pi$-invariant. Take the instance $\theta_0=\theta_m$ from Theorem B\* (a *vertical*, rotation-invariant instance), and $x^\circ=(0,0)$, i.e. "soft landing at the point directly below". Then $x^\circ\in\operatorname{conv}\mathrm{Reach}(\theta_m)$ and
$$\operatorname{dist}(x^\circ,\mathrm{Reach}(\theta_m))\ \ge\ \frac{\eta_0}{(1+t_f)\sqrt{1+s^{*2}}}>0 .$$
So every state-linear relaxation of this single instance, with terminal-error cost $\|x_f\|$, reports error $0$, while the true minimum error is positive.
*Proof.* Applied from $\theta_m$, the controls $c^{T^*}_{\pm u}$ produce trajectories equal to those from $\theta^*$ and $R_\pi\theta^*$, plus the horizontal shifts $-(r^*_{0h}+v^*_{0h}t)$ and its negative. Constraints that depend only on $(r_z,v_z)$ are unaffected. Their terminal states are $\pm(\text{shift}(t_f),\text{shift}'(t_f))$, which average to $0$. For any control $c$ from $\theta_m$, the terminal state is $A'(\theta_m-\theta(c))$ with $A'(\Delta r,\Delta v)=(\Delta r+t_f\Delta v,\Delta v)$ and $\|A'^{-1}\|\le1+t_f$. Here $\theta(c)\in F_{t_f}$ (unconstrained), and Theorem B\* bounds $\|\theta_m-\theta(c)\|$ from below. ∎
*Limitation:* the target has a **soft** terminal velocity (error on $(r(t_f),v(t_f))$ jointly), so this is not the LCvx soft-landing problem, where $v(t_f)=0$ is hard. The certified gap is tiny: $\eta_0/((1+t_f)\sqrt{1+s^{*2}})\approx1.4\cdot10^{-6}$ m for GTPL at $t_f=7$ s. The cost penalizes terminal velocity softly. The glide-slope cone with apex at $r(t_f)$ is not covered by D.1, because the shifted witnesses land with lateral velocity.

**Hard soft-landing version ⇔ slice Lemma S (open).** With $v(t_f)=0$ enforced and position error $\|r(t_f)-q\|$, Theorem D needs $L(\theta_0)=\{r(t_f):\ \text{genuine},\ v(t_f)=0\}$ with $\operatorname{conv}L\not\subseteq\operatorname{cl}L$. With a translation-equivariant glide slope (apex at $r(t_f)$), $L(\theta_0)=r_{0h}-\{p:(p,r_{0z},v_0)\in F\}$. So D-hard is equivalent to: **(S)** some $r_{0h}$-slice of $F$ at fixed $(r_{0z},v_0)$ has a nonconvex closure. In the cleanest instance, $v_{0h}=0$, the slice $L(\zeta)$, $\zeta=(r_{0z},v_{0z})$, is rotation-invariant, and (S) ⇔ $0\notin\operatorname{cl}L(\zeta)\neq\emptyset$.

**Proposition 11.2 (exact reduction of S).** In the setting of Theorem B\* with $\delta\le\pi/4$, let $f(\eta)=\gamma_X-c_1\eta-\sqrt{2W_b\eta}$ and $\eta_{crit}$ its root. For vertical data $\zeta$ with $\ell(\zeta)=\ell^*-\eta$, $\eta<\eta_{crit}$, every $p\in L(\zeta)$ has $\|p\|\ge f(\eta)>0$. Hence (S) holds as soon as **some state-feasible trajectory with zero net lateral impulse ($I_h=0$) has $\ell$-deficit $<\eta_{crit}$.**
*Proof.* For $v_{0h}=0$, $\Lambda_h=r_{0h}=p$, and Step 7 gives $\|\Lambda_h\|\ge f(\eta)$. ∎
*Why this does not close (S):* cancelling the dive's lateral impulse costs a deficit of order $\|I_{h,dive}\|^2/a$, about $10^{-2}$ m for GTPL. That is far above the rigorous $\eta_{crit}\sim10^{-5}$ m. A competitor that also cancels the position moment pays only an extra $\sim\|X_h\|^2/(2W_b)$. Deciding (S) therefore means comparing two second-order costs, and it must handle 3D coning (azimuth precession at fixed tilt). **(S) is open.** [numerics]/[adversary] runs a2 (mode1 vs mode2) are the relevant evidence.

### 11.3 The trivial possibility (for the record)
**Proposition 11.3.** Every optimal control problem $\min_{x\in\mathcal F}J(x)$, with $J$ bounded below, has an exact convex reformulation. Let $\tilde{\mathcal F}=\{(x,J(x)):x\in\mathcal F\}$ in any locally convex space containing it, and minimize the linear functional $(x,t)\mapsto t$ over $\operatorname{conv}\tilde{\mathcal F}$. The infimum over a convex hull of a linear functional equals the infimum over the set. If $\tilde{\mathcal F}$ is compact, then $\overline{\operatorname{conv}}\tilde{\mathcal F}$ is compact convex, the minimum is attained at an extreme point (Bauer), and extreme points lie in $\tilde{\mathcal F}$ (Milman), i.e. at genuine solutions.
This reformulation is **not state-linear**. The cost is an extra lifted coordinate that averages over mixtures (case (i) of §11.1), the hull is built per instance, and describing it is as hard as the original problem. So "is LCvx possible?" is meaningful only within a tractable class. Our impossibility is the precise statement that the **state-linear class** (Def. 1.3 and 11.1) cannot be exact for 5DOF/6DOF with attitude-rate (or decoupled torque) limits, unconditionally in the feasibility/uniform form (Thm A + B\*) and per instance in the terminal-error form (D.1). The per-instance hard-soft-landing form remains conditional on (S).
