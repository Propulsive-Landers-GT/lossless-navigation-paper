# Positive results: when lossless convexification IS possible (fixed attitude, per-instance, exact subclasses)

Author: [positive]. Status: CLAIMED (rows C, C-*, in `comms/CLAIMS.md`). Lean blueprint: `math/05-positive-lean-blueprint.md`.
Nothing here relies on prior literature as proof. Literature is cited only for context. The one external
theorem used without proof is **Aumann's integral theorem** (labelled **[Aumann]**). PMP is used only as a
labelled hypothesis **(H-PMP)**. Every other step is proved here.

---

## 0. Summary

| ID | Statement (short) | Model | Hypotheses | Status |
|---|---|---|---|---|
| C-G | **General extreme-point lemma**: maximizer of $\langle y,T\rangle$ on $\{\|T\|\le\Gamma\}\cap Q$ with $\|T\|<\Gamma$ forces $y\in N_Q(T)$ | any inner-product space | none | proved §2 |
| C-3 | **Lemma-3 analog**: on $\{\|T\|\le\Gamma,\ \langle b,T\rangle\ge\Gamma\cos\delta\}$, every maximizer has $\|T\|=\Gamma$ unless $y\in-\mathbb R_{\ge0}b$. The maximizer is then unique. Sharp. | pointwise | none | proved §2 |
| C-W | **Weak Theorem C**: for ANY measurable $b(\cdot)$, the time-varying-cone relaxation has the same optimal value and the same feasible boundary data as the original. A lossless optimal solution with identical $\Gamma$, mass, and terminal state always exists. | M1 with fixed $b$; mass or constant mass; nodewise state constraints exact; convex path constraints in value (Slater) | [Aumann] | proved §3 |
| C-F | For fixed $b$, the feasible boundary-data set $F_{t_f}(b)$ is **convex** | M1 fixed $b$, constant mass (or convexified-mass model) | [Aumann] | proved §3 |
| C-E | **Exchange**: lossiness can only occur at minimum throttle ($\Gamma^*=\rho_1$). With mass: at min throttle, or where max throttle saturates later. | relaxed fixed-$b$ problem | none (PMP-free) | proved §4 |
| C-S | **Strong Theorem C**: every relaxed optimum is lossless outside $D=\{t:p(t)\in-\mathbb R_{\ge0}b(t)\}$, where the primer $p$ is affine. With constant mass, lossy set $\subseteq D\cap\{\Gamma^*=\rho_1\}$. | M1 fixed $b$ | (H-PMP) | proved §5 |
| C-D | **Exact structure of $D$**: $p\equiv0$ (then $\Gamma^*\equiv\rho_1$), or $b$ coincides on positive measure with $\pm e$, or with a *gnomonic line* $\frac{a+ct}{\|a+ct\|}$. ND conditions are checkable. For analytic $b$: ND $\Leftarrow$ $\det(b,\dot b,\ddot b)\not\equiv0$. Bad $b$ form a meagre set. | M1 fixed $b$ | none | proved §5 |
| C-X | **Sharpness**: an explicit instance (fixed upright cone, vertical descent) where a lossy relaxed optimum exists, and an interior-point solver returns it | M1 / ACB-2013 fixed cone | none | proved §6 |
| C-K | **Discrete time**: KKT gives a nodewise lossless condition with an affine discrete primer. One extra "purification" SOCP gives a solution with at most $\tfrac12\sum_i c_i$ lossy nodes ($\le3$ without state constraints) | ZOH/FOH SOCP | Slater (for the KKT part only) | proved §7 |
| C-6 | **6DOF TVC (gimbal-torque-coupled, M3b)**: given the attitude $b(\cdot)$, the exact 6DOF problem is a convex scalar-throttle program (no relaxation). $F^{M3b}(b)$ is convex. | M3b, constant mass | none | proved §8 |
| C-U | **Per-instance exactness / union structure**: $F=\bigcup_b F(b)$ with every $F(b)$ convex, and $V(\theta)=\min_b V(b;\theta)$. With the optimal attitude $b^*$ known, the convex program is exact. Existence of 5DOF optima (M1, constant mass). | M1, M3b | [Aumann] | proved §9 |
| C-3D | **Exact subclass for 3DOF LCvx**: $V_5(\theta)=V_3(\theta)$ iff some 3DOF optimum is attitude-trackable. Closed-form primer-arc certificate. | M1 | (H-PMP) for the closed form only | proved §10 |
| C-Y | **Thinness under TVC coupling**: a prescribed thrust history with $\|T\|\ge\rho_1$ is M3b-realizable only for in-plane initial body rates in an interval of length $\le 2\delta\mu_c/\sinh(\mu_c t_f)$, with $\mu_c^2=\ell\rho_1\cos\delta/J_\perp$. GTPL: $\approx 3.5\,\mu$rad/s. So 3DOF LCvx is essentially never exactly 6DOF-optimal for a TVC-only vehicle. | M3b | none | proved §10 |
| C-Q | Open: $\rho_1=0$ and short horizon ⇒ $F^{M1}$ convex? $F(b)$ convex with exact mass? | | | conjecture §11 |

**Bottom line (possibility side).**
1. The relaxation itself is never the problem. For every fixed attitude profile, LCvx is lossless: always in value (C-W), and for every optimum under explicit, generic, checkable conditions (C-S, C-D).
2. The 5DOF/6DOF feasible set is a union of convex sets $F(b)$ indexed by attitude profiles (C-U). The impossibility results (Thm A/B/Q/L) say exactly that this union is nonconvex. The non-uniform convexification "solve the convex program at $b^*(\theta)$" is exact per instance.
3. The uniform 3DOF relaxation is exact precisely on the trackable subclass (C-3D). In the kinematic model M1 this subclass is fat (it contains every instance whose primer arc is slow and starts within $\delta$ of the current attitude). Under real TVC torque coupling (M3b) it is exponentially thin (C-Y).

There is no contradiction with Claims A/B/Q/L, and all of the above is consistent with them (§9.3).

---

## 1. Setting

### 1.1 Notation
$E$ is a real inner-product space (in applications $E=\mathbb R^3$). For $b\in E\setminus\{0\}$ and $c\in\mathbb R$ we write $\mathbb R_{\ge0}b=\{\kappa b:\kappa\ge0\}$. For a closed convex $Q\subseteq E$ and $x\in Q$, the normal cone is $N_Q(x)=\{y:\langle y,z-x\rangle\le0\ \forall z\in Q\}$. On $[0,t_f]$ we use Lebesgue measure $|\cdot|$.

The **cap** and the **lossless cap** at thrust level $\Gamma\ge0$, axis $b\in S^2$, half-angle $\delta\in[0,\pi/2)$:
$$K_\Gamma(b)=\{T:\|T\|\le\Gamma,\ \langle b,T\rangle\ge\Gamma\cos\delta\},\qquad S_\Gamma(b)=\{T:\|T\|=\Gamma,\ \langle b,T\rangle\ge\Gamma\cos\delta\}.$$
Note $S_\Gamma(b)=\{T:\|T\|=\Gamma,\ \angle(T,b)\le\delta\}$ for $\Gamma>0$.

### 1.2 The fixed-attitude problem (model M1 with $b$ given)
Data: $t_f>0$; $0<\rho_1\le\rho_2$; $\alpha\ge0$; $m_0>0$ with $m_0-\alpha\rho_2t_f>0$; $g\in\mathbb R^3$; a measurable $b:[0,t_f]\to S^2$; $\delta\in[0,\pi/2)$; boundary data $\theta=(r_0,v_0)$; a closed terminal set $X_f\subseteq\mathbb R^6$ (default $\{0\}$). Optionally there are state constraints $x(t)=(r(t),v(t))\in X(t)$ and a dry-mass bound $m(t_f)\ge m_{dry}$.

**Original problem $\mathrm{P}_0(b;\theta)$.** Minimize $\int_0^{t_f}\|T\|\,dt$ over measurable $T$ with
$$\rho_1\le\|T(t)\|\le\rho_2,\qquad \langle b(t),T(t)\rangle\ge\|T(t)\|\cos\delta\quad\text{a.e.},$$
$\dot r=v$, $\dot v=T/m+g$, $\dot m=-\alpha\|T\|$, and $x(0)=\theta$, $m(0)=m_0$, $x(t_f)\in X_f$.

