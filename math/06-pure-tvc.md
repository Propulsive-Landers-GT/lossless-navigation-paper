# Pure-TVC 6DOF landing (the GTPL actuation): nonconvexity of the upright-at-rest feasible set

Author: [proof-tvc]. Status: CLAIMED (CLAIMS rows TVC-*). Adversary: [adversary-6dof].
Numerics: `numerics/proof-tvc/` (own venv; single-threaded). Companion Lean list: `math/03-lean-blueprint.md` §"Pure TVC".

---

## 0. Verdict

| # | Statement | Status |
|---|---|---|
| TVC-1 | Pure TVC (gimbal is the only pitch/yaw torque), constant mass, upright at rest at both ends, $r_z\ge0$ and glide slope. For the **GTPL wet constants** at the certified horizons (table §3), $F^{\mathcal X}_{t_f}$ is **nonconvex**. So no uniform state-linear lossless convexification exists for that problem class at those horizons. Holds for competitors with roll held ($\omega_3\equiv0$) and also for competitors that use the roll RCS (variant R1). | **PROVED, computer-assisted** (§4). One finite-dimensional SDP certificate, re-verified by an eigenvalue computation, plus explicit remainder lemmas. No planarity or rigidity is used. |
| TVC-1q | Quantitative: $\operatorname{dist}(\theta_m,F_{t_f})\ge d_*$ (table §3). | proved with TVC-1 |
| TVC-B | Box gimbal $\pm15^\circ$: same with $\delta$ replaced by the corner angle $\delta^*=21.17^\circ$, $u$ on a box diagonal. | see table §3 |
| TVC-R | Gimbal-rate limit (100°/s, gimbal centred at $t=0$): only the witness must change, because the competitor class shrinks. | **numerics only** (§5.3) |
| TVC-F | Free final time on a window, via RR-LS. | conditional (§5.4) |
| — | Mass depletion ($\alpha>0$, varying $\varepsilon(m)$), realistic horizons 5–8 s, wind. | **OPEN** (§6) |

**Size.** The gap is genuinely thin: the gain of the best witness is about $10^{-4}$ m in $\ell=r_{0z}+s^*v_{0z}$ at $t_f=1$ s. The adversary's bottom-face numerics (0.08 m/s at 1 s, terminal attitude free or upright, altitude unconstrained) are consistent with this. With $r_z\ge0$ the only face we can certify is the dive-then-brake face, which is thin for the same reason as B\* (math/02 Rem. 10.2): a competitor can cancel lateral moments with small brake-phase tilts at quadratic cost.

**Why this works where the earlier routes failed.** Every previous route compared a 3D attitude path with a planar one: the M1 rigidity, the FLAT comparison $\omega_p=\|\omega_q\|$, and the B\*/D\* decoupling. Under $b(t_f)=e_z$, $\omega(t_f)=0$ these comparisons break ([adversary-6dof] BOARD 01:30, 01:45, thread item (1)). TVC-1 needs no comparison and no characterization of maximizers. It bounds **every zero-lateral competitor** directly. The bound has three ingredients:
1. Pointwise inequalities turn the exact functional into a quadratic form in the horizontal tilt $h=b_h$.
2. The torque constraint enters through an S-procedure multiplier $\lambda(s)$, and the two lateral-moment conditions through a Finsler multiplier $\rho$.
3. Because the quadratic form is a sum over the two components of $h$, the vector bound equals the scalar bound. Nonplanar loops, coning and two-lobe paths are therefore covered automatically.

The witness is explicit and planar, and only it needs to be computed accurately.

---

## 1. Model (PT) and standing assumptions