**Relaxed problem $\mathrm{P}_1(b;\theta)$.** Minimize $\int_0^{t_f}\Gamma\,dt$ over measurable $(T,\Gamma)$ with
$$T(t)\in K_{\Gamma(t)}(b(t)),\qquad \rho_1\le\Gamma(t)\le\rho_2\quad\text{a.e.},\qquad \dot m=-\alpha\Gamma,$$
and the same dynamics and boundary conditions.

$(T,\Gamma)$ is **lossless at $t$** if $\|T(t)\|=\Gamma(t)$. Then $T$ is $\mathrm{P}_0$-feasible with the same mass history and cost (L8 in §2).

**Log-mass form.** With $z=\ln m$, $u=T/m$ and $\sigma=\Gamma/m$, $\mathrm P_1$ is equivalent to minimizing $\int\sigma e^{z}$, or equivalently maximizing $z(t_f)$, subject to $\dot v=u+g$, $\dot z=-\alpha\sigma$, $u\in K_\sigma(b)$, and $\rho_1e^{-z}\le\sigma\le\rho_2e^{-z}$. The map $(m,T,\Gamma)\mapsto(z,u,\sigma)$ is a bijection of feasible sets with $\|u\|=\sigma\iff\|T\|=\Gamma$. **So every losslessness statement transfers verbatim between the two forms.** The usual convex surrogate replaces the $\sigma$-bounds by Taylor bounds $\mu_1(t,z)\le\sigma\le\mu_2(t,z)$ (lower bound convex, upper bound affine, both nonincreasing in $z$). We call the resulting problem the *convexified-mass model*. All results below stated "for any $\sigma$-bounds depending only on $(t,z)$" apply to it.

**Model scope.** M1 (`math/02` §1.2) treats the gimbal angle as free inside the cone, decoupled from torque. On a TVC-only vehicle the gimbal angle *is* the pitch/yaw torque input (`comms/threads/6dof-models.md`), so M1 relaxes the real dynamics. §8 treats the coupled model M3b separately. §§2–7 are statements about the fixed-$b$ M1 problem, which is also the problem the current GTPL 3DOF code solves when $b\equiv e_z$ (`context/vehicle.md`: pointing cone about vertical).

---

## 2. Pointwise lemmas (all elementary; formalization targets)

**Lemma C-G (general extreme-point lemma).** Let $Q\subseteq E$ be convex, $\Gamma\in\mathbb R$, $y\in E$. Suppose $T^*\in B_\Gamma\cap Q$ maximizes $\langle y,\cdot\rangle$ on $B_\Gamma\cap Q$, where $B_\Gamma=\{\|T\|\le\Gamma\}$. If $\|T^*\|<\Gamma$, then $y\in N_Q(T^*)$, i.e. $\langle y,T-T^*\rangle\le0$ for all $T\in Q$.

*Proof.* Fix $T\in Q$ and put $T_s=T^*+s(T-T^*)$. Then $T_s\in Q$ for $s\in[0,1]$ by convexity. Also $\|T_s\|\le\|T^*\|+s\|T-T^*\|\le\Gamma$ for $0\le s\le s_0:=\min\{1,(\Gamma-\|T^*\|)/(\|T-T^*\|+1)\}$, and $s_0>0$. By maximality, $\langle y,T_{s_0}\rangle\le\langle y,T^*\rangle$, i.e. $s_0\langle y,T-T^*\rangle\le0$. ∎

**Lemma H (normal cone of a half-space).** Let $b\ne0$, $c\in\mathbb R$, $H=\{T:\langle b,T\rangle\ge c\}$, $T^*\in H$. If $y\in N_H(T^*)$, then $y=-\kappa b$ for some $\kappa\ge0$.

*Proof.* Put $y_\perp=y-\frac{\langle y,b\rangle}{\|b\|^2}b$, so $\langle b,y_\perp\rangle=0$. Then $T^*\pm y_\perp\in H$, hence $\pm\langle y,y_\perp\rangle\le0$, so $\langle y,y_\perp\rangle=0$. Since $\langle y,y_\perp\rangle=\|y_\perp\|^2+\frac{\langle y,b\rangle}{\|b\|^2}\langle b,y_\perp\rangle=\|y_\perp\|^2$, we get $y_\perp=0$. Also $T^*+b\in H$, so $\langle y,b\rangle\le0$. Take $\kappa=-\langle y,b\rangle/\|b\|^2\ge0$. ∎

**Lemma C-3 (pointwise lemma; analog of ACB-2013 Lemma 3).** Let $b\ne0$, $c\in\mathbb R$, $\Gamma\in\mathbb R$, and $K=\{T:\|T\|\le\Gamma,\ \langle b,T\rangle\ge c\}$. If $T^*$ maximizes $\langle y,\cdot\rangle$ over $K$, then $\|T^*\|=\Gamma$ or $y\in-\mathbb R_{\ge0}b$.
*Proof.* Combine C-G (with $Q=H$) and Lemma H. ∎
(No assumption $\|b\|=1$, $c=\Gamma\cos\delta$, or $\delta<\pi/2$ is needed. The lemma holds in any real inner-product space.)

**Lemma U (uniqueness).** In the setting of C-3, if $y\notin-\mathbb R_{\ge0}b$, the maximizer (if it exists) is unique.
*Proof.* If $T_1,T_2$ both maximize, so does $\bar T=\tfrac12(T_1+T_2)\in K$, since $K$ is convex. By C-3, $\|T_1\|=\|T_2\|=\|\bar T\|=\Gamma$. The parallelogram law gives $\|T_1-T_2\|^2=2\|T_1\|^2+2\|T_2\|^2-4\|\bar T\|^2=0$. ∎

**Lemma S (sharpness).** If $\Gamma>0$, $\|b\|=1$, $0<\delta<\pi/2$, $c=\Gamma\cos\delta$, and $y=-\kappa b$ with $\kappa\ge0$, then $T^\flat:=\Gamma\cos\delta\,b$ is a maximizer with $\|T^\flat\|=\Gamma\cos\delta<\Gamma$.
*Proof.* For $T\in K$: $\langle y,T\rangle=-\kappa\langle b,T\rangle\le-\kappa\Gamma\cos\delta=\langle y,T^\flat\rangle$. ∎
So the exceptional set in C-3 cannot be shrunk.

**Remark (explicit maximizer, not needed later).** For $\|b\|=1$, $y\ne0$, and $\psi=\angle(y,b)\in[0,\pi)$: the maximizer is $\Gamma y/\|y\|$ if $\psi\le\delta$, and $\Gamma(\cos\delta\,b+\sin\delta\,\hat e)$ with $\hat e=\Pi_b y/\|\Pi_b y\|$ if $\delta<\psi<\pi$. The value is $h(y,b)=\Gamma\|y\|\cos((\psi-\delta)_+)$. This follows from C-3 plus the spherical triangle inequality $\angle(y,T)\ge\psi-\angle(b,T)$.

**Lemma J (joint ⇒ conditional).** If $(T^*,\Gamma^*)$ maximizes $\langle y,T\rangle-\beta\Gamma$ over $\{(T,\Gamma):T\in K_\Gamma(b),\ \rho_1\le\Gamma\le\rho_2\}$, then $T^*$ maximizes $\langle y,\cdot\rangle$ over $K_{\Gamma^*}(b)$. *(Trivial.)*

**Lemma L8 (lossless ⇒ original-feasible).** If $T\in K_\Gamma(b)$, $\|T\|=\Gamma$ and $\rho_1\le\Gamma\le\rho_2$, then $\rho_1\le\|T\|\le\rho_2$ and $\langle b,T\rangle\ge\|T\|\cos\delta$. *(Trivial.)*

**Lemma X (extreme points of the cap).** For $\Gamma>0$, $\|b\|=1$, $0\le\delta<\pi/2$, $\dim E\ge2$: $K_\Gamma(b)$ is compact and convex, its extreme points are exactly $S_\Gamma(b)$, and $K_\Gamma(b)=\operatorname{conv}S_\Gamma(b)$.
*Proof.* Compactness and convexity are clear. If $\|T\|<\Gamma$, pick $d\perp b$ with $d\ne0$ (possible since $\dim E\ge2$). Then $T\pm\varepsilon d\in K$ for small $\varepsilon$, so $T$ is not extreme. If $\|T\|=\Gamma$ and $T=\frac12(T_1+T_2)$ with $T_i\in K$, then $\|T_i\|\le\Gamma$ and the parallelogram law force $T_1=T_2$, so $T$ is extreme. Minkowski's theorem (finite dimension) gives $K=\operatorname{conv}\operatorname{ext}K$. ∎