Rigid body with $J=\operatorname{diag}(J_t,J_t,J_a)$ (axisymmetric). Body axis $b=\mathsf Re_3\in S^2$; engine pivot at $-Lb$ from the CG.
- (PT1) Constant mass $m$ and constant $J_t,L$, so $\varepsilon:=J_t/(mL)$ is constant. ($\alpha=0$; see §6 for $\alpha>0$.)
- (PT2) Thrust $T\in[\rho_1,\rho_2]$ with $0<\rho_1<mg_0<\rho_2$. Set $a_1=\rho_1/m$, $a_2=\rho_2/m$, $A_b=a_2-g_0>0$. Gimbal: $\angle(d,b)\le\delta\in(0,\pi/2)$ (cone). The box is in §5.1.
- (PT3) Pitch/yaw torque comes only from the gimbal: $\tau_\perp=-LT\,b\times d$. Roll: either (R0) $\omega_3\equiv0$, or (R1) roll torque $|\tau_3|\le\tau_r$ (RCS) with $\omega_3$ free.
- (PT4) Boundary data $\theta=(r_0,v_0)$. Fixed: $b(0)=e_z$, $\omega(0)=0$. Landing: $r(t_f)=0$, $v(t_f)=0$, $b(t_f)=e_z$, $\omega_\perp(t_f)=0$; the final roll rate is free.
- (PT5) State constraints $\mathcal X$: $r_z\ge0$ and $r_z\ge\tan\gamma_{gs}\|r_h\|$.
- (PT6) Controls are relaxed. With $u:=Td/m$ (thrust acceleration), the right-hand sides are affine in $u$, so relaxation means $u(s)\in\mathcal C(b(s))$ with
$$\mathcal C(b)=\operatorname{conv}\{a d: a\in[a_1,a_2],\ \angle(d,b)\le\delta\}=\{u:\ \angle(u,b)\le\delta,\ \|u\|\le a_2,\ \langle u,b\rangle\ge a_1\cos\delta\}.$$
The gimbal rate is unlimited. Ordinary controls are dense, and the witness of §4.8 is an ordinary control.

Notation: $p=\langle u,b\rangle\ (\ge a_1\cos\delta)$, $q=\Pi_bu$ ($\perp b$), $\|q\|\le p\tan\delta$, $p^2+\|q\|^2\le a_2^2$, hence $\|q\|\le a_2\sin\delta$. Also $v:=\|\dot b\|$, $h:=b_h$, $K_1=a_1\sin\delta/\varepsilon$, $K_2=a_2\sin\delta/\varepsilon$. $F_{t_f}$ is the unconstrained feasible set and $F^{\mathcal X}_{t_f}\subseteq F_{t_f}$ the constrained one.

GTPL wet (`context/vehicle.md`): $m=79.88$, $\rho_1=400$, $\rho_2=1000$ N, $J_t=63.6$, $J_a=3.74$ kg m², $L=0.589$ m, $\delta=15^\circ$ ($\delta^*=21.17^\circ$ box), $\tau_r=3$ N m. So $\varepsilon=1.352$ m, $a_1=5.008$, $a_2=12.52$ m/s², $K_1=0.959$, $K_2=2.397$ rad/s².

## 2. Exact identities

**Lemma 2.1 (torque, centre of percussion).** Under (PT), $\varepsilon\nabla_t\dot b=-q+\varepsilon\frac{J_a}{J_t}\omega_3\,b\times\dot b$, with $\ddot b=\nabla_t\dot b-v^2b$. Hence $y:=r+\varepsilon b$ satisfies
$$\ddot y=f\,b+\gamma_3-g_0e_z,\qquad f:=p-\varepsilon v^2,\qquad \gamma_3:=\varepsilon\tfrac{J_a}{J_t}\omega_3\,b\times\dot b .$$
*Proof.* This is math/02 Lemma 6.4, written with $u$ in place of $Td/m$. Euler's equation gives $J_t\nabla\dot b=-LT\Pi_bd+J_a\omega_3 b\times\dot b$, and $LT/J_t=1/(m\varepsilon)$. Then $\ddot y=u-g_0e_z+\varepsilon\ddot b=pb+q-q+\gamma_3-\varepsilon v^2b-g_0e_z$. ∎ (Numerically: residual $9\cdot10^{-9}$, `numerics/adversary-6dof/flat_check.py`.)

**Lemma 2.2 (speed and tilt).** $\frac{d}{dt}v\le\|q\|/\varepsilon\le K_2$ a.e. where $v>0$. The gyroscopic term is $\perp\dot b$ and does no work. With $\dot b=0$ at both ends this gives $v(s)\le\bar v(s):=K_2\min(s,t_f-s)$ and $\varphi(s):=\angle(b,e_z)\le\bar\varphi(s):=K_2\min(s,t_f-s)^2/2$. Under (R1), $|\omega_3(s)|\le\bar\omega_3(s):=\tau_rs/J_a$.

**Lemma 2.3 (landing identity).** If a control lands from $\theta$, then
$$v_0=g_0t_fe_z-\int(fb+\gamma_3),\qquad r_0=\int s(fb+\gamma_3)-\tfrac12g_0t_f^2e_z,$$
$$\Lambda(\theta):=r_0+s^*v_0=\int_0^{t_f}w\,(fb+\gamma_3)\,ds+\kappa e_z,\qquad w(s)=s-s^*,\ \kappa=g_0t_f(s^*-t_f/2).$$
*Proof.* Use $y(0)=r_0+\varepsilon e_z$, $\dot y(0)=v_0$ ($\dot b(0)=0$), and $y(t_f)=\varepsilon e_z$, $\dot y(t_f)=0$ (upright at rest). Integrate $\ddot y$ twice, exactly as in math/02 Lemma 10.1. ∎

So $\ell(\theta):=\Lambda_z(\theta)=W_z+\kappa$ with $W_z:=\int w(fb_z+\gamma_{3z})$, and the lateral data are
$$v_{0h}=-\textstyle\int (fh+\gamma_{3h}),\qquad r_{0h}=\int s(fh+\gamma_{3h}).$$

**Lemma 2.4 (rotation midpoint).** $F_{t_f}$ and $F^{\mathcal X}_{t_f}$ are invariant under the rotation $R_\pi$ about $e_z$. If $\theta^*,R_\pi\theta^*\in F^{\mathcal X}$ and $\theta_m=\frac12(\theta^*+R_\pi\theta^*)\notin F$, then $F^{\mathcal X}$ is not convex. $\theta_m$ has $r_{0h}=v_{0h}=0$ and $\ell(\theta_m)=\ell(\theta^*)$.

## 3. Main theorem

Baseline (vertical body, chattering gimbal early, full throttle late):
$J_0:=-a_1\cos\delta\,\frac{s^{*2}}2+a_2\frac{(t_f-s^*)^2}2$. A control's **gain** is $W_z-J_0$.

**Theorem TVC-1.** Assume (PT1)–(PT6) and (A1) $\bar\varphi(t_f/2)<\pi/2$, (A2) $a_1\cos\delta>\varepsilon\bar v(t_f/2)^2$. Suppose there is an explicit planar control $c_w$ (§4.8), landing upright at rest and satisfying $\mathcal X$, whose gain is $G_w$. Suppose also that a certificate $(\lambda,\rho,\rho_c)$ (Def. 4.5) gives a bound $U_{\rm tot}$ with
$$G_w>U_{\rm tot}.$$
Then $\theta_w,R_\pi\theta_w\in F^{\mathcal X}_{t_f}$ and $\theta_m\notin F_{t_f}$. So $F^{\mathcal X}_{t_f}$ is not convex, and by Theorem A (math/02 §2) no uniform convex relaxation of the pure-TVC landing problem with affine data entry is lossless at this horizon. Quantitatively, $\operatorname{dist}(\theta_m,F_{t_f})\ge d_*$, where $d_*$ solves $G_w-d\sqrt{1+s^{*2}}=U_{\rm tot}(d)$ (§4.9).

**Certified instances** (GTPL wet constants; `numerics/proof-tvc/certificate.py`, output files `cert_*.out`):

CERT_TABLE_PLACEHOLDER

## 4. Proof of Theorem TVC-1

Fix a relaxed control $c$ that lands from some $\theta$ with $r_{0h}=v_{0h}=0$. We show $W_z(c)-J_0\le U_{\rm tot}$. Then $\theta_m$ (which has $W_z=J_0+G_w$) is not in $F$. All a-priori quantities $\bar v,\bar\varphi,\bar\omega_3$ are from Lemma 2.2. "$\cos\bar\varphi$" means its value (or a cellwise lower bound) at the time considered.