---

## 3. Weak Theorem C (value and feasibility losslessness for ANY attitude profile)

**[Aumann]** (Aumann 1965). Let $F:[0,t_f]\rightrightarrows\mathbb R^n$ be measurable (Borel graph), nonempty, closed-valued, and integrably bounded. Then $\int F=\int\operatorname{conv}F$, where $\int F=\{\int f:\ f\text{ a measurable selection of }F\}$.

**Theorem C-W.** Let $b$ be any measurable attitude profile. Let $(T,\Gamma)$ be $\mathrm P_1(b;\theta)$-feasible with mass $m$. Then there is a measurable $\tilde T$ with $\tilde T(t)\in S_{\Gamma(t)}(b(t))$ a.e. such that $(\tilde T,\Gamma)$ is $\mathrm P_1$-feasible, has the **same** $\Gamma$, mass $m$ and cost, and its state equals that of $(T,\Gamma)$ at $t_f$ and at any prescribed finite set of times $0<t_1<\dots<t_M<t_f$. Hence:
1. $\mathrm P_0(b;\theta)$ is feasible iff $\mathrm P_1(b;\theta)$ is feasible, and $\inf\mathrm P_0=\inf\mathrm P_1$.
2. If $\mathrm P_1$ attains its minimum, so does $\mathrm P_0$, with the same value.
3. (1)–(2) hold with nodewise state constraints $x(t_i)\in X_i$ (arbitrary closed sets) and with the dry-mass constraint.
4. The same holds for the log-mass form with arbitrary $\sigma$-bounds depending only on $(t,z)$, in particular the convexified-mass model.

*Proof.* Since $\Gamma$ is unchanged, $m(t)=m_0-\alpha\int_0^t\Gamma$ is unchanged. The cost, the mass bounds and the dry-mass constraint are unchanged. On each subinterval $I_k=[t_k,t_{k+1}]$ (with $t_0=0$, $t_{M+1}=t_f$), the state increment is
$$x(t_{k+1})-\Phi_k x(t_k)-c_k=\int_{I_k}\Psi_k(s)\,\frac{T(s)}{m(s)}\,ds,\qquad \Psi_k(s)=\begin{pmatrix}(t_{k+1}-s)I_3\\ I_3\end{pmatrix},$$
which is linear in $T$ for the fixed $m$. Define $F_k(s)=\Psi_k(s)S_{\Gamma(s)}(b(s))/m(s)\subseteq\mathbb R^6$. It is measurable, nonempty (it contains $\Psi_k\Gamma b/m$), compact-valued, and bounded by $\rho_2\max\|\Psi_k\|/(m_0-\alpha\rho_2t_f)$. By Lemma X and linearity, $\operatorname{conv}F_k(s)=\Psi_k(s)K_{\Gamma(s)}(b(s))/m(s)\ni\Psi_k(s)T(s)/m(s)$. By [Aumann] there is a measurable selection $f$ of $F_k$ on $I_k$ with $\int_{I_k}f=\int_{I_k}\Psi_kT/m$. Since $\Psi_k(s)$ has full column rank, $\tilde T(s):=m(s)\Psi_k(s)^+f(s)$ is measurable, satisfies $\Psi_k\tilde T/m=f$, and lies in $S_{\Gamma(s)}(b(s))$, because $f(s)\in\Psi_k(s)S_{\Gamma(s)}(b(s))/m(s)$ and $\Psi_k(s)$ is injective. Concatenate over $k$. By induction the states agree at every $t_k$. Lossless implies original-feasible (L8). Since every $\mathrm P_0$-feasible $T$ gives the $\mathrm P_1$-feasible $(T,\|T\|)$, (1)–(3) follow. For (4), work in $(z,u,\sigma)$ with $\dot v=u+g$, which is linear in $u$ and independent of $z$. ∎

**Corollary C-W' (convex path constraints, value form).** Let the state constraint be $x(t)\in X$ for all $t$, with $X$ closed convex. Use constant mass or the convexified-mass model, so that $\mathrm P_1$ is a convex problem. Assume a **Slater point**: a $\mathrm P_1$-feasible solution $x^\circ$ with $\operatorname{dist}(x^\circ(t),X^c)\ge\eta>0$ for all $t$. Then $\inf\mathrm P_0=\min\mathrm P_1$.
*Proof.* Let $x^*$ be $\mathrm P_1$-optimal (existence: §9, Lemma 9.1). For $\lambda\in(0,1]$, $x^\lambda=(1-\lambda)x^*+\lambda x^\circ$ is $\mathrm P_1$-feasible, has cost $\le(1-\lambda)J^*+\lambda J^\circ$, and satisfies $B(x^\lambda(t),\lambda\eta)\subseteq X$ by convexity of $X$. Partition $[0,t_f]$ into intervals of length $h$ and apply Theorem C-W with nodes at the partition points. The resulting lossless $\tilde x$ agrees with $x^\lambda$ at the nodes and satisfies $\|\tilde x(t)-x^\lambda(t)\|\le C h$ in between, with $C=2\rho_2(1+h)/(m_0-\alpha\rho_2t_f)$, since both accelerations are bounded. Taking $Ch<\lambda\eta$ makes $\tilde x$ $\mathrm P_0$-feasible with cost $\le J^*+\lambda(J^\circ-J^*)$. Let $\lambda\to0$. ∎
(Attainment of $\mathrm P_0$ under active path constraints is not claimed. §5.5 gives the PMP version.)