### 4.0 Lemma (localization)
It suffices to bound competitors with gain $W_z-J_0\ge0$, since $G_w>0$. For these, §4.1–4.2 (with $\zeta=0$) give
$$\int_Lw\,\Pi+(1-c_{\rm abs})\cos\bar\varphi_E\int_E|w|\Delta p\le E_0:=\int_E|w|\Big[A_1(1+k)\big(\tfrac{K_1s^2}2\big)^2+B_1(1+k)K_1^2s^2\Big]ds .$$
Here $c_{\rm abs}<1$ is explicit. It comes from early speed $v\le K_1s+\beta Y(s)$ ($\beta=\tan\delta/\varepsilon$, $Y=\int_0^s\Delta p$), from $Y^2\le s\,\Delta p_{\max}Y$, and from $\int_t^{s^*}(s^*-s)s\,ds\le\frac{s^{*2}}2(s^*-t)$, plus the analogous bound for the tilt. Consequences:
- $\int_Lw|h|^2\le2E_0/a_2$, $\int_Lwv^2\le E_0/(\varepsilon c_0)$, $\int_Lw|q|^2\le2a_2E_0/c_0^2$.
- On $[s_0,t_f]$ with $s_0>s^*$ the weight satisfies $w\ge s_0-s^*$. Agmon's inequality $\sup g^2\le\ell^{-1}\int g^2+2(\int g^2\int\dot g^2)^{1/2}$, with $|\dot v|\le|q|/\varepsilon$ and $|\tfrac d{ds}|h||\le v$, then gives pointwise late bounds.
- Near $s^*$: Lipschitz bounds starting from $v(s^*)$ and $|h(s^*)|$.
- Early: $v\le\min(K_2s,\,K_1s+\beta\bar Y(s))$ with $\bar Y(s)=\min_\eta[\Delta p_{\max}\eta+\mathrm{Pen}_E/(c_E(s^*-s+\eta))]$, and $\varphi\le\int_0^sv$.

The resulting $\bar v_{\rm loc}\le\bar v$ and $\bar\varphi_{\rm loc}\le\bar\varphi$ (`localize.py`) replace the crude bounds in everything below. For GTPL at $t_f=1$, $s^*=0.25$: $E_0=4.5\cdot10^{-4}$ m, $\max\bar v_{\rm loc}=0.34$ rad/s (crude bound 1.20), $\max\bar\varphi_{\rm loc}=0.060$ rad (crude bound 0.30). The crude bounds are still used for (A1)/(A2), i.e. for $b_z>0$ and $f>0$. In the quantitative statement (§4.9), competitors within $d$ of $\theta_m$ have gain $\ge G_w-d\sqrt{1+s^{*2}}\ge0$, so the lemma applies to them as well.

### 4.1 Gain decomposition (exact)
With $E=[0,s^*]$ and $L=(s^*,t_f]$,
$$W_z-J_0=\int_E|w|\,(a_1\cos\delta-fb_z)\;-\;\int_L w\,\Pi\;+\;\int w\,\gamma_{3z},\qquad \Pi:=a_2-fb_z .$$

### 4.2 Pointwise majorants
Let $\Delta p=p-a_1\cos\delta\ge0$. By (A1) $b_z\ge\cos\bar\varphi>0$, and by (A2) $f\ge a_1\cos\delta-\varepsilon\bar v^2>0$.
- *Early:* $a_1\cos\delta-fb_z=a_1\cos\delta(1-b_z)+\varepsilon v^2b_z-\Delta p\,b_z\le \frac{a_1\cos\delta}{1+\cos\bar\varphi}|h|^2+\frac{\varepsilon}{\cos^2\bar\varphi}|\dot h|^2-\cos\bar\varphi\,\Delta p$. This uses $1-b_z=|h|^2/(1+b_z)$ and $v^2=|\dot h|^2+\dot b_z^2\le|\dot h|^2/b_z^2$.
- *Late:* $\Pi=(a_2-pb_z)+\varepsilon v^2b_z$. Let $P:=\sqrt{a_2^2-|q|^2}\ge p$. Then
$a_2-pb_z\ge a_2-\sqrt{(a_2^2-|q|^2)(1-|h|^2)}\ge\frac{|q|^2b_z^2+a_2^2|h|^2}{2a_2}$, using $a_2-\sqrt Y\ge(a_2^2-Y)/(2a_2)$. Hence
$\Pi\ge\frac{\cos^2\bar\varphi}{2a_2}|q|^2+\frac{a_2}2|h|^2+\varepsilon\cos\bar\varphi|\dot h|^2$. Also, since $f\ge0$, $\Pi=(a_2-f)+f(1-b_z)\ge|a_2-f|$.
  ([adversary-6dof] checked (a): TRUE; it needs $a\le a_2$, i.e. constant mass, and Jensen for relaxed controls.)
- *Gyroscopic (R1 only):* $\gamma_{3z}=\varepsilon\frac{J_a}{J_t}\omega_3(h\times\dot h)_z$, so $|w\gamma_{3z}|\le|w|\,\varepsilon\frac{J_a}{J_t}\bar\omega_3\,\tfrac12(g|h|^2+|\dot h|^2/g)$ for any $g>0$.

Split $\Pi=(1-\zeta)\Pi+\zeta\Pi$ with $\zeta\in(0,1)$. Then
$$W_z-J_0\le \mathcal Q(h)-\cos\bar\varphi\!\int_E|w|\Delta p-\zeta\!\int_Lw|a_2-f| ,$$
$$\mathcal Q(h)=\int_E|w|\big[A_1|h|^2+B_1|\dot h|^2\big]-\int_Lw\big[(1-\zeta)(A_2|h|^2+B_2|\dot h|^2+C_2|q|^2)-\text{gyro}\big],$$
with $A_1=\frac{a_1\cos\delta}{1+\cos\bar\varphi}$, $B_1=\frac{\varepsilon}{\cos^2\bar\varphi}$ (plus the gyro terms), $A_2=a_2/2$, $B_2=\varepsilon\cos\bar\varphi$, $C_2=\cos^2\bar\varphi/(2a_2)$.

### 4.3 Torque in tilt coordinates (homogeneous remainders)
Projecting Lemma 2.1 horizontally gives $\ddot h=-q_h/\varepsilon+\frac{J_a}{J_t}\omega_3(b\times\dot b)_h-v^2h$, so
$$\big|\,|\ddot h|-|q_h|/\varepsilon\,\big|\le \bar v^2|h|+c_3|\dot h|,\qquad c_3:=\tfrac{J_a}{J_t}\bar\omega_3/\cos\bar\varphi .$$
- *Early* ($|q|\le p\tan\delta$): $|\ddot h|^2\le(1+\kappa)\big(K_1^2+\kappa_D\Delta p\big)+2(1+\tfrac1\kappa)(\bar v^4|h|^2+c_3^2|\dot h|^2)$, with $\kappa_D=2K_1\tan\delta/\varepsilon+(a_2-a_1\cos\delta)\tan^2\delta/\varepsilon^2$. On the last $\eta_1$ cells before $s^*$ we use instead $|q|\le a_2\sin\delta$, i.e. $K_2$ with no $\Delta p$ term.
- *Late:* the same with $K_2$, and $|q|^2\ge\varepsilon^2\big[(1-\vartheta)|\ddot h|^2-(\tfrac1\vartheta-1)\,2(\bar v^4|h|^2+c_3^2|\dot h|^2)\big]$.

The splitting parameter $\vartheta=\vartheta(s)\in[10^{-3},0.9]$ is chosen per quadrature sub-cell, so that the homogeneous remainder removes at most a fraction $r_\vartheta=0.2$ of $A_2$. The remainders are **quadratic in $(h,\dot h)$ with small coefficients**, not additive constants. This is the fix for [adversary-6dof]'s attack A1: an additive remainder $R\sim\varepsilon^2\bar e^2$ swamped $G_w$. The remainders shift $A_2,B_2$ by $O(\varepsilon^2\bar v^4/a_2)$ and add $\lambda$-weighted terms to the gain side.