**Corollary C-F (convexity of the fixed-attitude feasible set).** With constant mass ($\alpha=0$), or for the convexified-mass model, and with convex terminal set and convex nodewise state constraints (or none), the set $F_{t_f}(b)=\{\theta:\mathrm P_0(b;\theta)\text{ feasible}\}$ is **convex** for every measurable $b$.
*Proof.* $\{(\theta,T,\Gamma):\mathrm P_1\text{-feasible}\}$ is convex, since $\theta$ enters through an affine map and all constraints are convex. Its projection to $\theta$ is convex and equals $F_{t_f}(b)$ by C-W(1),(3). ∎ (With convex *path* constraints, the same argument plus C-W' shows that $F_{t_f}(b)$ contains every relaxed-feasible $\theta$ admitting a Slater point. Hence $F_{t_f}(b)$ lies between a convex set and its "Slater core".)

This settles the "with cone: open" entry of Claim P-3 (`math/02` §8) for constant mass, for any fixed cone, even a time-varying one. With exact (non-Taylor) mass dynamics, convexity of $F(b)$ is open (§11). The convex-combination step fails there because $\sigma\le\rho_2e^{-z}$ is not convex in $z$.

---

## 4. Exchange proposition: lossiness only at minimum throttle (PMP-free)

**Proposition C-E.** (a) *Constant mass.* Let $(T^*,\Gamma^*)$ be $\mathrm P_1$-optimal. Then $|\{t:\|T^*(t)\|<\Gamma^*(t),\ \Gamma^*(t)>\rho_1\}|=0$. Every lossy instant is a minimum-throttle instant, at which the relaxation is "throttling below $\rho_1$".
(b) *Log-mass, any $\sigma$-bounds $\mu_1(t,z)\le\sigma\le\mu_2(t,z)$ nonincreasing in $z$, cost $-z(t_f)$, no terminal constraint on $z$ other than $z(t_f)\ge z_{dry}$.* Let $(u^*,\sigma^*,z^*)$ be optimal. Let $E\subseteq\{t:\|u^*\|<\sigma^*,\ \sigma^*>\mu_1(t,z^*)\}$ with $|E|>0$, and $\tau=\operatorname{ess\,inf}E$. Then there is no $\eta>0$ with $\sigma^*(s)\le\mu_2(s,z^*(s)+\eta)$ for a.e. $s\ge\tau$. In words: a lossy, above-minimum arc must be followed by an arc where the upper thrust bound is (asymptotically) saturated.

*Proof.* (a) Put $\Gamma'=\max(\rho_1,\|T^*\|)$ on the set and $\Gamma'=\Gamma^*$ elsewhere. Then $\|T^*\|\le\Gamma'\le\Gamma^*$, so $\langle b,T^*\rangle\ge\Gamma^*\cos\delta\ge\Gamma'\cos\delta$ (using $\cos\delta\ge0$), and $\rho_1\le\Gamma'\le\rho_2$. The trajectory is unchanged because $T$ and $m$ are unchanged, and the cost strictly decreases if the set has positive measure. Contradiction.
(b) Suppose such an $\eta$ exists. For $\varepsilon>0$ let $E_\varepsilon=\{t\in E:\ \sigma^*-\max(\|u^*\|,\mu_1(t,z^*))\ge\varepsilon\}$. Since $E=\bigcup_n E_{1/n}$ (up to null sets) and $|E|>0$, some $E_\varepsilon$ has positive measure. Choose a measurable $E'\subseteq E_\varepsilon$ with $0<|E'|\le\eta/(\alpha\varepsilon)$. Note $\operatorname{ess\,inf}E'\ge\tau$. Set $u'=u^*$ and $\sigma'=\sigma^*-\varepsilon\mathbf 1_{E'}$. Then $z'(t)=z^*(t)+\alpha\varepsilon|E'\cap[0,t]|\in[z^*,z^*+\eta]$, and $z'=z^*$ before $E'$. Check the constraints: (norm) $\sigma'\ge\|u^*\|$ on $E'$ by the choice of $E_\varepsilon$; (pointing) $\langle b,u^*\rangle\ge\sigma^*\cos\delta\ge\sigma'\cos\delta$; (lower bound) $\sigma'\ge\mu_1(t,z^*)\ge\mu_1(t,z')$, using monotonicity of $\mu_1$ in $z$; (upper bound) for $t\ge\tau$, $\sigma'\le\sigma^*\le\mu_2(t,z^*+\eta)\le\mu_2(t,z')$ by hypothesis and monotonicity, and before $\tau$ nothing changed; (dry mass) $z'(t_f)\ge z^*(t_f)$. $(r,v)$ are unchanged because $u$ is unchanged. But $z'(t_f)=z^*(t_f)+\alpha\varepsilon|E'|>z^*(t_f)$, which contradicts optimality. ∎

**Data point.** `context/vehicle.md` reports that the stored GTPL LCvx solutions are *not* tight on the min-thrust arc ($m\|u\|=296$ N vs $m\sigma=400$ N). That is exactly the C-E(a) mechanism: thrust below $\rho_1$ disguised as $\Gamma=\rho_1$. The present theory predicts it cannot happen above min throttle. The fix is §5–§7 (diagnose by the primer test, repair by purification or Aumann).

---

## 5. Strong Theorem C (every relaxed optimum is lossless), under PMP

### 5.1 The PMP hypothesis
State $x=(r,v,m)$, control $(T,\Gamma)\in U(t):=\{T\in K_\Gamma(b(t)),\ \rho_1\le\Gamma\le\rho_2\}$, Hamiltonian
$$H(t,x,T,\Gamma,\lambda_0,\lambda)=\lambda_0\Gamma+\langle\lambda_r,v\rangle+\langle\lambda_v,T/m+g\rangle-\alpha\lambda_m\Gamma .$$

**(H-PMP)** For the given $\mathrm P_1$-optimal $(x^*,T^*,\Gamma^*)$ there exist $\lambda_0\in\{0,1\}$ and an absolutely continuous $\lambda=(\lambda_r,\lambda_v,\lambda_m):[0,t_f]\to\mathbb R^7$, with $(\lambda_0,\lambda)\not\equiv0$, such that:
- (i) adjoint: $\dot\lambda_r=0$, $\dot\lambda_v=-\lambda_r$, $\dot\lambda_m=\langle\lambda_v,T^*\rangle/m^{*2}$ a.e.;
- (ii) minimum condition: for a.e. $t$, $(T^*(t),\Gamma^*(t))$ minimizes $H(t,x^*(t),\cdot,\cdot,\lambda_0,\lambda(t))$ over $U(t)$;
- (iii) transversality: $\lambda_m(t_f)=-\nu$ with $\nu\ge0$ and $\nu\,(m^*(t_f)-m_{dry})=0$ ($\nu=0$ if there is no dry-mass constraint). $(\lambda_r,\lambda_v)(t_f)$ are free, since the terminal state is fixed.

This is the standard PMP for a measurable control multifunction $U(\cdot)$. Context only (not used as proof): Vinter, *Optimal Control* (2000), Thm 6.2.1. The Lean development takes (H-PMP)(i)–(ii) as the only labelled hypothesis.

**Primer vector.** $p(t):=-\lambda_v(t)$. By (i), $\dot p=\lambda_r$ is constant, so
$$p(t)=a+ct\qquad(a,c\in\mathbb R^3).$$
Neither mass nor time-variation of $b$ enters the $(r,v)$ adjoint. Affinity of the primer holds for **every** $b$.

### 5.2 The theorem
**Theorem C-S.** Assume (H-PMP). Let $D=\{t:\ p(t)\in-\mathbb R_{\ge0}b(t)\}$. Then:
1. For a.e. $t\notin D$: $\|T^*(t)\|=\Gamma^*(t)$, and $T^*(t)$ is the unique maximizer of $\langle p(t),\cdot\rangle$ over $K_{\Gamma^*(t)}(b(t))$.
2. If $p\equiv0$, then $\Gamma^*=\rho_1$ a.e.
3. (Constant mass, $\alpha=0$.) If $p(t)=-\kappa b(t)$ with $\kappa>0$, then $\Gamma^*(t)=\rho_1$ (a.e. on such $t$). Hence the lossy set satisfies
$$L:=\{t:\|T^*\|<\Gamma^*\}\ \subseteq\ D\cap\{\Gamma^*=\rho_1\}\pmod{\text{null}} .$$
4. If $|D|=0$, every relaxed optimum is lossless and $\mathrm P_0$-optimal.

*Proof.* (1) Fix $\Gamma=\Gamma^*(t)$ in (ii). $T^*(t)$ minimizes $\langle\lambda_v,T\rangle/m$, i.e. maximizes $\langle p(t),T\rangle$ (since $m>0$), over $K_{\Gamma^*}(b)$ (Lemma J). Apply C-3 and U.
(2) $p\equiv0$ gives $\lambda_v\equiv0$, hence $\lambda_r=\dot p\equiv0$ and $\dot\lambda_m\equiv0$, so $\lambda_m\equiv-\nu$. Then $H$ restricted to the controls is $(\lambda_0+\alpha\nu)\Gamma$. Nontriviality gives $(\lambda_0,\nu)\ne0$. If $\alpha>0$, then $\lambda_0+\alpha\nu>0$. If $\alpha=0$, drop $m$ from the state; nontriviality gives $\lambda_0=1$. In both cases the minimum over $U(t)$ forces $\Gamma^*=\rho_1$.
(3) With $\alpha=0$, minimizing over $T\in K_\Gamma(b)$ for fixed $\Gamma$ gives $\min_T\langle\lambda_v,T\rangle/m=\kappa\Gamma\cos\delta/m$ (Lemma S). So $\min_{U(t)}H=\min_{\Gamma\in[\rho_1,\rho_2]}(\lambda_0+\kappa\cos\delta/m)\Gamma$. The coefficient is $>0$ since $\delta<\pi/2$, which forces $\Gamma^*=\rho_1$. Combine with (1), (2) and C-E(a).
(4) Lossless implies $\mathrm P_0$-feasible with equal cost (L8), and $\inf\mathrm P_0\ge\min\mathrm P_1$. ∎

*Remark (mass).* With $\alpha>0$, the $\Gamma$-coefficient at $t\in D^+$ is $\lambda_0-\alpha\lambda_m(t)+\kappa\cos\delta/m$, and its sign is not forced. In the relaxation, "propellant dumping" ($\|T\|<\Gamma$ at high $\Gamma$) is excluded only by C-E(b). Part (1) holds regardless.

### 5.3 Exact structure of the degenerate set (Claim C-D)
Write $D=Z\cup D^+$, with $Z=\{p=0\}$ and $D^+=\{p\ne0,\ b=-p/\|p\|\}$.

**Proposition C-D1.** Let $(a,c)\ne0$.
- (a) $|Z|\le1$ (at most one point).
- (b) If $a,c$ are linearly dependent, $p(t)=\varphi(t)e$ with $\|e\|=1$ and $\varphi$ affine, so $D^+\subseteq b^{-1}(\{e\})\cup b^{-1}(\{-e\})$.
- (c) If $a,c$ are independent, $D^+\subseteq\{t:b(t)=\beta(t)\}$ with $\beta(t)=-\frac{a+ct}{\|a+ct\|}$.

*Proof.* (a) Two zeros $t\ne t'$ give $c(t-t')=0$, so $c=0=a$. (b) and (c) are immediate. ∎

**Definition (gnomonic lines).** $\mathcal A=\{t\mapsto (a+ct)/\|a+ct\|:\ a,c\text{ independent}\}$ is the set of central projections onto $S^2$ of uniform rectilinear motions not through the origin. Each $\beta\in\mathcal A$ runs monotonically along a great circle. With $\Omega=\|c\|/d$, $d=\|a\times c\|/\|c\|$ and $t^*=-\langle a,c\rangle/\|c\|^2$, its angle along the circle is $\theta(t)=\theta_0+\arctan(\Omega(t-t^*))$ and its speed is
$$\|\dot\beta(t)\|=\frac{\|a\times c\|}{\|a+ct\|^2}=\frac{\Omega}{1+\Omega^2(t-t^*)^2}.$$
Note $-\mathcal A=\mathcal A$.

**Non-degeneracy conditions on $b$ (checkable a priori, no multipliers):**
- (ND1) every level set $b^{-1}(\{e\})$ is null ("$b$ never dwells");
- (ND2) for every $\beta\in\mathcal A$, $\{t:b(t)=\beta(t)\}$ is null ("$b$ never follows a gnomonic line").

**Corollary C-D2.** Under (H-PMP), (ND1) and (ND2): either $p\equiv0$ (and then $\Gamma^*\equiv\rho_1$), or every relaxed optimum is lossless. In particular, if additionally the **min-throttle problem is infeasible**, i.e. $\mathrm P_1$ with $\Gamma\equiv\rho_1$ (a convex feasibility problem) has no solution, then every relaxed optimum is lossless and optimal. A posteriori, $\Gamma^*>\rho_1$ on a set of positive measure also suffices.

**Proposition C-D3 (checkable criteria).**
- (a) If $b\in C^2$ and $\{t:\dot b=0\}$ and $\{t:\dot b\ne0,\ \det(b,\dot b,\ddot b)=0\}$ are null, then (ND1) and (ND2) hold.
- (b) If $b$ is real-analytic on $[0,t_f]$: (ND1) ⇔ $b$ is not constant. If $\det(b,\dot b,\ddot b)\not\equiv0$ (i.e. $b$ is not a great-circle motion), (ND2) holds. If $b$ moves on a great circle (nonconstant), (ND2) fails iff $1/\|\dot b(t)\|=At^2+Bt+C$ with $A>0$ and $4AC-B^2=4$ (and $b$ does not reverse direction).
- (c) Typical profiles are non-degenerate: constant-rate slews ($1/\|\dot b\|$ constant), bang-bang-acceleration slews ($\|\dot b\|$ piecewise linear), and any non-planar analytic profile. The degenerate profiles include $b=\pm$ (3DOF primer direction). For those, C-S(3) still gives $L\subseteq\{\Gamma^*=\rho_1\}$, and C-D4 below gives more.

*Proof.* (a) If $b=\beta$ on $E$ with $|E|>0$, then almost every $t_0\in E$ is an accumulation point of $E$. Componentwise Rolle between zeros of $b-\beta$ accumulating at $t_0$ gives $(b-\beta)'(t_0)=0$, and applying Rolle again, $(b-\beta)''(t_0)=0$. For $\beta\in\mathcal A$: $\dot\beta\ne0$ and $\det(\beta,\dot\beta,\ddot\beta)=0$ (great circle), so $t_0$ lies in the second null set. Contradiction. For a level set: $\dot b(t_0)=0$, so $t_0$ lies in the first null set. (b) Zero sets of analytic functions on an interval are finite or everything. If $\det(b,\dot b,\ddot b)\equiv0$ and $b\times\dot b\ne0$ somewhere, then $\frac{d}{dt}(b\times\dot b)=b\times\ddot b\in\operatorname{span}(b\times\dot b)$, so the normal is constant and $b$ is planar. The speed law of $\mathcal A$ is $1/\|\dot\beta\|=\Omega^{-1}+\Omega(t-t^*)^2$, i.e. $A=\Omega$, $B=-2\Omega t^*$, $C=\Omega^{-1}+\Omega t^{*2}$, so $4AC-B^2=4$. Conversely, a planar monotone curve with this speed law is $\cos\theta\,m_1+\sin\theta\,m_2$ with $\theta=\theta_0+\arctan(\Omega(t-t^*))$, which lies in $\mathcal A$. (c) follows from (a)/(b). ∎

**Proposition C-D4 (degeneracy is meagre).** In $C^0([0,t_f];S^2)$ with the sup norm, the set of $b$ violating (ND1) or (ND2) is of first category.
*Proof.* Normalize $\|(a,c)\|=1$. For $\varepsilon>0$ let $\mathcal B_\varepsilon=\{b:\exists(a,c)\in S^5,\ |D^+_{a,c}(b)|\ge\varepsilon\}$.
- *Closed:* take $b_n\to b$ uniformly, $(a_n,c_n)\to(a,c)$ by compactness, $E_n=D^+_{a_n,c_n}(b_n)$, and $E=\limsup E_n$. Then $|E|\ge\limsup|E_n|\ge\varepsilon$ (finite measure). For $t\in E$ with $p(t)\ne0$ (all but $\le1$ point), $\hat p_n(t)\to\hat p(t)$ along the indices with $t\in E_n$, so $b(t)=-\hat p(t)$.
- *Empty interior:* polynomial curves $q$ with $\det(q,q',q'')(t_0)\ne0$ are dense (Weierstrass plus a small perturbation). For $\|q-b\|_\infty$ small, $q/\|q\|$ is analytic and non-planar, so it satisfies (ND1) and (ND2) by C-D3(b).

So $\mathcal B_\varepsilon$ is nowhere dense, and the bad set $\bigcup_n\mathcal B_{1/n}$ is meagre. ∎
*Finite-dimensional version.* For $b=q/\|q\|$ with $q$ a polynomial of degree $n\ge2$ per piece, the bad coefficient set lies in the proper algebraic subset $\{\det(q,q',q'')\equiv0\}$, so it has Lebesgue measure zero.

### 5.4 Free final time
If $t_f$ is free (and optimized), $b$ is Lipschitz (true for rate-limited attitude), and the free-endpoint PMP adds $\min_U H(t_f)=0$, then $p\equiv0$ is impossible. Indeed, if $p\equiv0$ then $\min_UH=(\lambda_0+\alpha\nu)\rho_1$ is independent of $b$ and $t$, and it vanishes only if $\lambda_0=\nu=0$, contradicting nontriviality. *(Hypothesis: the free-time PMP, as a labelled extension of (H-PMP).)*

### 5.5 State constraints (glide slope etc.)
- *Discrete time / nodewise constraints:* exact. See C-W(3) and §7: the discrete primer picks up the state-constraint multipliers, and the nodewise test is unchanged.
- *Continuous path constraints, strong form:* with the state-constrained PMP (measure multiplier, labelled hypothesis (H-PMP-S)), $\lambda_v$ is absolutely continuous and $\lambda_r$ is BV, and the minimum condition is still pointwise over $U(t)$. So C-S(1) holds verbatim with $p=-\lambda_v$, which is now continuous and **affine on every open interval where the constraint is inactive**. C-D1 to C-D3 apply interval-by-interval. On boundary arcs $p$ has no a priori structure. There the condition $p\notin-\mathbb R_{\ge0}b$ is checked a posteriori from duals. In value, C-W' always applies.

---

## 6. Sharpness: a genuine lossy optimum (Claim C-X)

Constant mass $m=1$, gravity $g=-g_0e_z$, fixed upright axis $b\equiv e_z$ (this is the ACB-2013 fixed cone), $0<\delta<\pi/2$, $\rho_1<g_0<\rho_2$, start at rest at height $h$, land at rest at $t_f$, lateral data zero.

*Facts.* (1) With purely vertical thrust $T_z\in[\rho_1,\rho_2]$ and $\int T_z=g_0t_f$, the largest height that can be lost is $D(\rho_1)$, where $D(s)=\tfrac12(g_0-s)\,t_1(s)\,t_f$ and $t_1(s)=t_f(\rho_2-g_0)/(\rho_2-s)$ ("fall at $s$, brake at $\rho_2$"). (2) The relaxed problem allows $T_z\in[\Gamma\cos\delta,\Gamma]$ with zero lateral thrust, so it can lose up to $D(\rho_1\cos\delta)>D(\rho_1)$.

Take $h\in(D(\rho_1),D(\rho_1\cos\delta)]$. Every relaxed-feasible solution needs $T_z<\rho_1$ on a set of positive measure, where $\Gamma\ge\rho_1>T_z$.
- **Relaxed optimum is lossy.** The solution with $T=(0,0,T_z)$ and $\Gamma=\max(\rho_1,T_z)$ is feasible. It is optimal, because the cost $\int\max(\rho_1,T_z)$ is a lower bound for every relaxed-feasible solution with the same vertical profile, and the vertical profile problem is a 1D convex problem. On the set where $T_z<\rho_1$ it has $\|T\|<\Gamma$.
- **The relaxation is rotation-symmetric about $e_z$** and the optimal face is invariant. In the discretized SOCP with the standard rotation-invariant barriers, each central-path point is the unique minimizer of a strictly convex rotation-invariant problem. It is therefore rotation-invariant, so its lateral thrust is $0$. The same holds for the limit. An interior-point method thus returns a **lossy** optimum.
- **The primer.** The optimum is lossy on a set of positive measure. By C-S(1), *any* PMP multiplier of it must have $p(t)\in-\mathbb R_{\ge0}e_z$ on that set, so $|D|>0$ (here $b$ is constant: (ND1) fails). This is the exact C-S/C-D failure mode.
- **Losslessness in value nevertheless holds (C-W).** Coning lateral thrust of magnitude $\sqrt{\rho_1^2-T_z^2}$ with zero net lateral impulse and moment realizes the same cost exactly. In discrete time, §7 gives such a solution with at most $3$ lossy nodes.
- With a **rate-limited gimbal** (M2) coning is unavailable and the cheat is a genuine infeasibility. With TVC torque coupling (M3b) the fixed upright cone forces $\delta_{\rm eff}=0$ (§8), which makes the instance infeasible for $h>D(\rho_1)$.

So the exceptional set in C-S cannot be removed, and the GTPL observation in §4 is this phenomenon.

---

## 7. Discrete time (what the flight code actually solves) — Claim C-K

Grid $t_j=jh$, $N h=t_f$, controls $u_j$ (ZOH or FOH), throttles $\sigma_j$, log-mass $z$ depending only on $\sigma$, cone $C_j(\sigma)=K_\sigma(b_j)$, translational state $x_i=\text{affine}+\sum_{j}M_{ij}u_j$, constraints $x_i\in X_i$ (closed convex; $X_N$ the terminal set), any $\sigma$-bounds in $(j,z)$, and cost $f(\sigma,z)$.

**Theorem C-K1 (nodewise KKT test).** Assume the discrete relaxed SOCP satisfies Slater, so KKT holds. Let $\nu_i\in N_{X_i}(x_i^*)$ be the state multipliers and $p_j:=-\sum_iM_{ij}^\top\nu_i$. Then $u_j^*$ maximizes $\langle p_j,\cdot\rangle$ over $K_{\sigma_j^*}(b_j)$. Hence **$\|u_j^*\|=\sigma_j^*$ at every node with $p_j\notin-\mathbb R_{\ge0}b_j$**, and $u_j^*$ is unique there. Without state constraints and with ZOH,
$$p_j=-h\big(\nu_v+(t_f-t_j-\tfrac h2)\nu_r\big)$$
is affine in $t_j$, so C-D1 applies verbatim. With FOH it is also affine at interior nodes.
*Proof.* Stationarity in $(u_j,\sigma_j)$ gives $(p_j,\cdot)\in N_{\{(u,\sigma):u\in K_\sigma(b_j),\ \sigma\in\text{bounds}\}}(u_j^*,\sigma_j^*)$. Restricting to $\sigma=\sigma_j^*$ gives $\langle p_j,u-u_j^*\rangle\le0$ on $K_{\sigma_j^*}(b_j)$. Apply C-3 and U. ∎

**Theorem C-K2 (purification: at most $\tfrac12\sum c_i$ lossy nodes, no assumptions).** Suppose the discrete relaxed problem has an optimum $(u^*,\sigma^*,z^*)$. Let $S=\{u:u_j\in K_{\sigma_j^*}(b_j)\ \forall j,\ x_i(u)\in X_i\ \forall i\}$, which is compact, convex and nonempty. Every $u\in S$ gives an optimal solution, since cost and mass depend only on $\sigma^*$. Every extreme point $\bar u$ of $S$ has
$$\#\{j:\|\bar u_j\|<\sigma_j^*\}\ \le\ \tfrac12\textstyle\sum_i c_i,$$
where $c_i$ is the codimension in $\mathbb R^6$ of the minimal face of $X_i$ containing $x_i(\bar u)$. Values: $c_N=6$ for $X_N=\{0\}$; $c_i=0$ for an inactive constraint; $c_i=2$ when a circular glide-slope cone is active at a non-apex point; $c_i=3$ at the apex. **Without state constraints: at most 3 lossy nodes.** A maximizer of a generic linear functional over $S$ is unique, hence extreme. So one extra SOCP (fix $\sigma=\sigma^*$, maximize a random linear objective) produces such a $\bar u$ with probability 1.
*Proof.* Let $J$ be the set of lossy nodes. For $j\in J$, every $d\in b_j^\perp$ (a 2-dimensional space) satisfies $\bar u_j\pm\varepsilon d\in K_{\sigma_j^*}(b_j)$ for small $\varepsilon$, because $\|\bar u_j\|<\sigma_j^*$ and $\langle b_j,d\rangle=0$. Since $x_i(\bar u)\in\operatorname{ri}F_i$, a two-sided move $x_i\pm\varepsilon\,\delta x_i$ stays in $X_i$ iff $\delta x_i\in\operatorname{lin}F_i$. That is $c_i$ linear conditions. The linear map $\bigoplus_{j\in J}b_j^\perp\to\prod_i\mathbb R^6/\operatorname{lin}F_i$ has domain dimension $2|J|$ and target dimension $\sum c_i$. If $2|J|>\sum c_i$, it has a nonzero kernel element $\delta u$ with $\bar u\pm\varepsilon\delta u\in S$, so $\bar u$ is not extreme. Generic uniqueness: the support function of a compact convex set is differentiable a.e. (convex, hence Rademacher), and at points of differentiability the maximizer is unique. ∎

*Practical reading (deferred work, recorded only).* After any LCvx solve with a time-varying cone: (1) if $\Gamma^*>\rho_1$ wherever $\|u^*\|<\sigma^*$ fails, C-E is violated, which indicates a solver tolerance issue; (2) compute $p_j$ from the duals and flag nodes with $\angle(p_j,-b_j)\approx0$; (3) purify (C-K2). This removes the GTPL min-thrust-arc looseness up to $\le3$ nodes (or $\tfrac12\sum c_i$).

---

## 8. Gimbal-torque-coupled 6DOF TVC (M3b): exact convexity given attitude — Claim C-6

**Model M3b.** Axisymmetric rigid body with transverse inertia $J_\perp$, gimbal lever arm $\ell$ (gimbal at $-\ell b$ from the CG), $J_\perp$ and $\ell$ constant, $k:=J_\perp/\ell$. Pitch/yaw torque comes only from the gimbal: $\tau=(-\ell b)\times T=\ell\,T\times b$. Roll RCS holds roll rate $\omega_3=\langle\omega,b\rangle\equiv0$ (for axisymmetric $J$ this needs no roll torque). Gimbal: $\angle(T,b)\le\delta$ (cone; a body-fixed box is handled identically, see below). Constant mass $m$. Attitude limits are arbitrary constraints on $b(\cdot)$ alone (rate, acceleration, boundary attitude and rate).

**Lemma 8.1 (torque balance).** With $\omega_3\equiv0$, $\omega=b\times\dot b$, and the angular momentum is $J_\perp\omega$. Euler's equation is $J_\perp\,b\times\ddot b=\ell\,T\times b$, which is equivalent to
$$\Pi_bT=-k\,\Pi_b\ddot b,\qquad \Pi_b:=I-bb^\top .$$
*Proof.* $\frac{d}{dt}(J_\perp b\times\dot b)=J_\perp b\times\ddot b$. Write $T=\langle b,T\rangle b+\Pi_bT$ and $\ddot b=\langle b,\ddot b\rangle b+\Pi_b\ddot b$. Then $(\Pi_bT+k\Pi_b\ddot b)\times b=0$ with both terms $\perp b$, so the sum is $0$. Conversely, the identity gives Euler's equation. ∎
*(Consequence: thrust deflected toward $+x$ relative to the body rotates the body toward $-x$. This is the non-minimum-phase TVC behaviour noted by [adversary-6dof].)*

**Theorem C-6.** Fix $b\in W^{2,\infty}([0,t_f];S^2)$ satisfying the attitude limits. Put $F(t)=-k\Pi_b\ddot b$ and $\varkappa(t)=\|F(t)\|$. The exact 6DOF problem with this attitude is
$$\min\ \textstyle\int\phi(T_a,\varkappa)\ \text{ s.t. }\ \ddot r=(T_a b+F)/m+g,\quad T_a(t)\in[L(t),U(t)],\ \text{BCs},$$
with $L=\max\{\varkappa\cot\delta,\ \sqrt{(\rho_1^2-\varkappa^2)_+}\}$, $U=\sqrt{\rho_2^2-\varkappa^2}$ (feasible iff $L\le U$ a.e.), and fuel integrand $\phi=\sqrt{T_a^2+\varkappa^2}$. This is a **convex** program in $T_a$, with linear dynamics and a convex cost, and it is **exact: no relaxation is involved**. Consequently $F^{M3b}_{t_f}(b)$ is convex for every attitude profile $b$. For a body-fixed box gimbal, the interval constraint becomes $|\langle F,e_{x,y}^{body}\rangle|\le T_a\tan\delta_{box}$, which is still linear in $T_a$.
*Proof.* By 8.1, $T=T_ab+F$ with $T_a=\langle b,T\rangle$. Gimbal: $\angle(T,b)\le\delta\iff T_a>0$ and $\varkappa\le T_a\tan\delta$. Throttle: $\rho_1^2\le T_a^2+\varkappa^2\le\rho_2^2$ with $T_a\ge0$, which is an interval in $T_a$. The dynamics are affine in $T_a$ for fixed $b$. $\phi$ is the norm of an affine map, hence convex. The $\theta$-feasible set is the projection of a convex set. ∎
*(Variable mass: $F/m$ and $J_\perp(m)$ make the problem nonconvex in $m$ even for fixed $b$. Stated for constant or prescribed mass only.)*

**Corollary 8.2 (fixed-cone ACB-2013 under TVC).** If $b\equiv e_z$ (body held upright), Lemma 8.1 forces $\Pi_bT=0$, i.e. $T\parallel e_z$: the effective cone is $\delta_{\rm eff}=0$. The upright-body/15°-cone formulation is therefore **not** 6DOF-feasible for any trajectory that uses off-vertical thrust. This proves orchestrator caveat (1).

---

## 9. Per-instance exactness and the union structure — Claim C-U

Let $\mathcal B$ be the set of admissible attitude profiles: for M1, angle-Lipschitz $(AL_\omega)$ with boundary attitude conditions (`math/02` §1.2); for M3b, $W^{2,\infty}$ with rate/acceleration limits. Let $V(b;\theta)=\inf\mathrm P_0(b;\theta)$ and $V(\theta)=\inf_{b\in\mathcal B}V(b;\theta)$ (the 5DOF/6DOF optimum).

**Lemma 9.1 (existence; M1, constant mass).** If $F^{M1}_{t_f}\ni\theta$, the 5DOF problem attains its minimum.
*Proof.* Take a minimizing sequence $(b_n,T_n,\Gamma_n)$ (relaxed). $\mathcal B$ is compact in $C^0$ (Arzelà–Ascoli; $(AL_\omega)$ is closed under uniform limits). $(T_n,\Gamma_n)$ is bounded in $L^\infty$, so after passing to subsequences, $b_n\to b$ uniformly and $(T_n,\Gamma_n)\rightharpoonup^*(T,\Gamma)$. The constraints $\|T\|\le\Gamma$ and $\rho_1\le\Gamma\le\rho_2$ are convex and closed, hence weak*-closed. For the cone: $\int\varphi(\langle b_n,T_n\rangle-\Gamma_n\cos\delta)\ge0$ for all $\varphi\ge0$ in $L^1$. Since $\|b_n-b\|_\infty\|T_n\|_\infty\to0$, the limit gives $\int\varphi(\langle b,T\rangle-\Gamma\cos\delta)\ge0$, hence the constraint holds a.e. The dynamics and BCs are weak*-continuous and the cost is linear. Apply C-W at $b$ to obtain a lossless minimizer. ∎

**Theorem C-U.**
1. **Union structure.** $F_{t_f}=\bigcup_{b\in\mathcal B}F_{t_f}(b)$, with each $F_{t_f}(b)$ convex (C-F for M1, constant mass or convexified mass; C-6 for M3b, constant mass).
2. **Per-instance exactness.** If $(T^*,b^*)$ is a 5DOF optimum for $\theta$ (it exists in M1, constant mass, by 9.1), then the convex program $\mathrm P_1(b^*;\theta)$ (M1) or the program of C-6 at $b^*$ (M3b) has optimal value $V(\theta)$. Every lossless optimal solution of it is 5DOF-optimal. In M1, under (ND1)–(ND2) at $b^*$ and the min-throttle exclusion (C-D2), every optimal solution is lossless; in any case one can be produced by C-K2/C-W. In M3b no relaxation is involved at all.
3. **Inner approximation.** For any fixed $b$, the convex relaxation $\mathrm P_1(b;\cdot)$ is a *uniform* convex relaxation, in the sense of `math/02` Def. 1.3, of the restricted problem. Its feasible set $F(b)$ is a convex **inner** approximation of $F$, exact in value on $\Theta_b=\{\theta:V(b;\theta)=V(\theta)\}$.

*Proof.* (1) $\theta\in F$ iff some $b$ admits a feasible $T$. (2) $V(\theta)\le V(b^*;\theta)\le\text{cost}(T^*)=V(\theta)$, and $\min\mathrm P_1(b^*)=V(b^*)$ by C-W. (3) is a restatement. ∎

### 9.3 Consistency with the impossibility claims
Claims A/B/Q/L assert that $F$ (a union of convex sets) is nonconvex. C-U says the nonconvexity lives *entirely* in the choice of attitude profile. Each $F(b)$ is convex, and $\theta\mapsto b^*(\theta)$ is where convexity breaks. A non-uniform relaxation, i.e. one whose constraint set depends on $\theta$ through $b^*(\theta)$, is not covered by Thm A, and C-U shows it is exact. This matches the remark in `math/00` §4 and the asymptotics in `math/02` §5 (gap $\to0$ as $\omega\to0$; at $\omega=0$ the problem is fixed-$b$, where C-F gives convexity). It also matches C-E/C-S: both the relaxation's lossiness and the Thm B witness live on minimum-throttle arcs. **No contradiction found.**

---

## 10. When the uniform 3DOF LCvx is already 5DOF/6DOF-exact — Claims C-3D, C-Y

Let $\mathrm P_3(\theta)$ be the 3DOF problem: the same constraints, cost, and state/terminal constraints, but with no attitude and no gimbal cone. Let $V_3$ be its value. It is lossless by the $b$-free case of the lemmas: take $Q=E$ in C-G, so lossy instants need $p=0$.

**Theorem C-3D (exact characterization, M1).** $V_3(\theta)\le V(\theta)$ always. Assume both minima are attained. Then
$$V(\theta)=V_3(\theta)\iff\text{some 3DOF optimum }T_3\text{ is }\delta\text{-trackable: }\exists b\in\mathcal B,\ \langle b(t),T_3(t)\rangle\ge\|T_3(t)\|\cos\delta\ \text{a.e.}$$
In that case $T_3$ is 5DOF-optimal, and $\mathrm P_1(b;\theta)$ is exact for the tracking $b$. If the 3DOF optimum is unique and $V=V_3$, the 3DOF optimum is necessarily trackable.
*Proof.* Every 5DOF-feasible solution is 3DOF-feasible with the same cost, so $V_3\le V$. (⇐) A trackable optimum is 5DOF-feasible with cost $V_3$. (⇒) A 5DOF optimum is 3DOF-feasible with cost $V=V_3$, so it is 3DOF-optimal and trackable by its own $b$. ∎

**Proposition C-3D' (closed-form primer-arc certificate).** No state constraints, 3DOF without a pointing cone, (H-PMP) for $\mathrm P_3$ with primer $p=a+ct$, and $\min_{[0,t_f]}\|p\|>0$. Then $T_3(t)=\Gamma_3(t)\,\hat p(t)$ a.e., by C-G with $Q=E$ (lossy only where $p=0$). Define
$$\omega_{\rm req}=\frac{\|a\times c\|}{\min_{t\in[0,t_f]}\|a+ct\|^2},\qquad \varepsilon_0=\angle(b_0,\hat p(0)).$$
- (a) *Free terminal attitude.* If $\omega_{\rm req}\le\omega$ and $\varepsilon_0\le\delta$, then $\theta\in\Theta_{\rm exact}^{M1}$, and $V=V_3$.
- (b) *Upright landing $b(t_f)=e_z$.* With $\varepsilon_1=\angle(\hat p(t_f),e_z)$: if $\omega_{\rm req}+(\varepsilon_0+\varepsilon_1)/t_f\le\omega$ and $2\varepsilon_0+\varepsilon_1\le\delta$, the same conclusion holds.
- (c) *Angular acceleration demanded by the 3DOF profile* (needed for M3a envelope models): $\dot\omega=-2\|a\times c\|\langle p,c\rangle/\|p\|^4$, with $\sup_{\mathbb R}|\dot\omega|=\frac{3\sqrt3}{8}\Omega^2$, $\Omega=\|c\|^2/\|a\times c\|$.

*Proof.* $\hat p$ moves on a great circle with speed $\|a\times c\|/\|p\|^2\le\omega_{\rm req}$ on $[0,t_f]$. (a) Let $R_0$ be the rotation by $\varepsilon_0$ taking $\hat p(0)$ to $b_0$, and put $b=R_0\hat p$. Then $b(0)=b_0$, $\|\dot b\|=\|\dot{\hat p}\|\le\omega$, and $\angle(b,\hat p)\le\varepsilon_0\le\delta$ (a rotation by $\varepsilon$ moves unit vectors by at most $\varepsilon$). Prop. 1.2 of `math/02` gives $(AL_\omega)$. (b) Use $b=R(t)\hat p$, with $R$ the constant-speed geodesic in $SO(3)$ from $R_0$ to $R_1$, where $R_1\hat p(t_f)=e_z$ and $R_1$ is a rotation by $\varepsilon_1$. Then $d(I,R(t))\le d(I,R_0)+d(R_0,R_1)\le2\varepsilon_0+\varepsilon_1$, and $\|\dot b\|\le\|\dot R\|+\|\dot{\hat p}\|\le(\varepsilon_0+\varepsilon_1)/t_f+\omega_{\rm req}$. (c) $\|p\|^2=d^2+\|c\|^2s^2$ with $s=t-t^*$, so $\omega=\Omega_0/(1+x^2)$ with $\Omega_0=\|c\|/d$ and $x=\|c\|s/d$, and $\dot\omega=-2\Omega_0^2x/(1+x^2)^2$. The maximum of $x/(1+x^2)^2$ is $3\sqrt3/16$, at $x^2=1/3$. Here $\Omega_0=\|c\|^2/\|a\times c\|$. ∎
The primer $(a,c)$ is available online from the terminal-constraint duals ($p_j=-h(\nu_v+(t_f-t_j-\frac h2)\nu_r)$, §7), or by a homogeneous least-squares fit $\hat T_{3,j}\times(a+ct_j)=0$. The test costs $O(1)$. **Example:** vertical descent from upright rest ($T_3\parallel e_z$, $b_0=e_z$): $b\equiv e_z$ tracks, so $\Theta^{M1}_{\rm exact}\ne\emptyset$.

**Theorem C-Y (thinness under TVC coupling, M3b).** Let $T(\cdot)$ be any measurable thrust history with $\|T\|\ge\rho_1$ and $T(t)\in\Pi$ for a fixed plane $\Pi$ through $0$ (e.g. a 3DOF primer arc, which is a great circle). Let $b_0\in\Pi\cap S^2$, and let $\dot b_0$ be an in-plane initial body rate. Put $\mu_c^2=\rho_1\cos\delta/k=\ell\rho_1\cos\delta/J_\perp$. Then the set of $\dot b_0\in T_{b_0}\Pi$ (identified with $\mathbb R$) for which $T$ is exactly M3b-realizable on $[0,t_f]$ (gimbal $\angle(T,b)\le\delta$ throughout) has diameter at most
$$\frac{2\,\delta\,\mu_c}{\sinh(\mu_c t_f)} .$$
*Proof.* By 8.1, a realizing $b$ solves (uniquely, given $(b_0,\dot b_0)$; the right-hand side is Carathéodory and locally Lipschitz) $\ddot b=-\Pi_bT/k-\|\dot b\|^2b$. For data in $\Pi$ the solution stays in $\Pi$ (uniqueness, with an in-plane right-hand side). With $b=(\cos\varphi,\sin\varphi)$ and $T=\|T\|(\cos\psi,\sin\psi)$ in $\Pi$-coordinates, the equation reads $\ddot\varphi=\frac{\|T\|}{k}\sin(\varphi-\psi)$. Let $\varphi_1,\varphi_2$ be two realizations with the same $\varphi(0)$ and initial rates differing by $\eta>0$, and put $e=\varphi_2-\varphi_1$. By the mean value theorem $\ddot e=q\,e$ with $q=\frac{\|T\|}{k}\cos\xi$, where $\xi$ lies between $\varphi_1-\psi$ and $\varphi_2-\psi$, both in $[-\delta,\delta]$. So $q\ge\mu_c^2$. Let $w=\frac{\eta}{\mu_c}\sinh(\mu_ct)$. While $e\ge0$, $(\dot ew-e\dot w)'=(q-\mu_c^2)ew\ge0$, and it vanishes at $0$. Hence $(e/w)'\ge0$ and $e/w\ge1$ (limit at $0^+$). So $e$ never returns to $0$ and $e(t_f)\ge w(t_f)$. Both realizations satisfy $|\varphi_i-\psi|\le\delta$ at $t_f$, so $e(t_f)\le2\delta$, giving $\eta\le2\delta\mu_c/\sinh(\mu_ct_f)$. ∎

**Corollary C-Y'.** Suppose the 3DOF optimum is unique, both optima are attained, and the 3DOF thrust lies in a plane. If the in-plane initial body rate lies outside an interval of length $2\delta\mu_c/\sinh(\mu_ct_f)$, then $V_{M3b}(\theta)>V_3(\theta)$ strictly (by C-3D with "trackable" replaced by "M3b-realizable"). **GTPL numbers** (`context/vehicle.md`: $J_\perp=63.6$, $\ell=0.589$, $\rho_1=400$ N, $\delta=15^\circ$, $t_f=7$ s): $\mu_c=1.89\,\mathrm{s^{-1}}$, $\sinh(13.2)\approx2.8\times10^5$, interval length $\le3.5\times10^{-6}$ rad/s. Dry-vehicle or MPC-model inertias give even smaller values. *For the real TVC vehicle, exact 3DOF⇒6DOF optimality is a measure-near-zero event. Per-instance exactness (C-U/C-6) is the operative possibility statement.* (This is not a statement about the size of $V_{M3b}-V_3$, which may well be small. Quantifying it is open, §11.)

---

## 11. Open questions / conjectures
- **Q1 ($\rho_1=0$).** With $\rho_1=0$, $\alpha=0$ and $\delta+\omega t_f\le\pi/2$, is $F^{M1}$ convex? The $M$-witness is reachable (vertical $b$, reduced throttle), and `numerics` finds gap $\propto\rho_1$. `math/02` §8 shows nonconvexity once $\delta+\omega t_f>\pi/2$. A positive answer would be a genuine *uniform* possibility regime.
- **Q2.** Is $F(b)$ convex for fixed $b$ with **exact** mass depletion? (C-F needs constant or convexified mass.)
- **Q3.** Quantitative $V_{M3b}-V_3$ and $V_{M1}-V_3$ bounds in terms of $\omega_{\rm req}-\omega$ and $\varepsilon_0-\delta$.
- **Q4.** Is $\Theta^{M1}_{\rm exact}$ open with nonempty interior? (True if the 3DOF primer depends continuously on $\theta$; not proved.)
- **Deferred (per orchestrator).** Algorithms built on C-U: alternating "SOCP at $b$ ↔ attitude update", and CCP on the bilinear $\langle w,u\rangle\ge\sigma\cos\delta$ with feasible, monotone iterates. These are recorded in the BOARD post and not developed here.