### 4.4 Moments
Let $f_0=a_1\cos\delta$ on $E$ and $a_2$ on $L$, and $m_j:=\int s^jf_0h$ for $j=0,1$. Zero lateral data give
$m_j=-\int s^j\big[(f-f_0)h+\gamma_{3h}\big]$, so
$$|m_j|\le M^v_j+\int s^j\sin\bar\varphi\,D,\qquad D=\Delta p\ (E),\ |a_2-f|\ (L),$$
$$M^v_j=\int_Es^j\sin\bar\varphi\,\varepsilon\bar v^2+\int s^j\varepsilon\tfrac{J_a}{J_t}\bar\omega_3\bar v .$$

### 4.5 Certificate (S-procedure + Finsler)
**Definition 4.5.** A certificate is a triple $(\lambda,\rho,\rho_c)$. Here $\lambda\ge0$ is piecewise constant on a uniform grid of $N$ cells, and $\rho,\rho_c\ge0$. For every $n\in L^2(0,t_f)$, set $x=I^2n$ ($x(0)=\dot x(0)=0$) and require
$$\mathcal Q_{\rm sc}(x)+\int\lambda\,\ell_\lambda(x)\le\int\lambda n^2+(1-\zeta)\!\int_LwC_2\varepsilon^2(1-\vartheta)n^2+\rho\sum_j m_j(x)^2+\rho_c\big(\dot x(t_f)^2+x(t_f)^2\big),\tag{C}$$
where $\mathcal Q_{\rm sc}$ is the scalar form of §4.2/4.3 without the $C_2$ term, and $\ell_\lambda(x)=2(1+1/\kappa)(\bar v^4x^2+c_3^2\dot x^2)$. In addition:
(i) $\lambda(1+\kappa)\kappa_D\le(1-\xi)|w|\cos\bar\varphi$ on the early cells away from $s^*$ (absorption of $\Delta p$);
(ii) $\lambda\le\lambda_{\max}$.
Its value is $V_\lambda=(1+\kappa)\int\lambda\bar N^2$, with $\bar N=K_1$ on early cells away from $s^*$ and $K_2$ elsewhere.

*Use.* Apply (C) to each component $x=h_i$ ($i=1,2$; $h$ is clamped, so the $\rho_c$ term vanishes) and add. $|\ddot h|^2=\sum_i\ddot h_i^2$ and $|m_j|^2=\sum_i m_{j,i}^2$. **Separability makes the vector bound equal the scalar bound; no planarity is needed.** Insert the pointwise bound of §4.3 for $|\ddot h|^2$ and use (i). The result is
$$W_z-J_0\le V_\lambda+\rho\sum_j|m_j|^2-\mathrm{Pen},\qquad \mathrm{Pen}=\xi\!\int_E|w|\cos\bar\varphi\,\Delta p+\zeta\!\int_Lw|a_2-f| .$$

### 4.6 Lemma (continuous validity from a finite SDP)
*Version used for the certified numbers (`certificate2.py`, Lemma 4.6′).* The discrete space is cellwise **linear** functions, with $2N$ degrees of freedom. The remainder $n''$ is orthogonal to $\{1,t\}$ on every cell. Hence $\dot x''$ vanishes at both cell ends and has zero cell mean, so $\dot x''$ and $x''$ are cell-local. Wirtinger gives $\|\dot x''\|^2_{\rm cell}\le(h_c/2\pi)^2\|n''\|^2_{\rm cell}$ and $\|x''\|^2_{\infty,\rm cell}\le h_c^3/(4\pi^2)\|n''\|^2_{\rm cell}$, and $|\int gn''|\le\sup|g''|\,\frac{h_c^2}8\sqrt{t_f}\|n''\|$; the clamp functionals are linear, so their remainder vanishes. The splitting parameters are $\tau=\tau'=0.01$. Everything else below is as stated.

*Original version (`certificate.py`, cell averages).* Split $n=\bar n+n'$, where $\bar n$ is the cell average, and split the form in (C) into its PSD part $\mathcal K_+$ (early gains, $\lambda$-terms) and its NSD part $\mathcal K_-$ (late costs, $-\rho\,m^2$, $-\rho_c$ clamps). Then
$$\langle\mathcal K n,n\rangle\le(1+\tau)\langle\mathcal K_+\bar n,\bar n\rangle+(1-\tau')\langle\mathcal K_-\bar n,\bar n\rangle+(1+\tfrac1\tau)\langle\mathcal K_+n',n'\rangle+(\tfrac1{\tau'}-1)\langle-\mathcal K_-n',n'\rangle .$$
For cell-constant $\bar n$, the first two terms are an exact $N\times N$ matrix form (5-point Gauss–Legendre is exact, since the integrands are polynomials of degree $\le9$ on sub-cells with frozen conservative coefficients). The SDP enforces it to be $\le\int(\lambda+M_{\rm late})\bar n^2$. For zero-mean $n'$:
- $|\dot x'(s)|^2\le h_c\|n'\|_k^2$ in cell $k$;
- $|x'(s)|\le h_c\sqrt{t_f/12}\,\|n'\|+h_c^{3/2}\|n'\|_k/\sqrt3$;
- $|\int gn'|\le\sup|g'|\,h_c\sqrt{t_f/12}\,\|n'\|$.

So the $n'$ terms are $\le\sum_kc_{{\rm loc},k}\|n'\|_k^2+c_g\|n'\|^2$, of order $h_c^2$. Requiring $\lambda_k+M_{{\rm late},k}\ge c_{{\rm loc},k}+c_g$ makes (C) hold for all $n\in L^2$. ([adversary-6dof] checked (c): no error.) The discrete inequality is re-verified by `numpy.linalg.eigvalsh`. If the top eigenvalue is positive at solver tolerance, $\lambda$ is shifted uniformly until it is $\le0$.

### 4.7 Lemma (moment shifts are paid for by Pen)
For any $\eta>0$, $\int s^j\sin\bar\varphi D\le D_{\max}\int_{|w|<\eta}s^j\sin\bar\varphi+\frac1\eta\sup_{|w|\ge\eta}\frac{s^j\sin\bar\varphi}{\omega_D}\,\mathrm{Pen}=:U_j(\mathrm{Pen})$ (minimized over $\eta$). Here $\omega_D=\xi\cos\bar\varphi$ on $E$ and $\zeta$ on $L$, and $D_{\max}=a_2-a_1\cos\delta+\varepsilon\max\bar v^2$. Hence
$$W_z-J_0\le U_{\rm tot}:=V_\lambda+\max_{\mathrm{Pen}\ge0}\Big[\rho\sum_j\big(M^v_j+U_j(\mathrm{Pen})\big)^2-\mathrm{Pen}\Big].$$
$U_j$ is nondecreasing, so the maximum is bounded on a grid by pairing the right-endpoint $U$ with the left-endpoint Pen.

### 4.8 The witness (planar dive-then-brake, ordinary control)
Planar meridian $b=\cos\psi\,e_z+\sin\psi\,u$, with $\ddot\psi=n$ piecewise constant (100 cells), $\psi,\dot\psi=0$ at both ends.
- On $E$: $T=\rho_1$, gimbal in the plane at angle $\delta$, so $p=a_1\cos\delta$, $|q|=a_1\sin\delta$, $|n|\le K_1$. The optimized profile is bang-bang $|n|=K_1$ on $E$, so no chattering is needed.
- On $L$: $T=\rho_2$, gimbal angle $\mu$ with $a_2\sin\mu=\varepsilon|n|$, so $p=\sqrt{a_2^2-\varepsilon^2n^2}$.

$W_z=\int w(p-\varepsilon\dot\psi^2)\cos\psi$ is evaluated exactly: $\psi$ is integrated in closed form on 40000 sub-steps, with a midpoint quadrature of the smooth integrand. For the state constraints, $v_z<0$ on $[0,t_f)$ gives $r_z>0$, and $\min r_z/|r_h|$ gives the admissible glide-slope angle (both in the table). By Lemma 2.4 the rotated witness lands from $R_\pi\theta_w$.

### 4.9 Conclusion and quantitative bound
If $\theta\in F$ with $\|\theta-\theta_m\|\le d$, then $|v_{0h}|,|r_{0h}|\le d$, which replaces $M^v_j$ by $M^v_j+d$, and $\ell(\theta)\ge\ell(\theta_m)-d\sqrt{1+s^{*2}}$. So $G_w-d\sqrt{1+s^{*2}}\le U_{\rm tot}(d)$. Bisection gives $d_*$. ∎

## 5. Variants and scope

### 5.1 Box gimbal
The box satisfies $\mathcal C_{\rm box}(b)\subseteq\mathcal C_{\delta^*}(b)$ with $\delta^*=\arccos(\cos^215^\circ)$. The witness runs along a diagonal: at the corner it gives $p=a_1\cos\delta^*$, $|q|=a_1\sin\delta^*$, and late gimbal angles $\le\delta^*$ along the diagonal are available. With $\omega_3\equiv0$ the box does not rotate, and $R_\pi$ maps the box to itself. So TVC-1 applies with $\delta=\delta^*$ (table row "box").
### 5.2 Glide slope
The witness has $\min_{t<t_f} r_z/\|r_h\|$ as in the table, so every $\gamma_{gs}$ with $\tan\gamma_{gs}$ below it is covered. The competitor bound uses no state constraint.
### 5.3 Gimbal-rate limit
The competitor class shrinks, so $U_{\rm tot}$ stays valid. The witness must be rate-feasible from a centred gimbal. `witness_ratelim.py` optimizes it (state $\mu$, $|\dot\mu|\le100^\circ$/s, free throttle): RATELIM_PLACEHOLDER
### 5.4 Free final time
By RR-LS (math/redteam-reform §4) it suffices that $\theta_m(t^\circ)\notin\bigcup_{t\in W}F_t$. Since $\Lambda$ does not depend on the horizon, a competitor at horizon $t$ satisfies $\ell(\theta)\le J_0(t)+\kappa(t)+U_{\rm tot}(t)$. Here $J_0(t)+\kappa(t)$ is increasing in $t$ (derivative $A_b(t-s^*)>0$). Taking $t^\circ=t_b$ gives a sufficient condition:
$$G_w(t_b)>\max_{t\in[t_a,t_b]}\Big[U_{\rm tot}(t)-\tfrac{A_b}2\big((t_b-s^*)^2-(t-s^*)^2\big)\Big].$$
This needs certificates on a continuum of $t$. We have checked it only on a grid, so TVC-F remains conditional.
### 5.5 Variable $\varepsilon$, mass depletion
Not covered. With $\alpha>0$, $\varepsilon(m(t))$ gives $\ddot y$ the extra terms $2\dot\varepsilon\dot b+\ddot\varepsilon b$, and $\ddot\varepsilon$ contains $\dot T$, which is unbounded for relaxed throttle. The late baseline also moves by $\alpha\rho_2(\rho_2-\rho_1)s^*/m^2\cdot\int_Lw\approx4\cdot10^{-3}$ m, which is far larger than the gap. A certificate for the $\alpha>0$ class needs the competitor's own mass history inside Pen ([adversary-6dof] A2). **Open.** TVC-1 is a theorem about the constant-mass class. That class is the standard LCvx idealization, but it is not literally GTPL.

## 6. What remains open
1. **Realistic horizons (5–8 s).** (A1)/(A2) fail for $t_f\gtrsim1.5$ s with the crude a-priori bounds of Lemma 2.2. A localization lemma would extend the method: a competitor with gain $\ge0$ has small late tilt and rate, by an energy bound plus Lipschitz bootstrap. The certificate would also need to scale, roughly $N\propto t_f$, and the SDP cost grows with $N$.
2. Mass depletion / varying $\varepsilon$ (§5.5).
3. A rate-limited witness that beats $U_{\rm tot}$, or a bound tailored to the rate-limited class (§5.3).
4. Non-axisymmetric $J$, aerodynamic torque, wind (wind breaks the $R_\pi$ symmetry).
5. A formal (interval-arithmetic or Lean) check of the SDP certificate. The rest of the proof is Lean-ready (math/03 §Pure TVC).
6. A *non*-thin face for the constrained problem (practical ε-impossibility). As for M1 (math/02 Rem. 10.2), none is known.
