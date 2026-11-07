# Pure-TVC 6DOF landing (the GTPL actuation): nonconvexity of the upright-at-rest feasible set

Author: [proof-tvc]. Status: CLAIMED (CLAIMS rows TVC-*). Adversary: [adversary-6dof].
Numerics: `numerics/proof-tvc/` (own venv; single-threaded). Companion Lean list: `math/03-lean-blueprint.md` §"Pure TVC".

---

## 0. Verdict

| # | Statement | Status |
|---|---|---|
| TVC-1 | Pure TVC (gimbal is the only pitch/yaw torque), roll held ($\omega_3\equiv0$, as in the brief), constant mass, upright at rest at both ends, $r_z\ge0$ and glide slope. For the **GTPL wet constants** at $t_f=1$ s ($s^*=0.25$ s), $F^{\mathcal X}_{t_f}$ is **nonconvex**, with both a cone gimbal (15°) and the Cardan box (±15°). So no uniform state-linear lossless convexification exists for that problem class at that horizon. | **PROVED, computer-assisted** (§4). One finite-dimensional SDP certificate (2N×2N) plus explicit remainder lemmas. **Certified in exact rational/interval arithmetic by [verify-tvc]**; [adversary-6dof] verdict SURVIVES. No planarity or rigidity is used. |
| TVC-1q | Quantitative: $\operatorname{dist}(\theta_m,F_{t_f})\ge d_*$ (table §3). | proved with TVC-1 |
| TVC-B | Box gimbal $\pm15^\circ$ (Cardan): same with $\delta$ replaced by the corner angle $\delta^*=21.09^\circ$, and $u$ along the corner azimuth. | **PROVED** (certificate, table §3) |
| TVC-1R | Competitors that also use the roll RCS ($|\tau_3|\le3$ N m, $\omega_3$ free). All gyroscopic terms are in the certificate, including the lateral force, which goes in by weighted Cauchy–Schwarz: $(\int c|\dot h|)^2\le\int c\int c|\dot h|^2$. The localization lemma absorbs the gyro term into $\vartheta_g\Pi$. | **PROVED, computer-assisted** at $N=120$: margin 4.0%, re-verified ($N=60$ fails) |
| TVC-R | Gimbal-rate limit (100°/s per axis, gimbal centred at $t=0$). | **Nonconvex numerically, unproved.** In the full 6DOF model ([adversary-6dof]'s `m3tvc.py`: Cardan box rate-limited, mass depletion, roll free, $r_z\ge0$, upright at rest), the dive-then-brake face has zero-lateral max < free max at every horizon tried; see §5.3 table. The certificate does not transfer: the rate-limited baseline is unattainable, so a jerk multiplier is needed (§5.3). |
| TVC-F | Free final time on a window, via RR-LS. | conditional (§5.4) |
| TVC-2 | $t_f=2$ s, no tilt cap (§5.7), state-space Riccati certificate with Arb-verified recursion; margin 8.06%, $d_*\ge9.23\cdot10^{-5}$ m (cone, roll held). | **PROVED, computer-assisted; CONFIRMED** ([verify-tvc] exact re-certification; [adversary-6dof] SURVIVES) |
| TVC-3 | $t_f=3$ s, **tilt-capped class** (cap $80^\circ$ or $30^\circ$), $r_z\ge0$; margin 4.16%, $d_*\ge4.79\cdot10^{-5}$ m (§5.8). | **PROVED, computer-assisted; CONFIRMED** ([verify-tvc] exact) |
| TVC-5 | $t_f=5$ s, tilt-capped class (cap $80^\circ$/$30^\circ$), $r_z\ge0$ + glide slope; margin 0.20%, $d_*\ge2.48\cdot10^{-6}$ m (§5.9). | **PROVED, computer-assisted; CONFIRMED** ([verify-tvc] exact) |
| TVC-L∞ | $t_f\ge6$ s; uncapped $t_f>2.3$ s (needs a tumbling lemma); mass depletion; rate limit. | **OPEN as proof**; numerically nonconvex. Tools are built ((A2) dropped; bootstrap localization), and the ideal ratio is 0.70 at $t_f=3$, but the rigorous runs fail (§5.6). Numerically nonconvex. |
| — | Mass depletion ($\alpha>0$, varying $\varepsilon(m)$), wind. | **OPEN** as proof (§5.5). The numerics above include mass depletion and still show nonconvexity. |

**Size.** The gap is genuinely thin. The certified distance from $\theta_m$ to $F$ is $\ge9.6\cdot10^{-6}$ m (cone) and $\ge7.3\cdot10^{-6}$ m (box). The gain of the best witness is about $10^{-4}$ m in $\ell=r_{0z}+s^*v_{0z}$ at $t_f=1$ s. The adversary's bottom-face numerics (0.08 m/s at 1 s, terminal attitude free or upright, altitude unconstrained) are consistent with this. With $r_z\ge0$ the only face we can certify is the dive-then-brake face, which is thin for the same reason as B\* (math/02 Rem. 10.2): a competitor can cancel lateral moments with small brake-phase tilts at quadratic cost.

**Why this works where the earlier routes failed.** Every previous route compared a 3D attitude path with a planar one: the M1 rigidity, the FLAT comparison $\omega_p=\|\omega_q\|$, and the B\*/D\* decoupling. Under $b(t_f)=e_z$, $\omega(t_f)=0$ these comparisons break ([adversary-6dof] BOARD 01:30, 01:45, thread item (1)). TVC-1 needs no comparison and no characterization of maximizers. It bounds **every zero-lateral competitor** directly. The bound has three ingredients:
1. Pointwise inequalities turn the exact functional into a quadratic form in the horizontal tilt $h=b_h$.
2. The torque constraint enters through an S-procedure multiplier $\lambda(s)$. The two lateral-moment conditions enter through Finsler multipliers: $\rho_0$ on the unweighted moment and $\rho_w$ on the weighted one, $\Lambda_h$.
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

GTPL wet (`context/vehicle.md`): $m=79.88$, $\rho_1=400$, $\rho_2=1000$ N, $J_t=63.6$, $J_a=3.74$ kg m², $L=0.589$ m, $\delta=15^\circ$ ($\delta^*=21.09^\circ$ box), $\tau_r=3$ N m. So $\varepsilon=1.352$ m, $a_1=5.008$, $a_2=12.52$ m/s², $K_1=0.959$, $K_2=2.397$ rad/s².

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

**Theorem TVC-1.** Assume (PT1)–(PT6) and (A1) $\bar\varphi(t_f/2)<\pi/2$, (A2) $a_1\cos\delta>\varepsilon\bar v(t_f/2)^2$ (A2 holds at the certified $t_f=1$ instances; it can be dropped altogether, §5.6). Suppose there is an explicit planar control $c_w$ (§4.8), landing upright at rest and satisfying $\mathcal X$, whose gain is $G_w$. Suppose also that a certificate $(\lambda,\rho,\rho_c)$ (Def. 4.5) gives a bound $U_{\rm tot}$ with
$$G_w>U_{\rm tot}.$$
Then $\theta_w,R_\pi\theta_w\in F^{\mathcal X}_{t_f}$ and $\theta_m\notin F_{t_f}$. So $F^{\mathcal X}_{t_f}$ is not convex, and by Theorem A (math/02 §2) no uniform convex relaxation of the pure-TVC landing problem with affine data entry is lossless at this horizon. Quantitatively, $\operatorname{dist}(\theta_m,F_{t_f})\ge d_*$, where $d_*$ solves $G_w-d\sqrt{1+s^{*2}}=U_{\rm tot}(d)$ (§4.9).

**Certified instances** (GTPL wet constants; `numerics/proof-tvc/certificate.py`, output files `cert_*.out`):

| gimbal | competitors | $N$ (solver) | $G_w$ (m) | $U_{\rm tot}$ (m) | margin | $d_*$ (m) | $(\rho_0,\rho_w)$ | file |
|---|---|---|---|---|---|---|---|---|
| cone 15° | R0 | 60 (Clarabel) | 7.269e-5 | 6.781e-5 | 6.7% | 4.7e-6 | (1.5, 15) | `cert2_R60.out` |
| cone 15° | R0 | 120 (SCS + eigen repair) | 7.2691e-5 | 6.2736e-5 | 13.7% | 9.6e-6 | (1.5, 100) | `cert2_R120.out` |
| box ±15° (δ*=21.09°) | R0 | 60 (Clarabel) | 1.4043e-4 | 1.3286e-4 | 5.4% | 7.3e-6 | (1, 15) | `cert2_R60_box.out` |
| cone 15° | R1 (roll free) | 60 | 7.269e-5 | 8.709e-5 | FAIL | — | (1, 15) | `cert2_R60_roll.out` |
| cone 15° | R1 (roll free) | 120 (SCS + repair) | 7.2691e-5 | 6.9798e-5 | 4.0% | 2.8e-6 | (1, 30), $\kappa_g=0.3$ | `cert2_R120_roll.out` |

Common parameters: $\zeta=\xi=0.1$, $\tau=0.03$, $\tau'=0.01$, $\tau_\rho=0.2$, $\kappa=0.01$, $r_\vartheta=0.2$, $\lambda_{\max}=3\cdot10^{-3}$ (fixed PSD bound for the $\lambda$-weighted remainder terms), $\rho_c=0.1$, $\eta_1=2$ cells. The $N=120$ cone (R0, R1) and $N=60$ box certificates were **re-checked in floating point** by `verify_cert.py` (fresh process, matrices rebuilt, no SDP solver; float only). **They are also CERTIFIED IN EXACT ARITHMETIC by the independent auditor [verify-tvc]** (math/verify-tvc-report.md, numerics/verify-tvc/exact_cert.py). That check re-assembles every matrix by exact polynomial integration, with Arb balls for the transcendental coefficients, and decides $-M\succ0$ by exact integer Sylvester minors. It reproduces margins 13.70% / 5.40% / 3.99% and $d_*$ = 9.63e-6 / 7.34e-6 / 2.81e-6 m, after the auditor's repairs W1 (ordinary witness, §4.8) and W2 (R1 gyro weight). The float re-check gave top eigenvalue $-3.0\cdot10^{-8}$ (cone, $N=120$), $-5.4\cdot10^{-8}$ (roll, $N=120$) and $-2.0\cdot10^{-11}$ (box), Cholesky of $-M$ succeeds, $U_{\rm tot}$ reproduced.

Witness ($t_f=1$, $s^*=0.25$, cone): $r_0=(0.0078,\,1.116)$ m, $v_0=(-0.022,\,-0.791)$ m/s, maximum tilt 0.45°. $v_z<0$ on $[0,t_f)$: $v_z$ decreases on $E$ and $v_z(0)<0$, while on $L$, $\dot v_z>0$ and $v_z(t_f)=0$. Hence $r_z>0$ on $[0,t_f)$. The glide slope holds for every $\tan\gamma_{gs}\le116$. Quadrature error of $G_w$: midpoint rule on 400 sub-steps per smooth piece, $\le t_f\,\Delta t^2/24\cdot\sup|\ddot g|\approx10^{-9}$, which is $\ll$ the margin.

*Remark (no closure argument needed; referee items on E₀).* The bound of §4 holds for every **relaxed** control, i.e. $u(s)\in\mathcal C(b(s))$, which is a superset of the ordinary controls. The witness is an **ordinary** control: bang-bang full deflection early, a smooth gimbal angle late, no chattering. So $\theta_w,R_\pi\theta_w\in F^{\mathcal X}$ and $\theta_m\notin F^{\rm rel}\supseteq F$, and no identity $\mathrm{cl}\,R=R^{\rm rel}$ is used. The referee's other items for E₀ ([verify-pos6]: constant mass, and the regime of §6) are satisfied here: the mass is constant (PT1), and the regime conditions are (A1)/(A2), checked in the code. Box corner angle for the Cardan gimbal: $\arccos(\cos^215^\circ)=21.09^\circ$.

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
Let $\Delta p=p-a_1\cos\delta\ge0$. By (A1) $b_z\ge\cos\bar\varphi>0$. ((A2) $f\ge0$ was used in v1 only for $\Pi\ge|a_2-f|$; v2 uses $\Pi\ge b_z|a_2-f|$ instead, see §5.6.)
- *Early:* $a_1\cos\delta-fb_z=a_1\cos\delta(1-b_z)+\varepsilon v^2b_z-\Delta p\,b_z\le \frac{a_1\cos\delta}{1+\cos\bar\varphi}|h|^2+\frac{\varepsilon}{\cos^2\bar\varphi}|\dot h|^2-\cos\bar\varphi\,\Delta p$. This uses $1-b_z=|h|^2/(1+b_z)$ and $v^2=|\dot h|^2+\dot b_z^2\le|\dot h|^2/b_z^2$.
- *Late:* $\Pi=(a_2-pb_z)+\varepsilon v^2b_z$. Let $P:=\sqrt{a_2^2-|q|^2}\ge p$. Then
$a_2-pb_z\ge a_2-\sqrt{(a_2^2-|q|^2)(1-|h|^2)}\ge\frac{|q|^2b_z^2+a_2^2|h|^2}{2a_2}$, using $a_2-\sqrt Y\ge(a_2^2-Y)/(2a_2)$. Hence
$\Pi\ge\frac{\cos^2\bar\varphi}{2a_2}|q|^2+\frac{a_2}2|h|^2+\varepsilon\cos\bar\varphi|\dot h|^2$. Also $\Pi\ge b_z|a_2-f|$ for either sign of $f$, and $\Pi\ge|a_2-f|$ when $f\ge0$ (§5.6).
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
Let $f_0=a_1\cos\delta$ on $E$ and $a_2$ on $L$. Use the two moment functionals
$$m_0(h):=\int f_0h,\qquad m_w(h):=\int (s-s^*)f_0h .$$
Zero lateral data ($v_{0h}=0$, and $\Lambda_h=r_{0h}+s^*v_{0h}=0$) give $m_0=-\int[(f-f_0)h+\gamma_{3h}]$ and $m_w=-\int w[(f-f_0)h+\gamma_{3h}]$. Hence, with $D=\Delta p$ on $E$ and $D=|a_2-f|$ on $L$:
$$|m_0|\le M^v_0+\int\sin\bar\varphi\,D,\qquad |m_w|\le M^v_w+\int|w|\sin\bar\varphi\,D\le M^v_w+c_w\,\mathrm{Pen},$$
where $c_w=\sup\sin\bar\varphi/\omega_D$, $M^v_0=\int_E\sin\bar\varphi\,\varepsilon\bar v^2+\int\varepsilon\frac{J_a}{J_t}\bar\omega_3\bar v$, and $M^v_w$ is the same with an extra weight $|w|$.

**Why two functionals.** The weighted moment is $\Lambda_h$. Its throttle shift is *linear* in the penalty, because the weight $|w|$ appears in both. So it tolerates a very large Finsler multiplier $\rho_w$. Throttle modulation near $s^*$ is almost free to first order. It can shift the *unweighted* moment at a cost that is only quadratic: $\mu_0^2\lesssim4H^2D_{\max}\mathrm{Pen}/\omega$ with $H=|h(s^*)|$. That shift is genuine competitor freedom, not a proof artefact, and it caps $\rho_0$. With the two-functional split and $(\rho_0,\rho_w)=(1.5,10^3)$, the idealized zero-lateral bound at $t_f=1$, $s^*=0.25$ is $5.25\cdot10^{-5}$. A single $\rho$ on $(m_0,m_1)$ gives only $\approx6.5\cdot10^{-5}$ at $\rho=1$.

### 4.5 Certificate (S-procedure + Finsler)
**Definition 4.5.** A certificate is $(\lambda,\rho_0,\rho_w,\rho_c)$. Here $\lambda\ge0$ is piecewise constant on a uniform grid of $N$ cells, and $\rho_0,\rho_w,\rho_c\ge0$. For every $n\in L^2(0,t_f)$, set $x=I^2n$ ($x(0)=\dot x(0)=0$) and require
$$\mathcal Q_{\rm sc}(x)+\int\lambda\,\ell_\lambda(x)\le\int\lambda n^2+(1-\zeta)\!\int_LwC_2\varepsilon^2(1-\vartheta)n^2+\rho_0m_0(x)^2+\rho_wm_w(x)^2+\rho_c\big(\dot x(t_f)^2+x(t_f)^2\big),\tag{C}$$
where $\mathcal Q_{\rm sc}$ is the scalar form of §4.2/4.3 without the $C_2$ term, and $\ell_\lambda(x)=2(1+1/\kappa)(\bar v^4x^2+c_3^2\dot x^2)$. In addition:
(i) $\lambda(1+\kappa)\kappa_D\le(1-\xi)|w|\cos\bar\varphi$ on the early cells away from $s^*$ (absorption of $\Delta p$);
(ii) $\lambda\le\lambda_{\max}$.
Its value is $V_\lambda=(1+\kappa)\int\lambda\bar N^2$, with $\bar N=K_1$ on early cells away from $s^*$ and $K_2$ elsewhere.

*Use.* Apply (C) to each component $x=h_i$ ($i=1,2$; $h$ is clamped, so the $\rho_c$ term vanishes) and add. $|\ddot h|^2=\sum_i\ddot h_i^2$, and $|m_0|^2$, $|m_w|^2$ are sums over components. **Separability makes the vector bound equal the scalar bound; no planarity is needed.** Insert the pointwise bound of §4.3 for $|\ddot h|^2$ and use (i). The result is
$$W_z-J_0\le V_\lambda+\rho_0|m_0|^2+\rho_w|m_w|^2-\mathrm{Pen},\qquad \mathrm{Pen}=\xi\!\int_E|w|\cos\bar\varphi\,\Delta p+\zeta\!\int_Lw|a_2-f| .$$

### 4.6 Lemma (continuous validity from a finite SDP)
*Version used for the certified numbers (`certificate2.py`, Lemma 4.6′).* The discrete space is cellwise **linear** functions, with $2N$ degrees of freedom. The remainder $n''$ is orthogonal to $\{1,t\}$ on every cell. Hence $\dot x''$ vanishes at both cell ends and has zero cell mean, so $\dot x''$ and $x''$ are cell-local. Wirtinger gives $\|\dot x''\|^2_{\rm cell}\le(h_c/2\pi)^2\|n''\|^2_{\rm cell}$ and $\|x''\|^2_{\infty,\rm cell}\le h_c^3/(4\pi^2)\|n''\|^2_{\rm cell}$, and $|\int gn''|\le\sup|g''|\,\frac{h_c^2}8\sqrt{t_f}\|n''\|$; the clamp functionals are linear, so their remainder vanishes. The splitting parameters are $\tau=0.03$, $\tau'=0.01$, $\tau_\rho=0.2$. Everything else below is as stated.

*Original version (`certificate.py`, cell averages).* Split $n=\bar n+n'$, where $\bar n$ is the cell average, and split the form in (C) into its PSD part $\mathcal K_+$ (early gains, $\lambda$-terms) and its NSD part $\mathcal K_-$ (late costs, $-\rho\,m^2$, $-\rho_c$ clamps). Then
$$\langle\mathcal K n,n\rangle\le(1+\tau)\langle\mathcal K_+\bar n,\bar n\rangle+(1-\tau')\langle\mathcal K_-\bar n,\bar n\rangle+(1+\tfrac1\tau)\langle\mathcal K_+n',n'\rangle+(\tfrac1{\tau'}-1)\langle-\mathcal K_-n',n'\rangle .$$
For cell-constant $\bar n$, the first two terms are an exact $N\times N$ matrix form (5-point Gauss–Legendre is exact, since the integrands are polynomials of degree $\le9$ on sub-cells with frozen conservative coefficients). The SDP enforces it to be $\le\int(\lambda+M_{\rm late})\bar n^2$. For zero-mean $n'$:
- $|\dot x'(s)|^2\le h_c\|n'\|_k^2$ in cell $k$;
- $|x'(s)|\le h_c\sqrt{t_f/12}\,\|n'\|+h_c^{3/2}\|n'\|_k/\sqrt3$;
- $|\int gn'|\le\sup|g'|\,h_c\sqrt{t_f/12}\,\|n'\|$.

So the $n'$ terms are $\le\sum_kc_{{\rm loc},k}\|n'\|_k^2+c_g\|n'\|^2$, of order $h_c^2$. Requiring $\lambda_k+M_{{\rm late},k}\ge c_{{\rm loc},k}+c_g$ makes (C) hold for all $n\in L^2$. ([adversary-6dof] checked (c): no error.) The discrete inequality is re-verified by `numpy.linalg.eigvalsh`. If the top eigenvalue is positive at solver tolerance, $\lambda$ is shifted uniformly until it is $\le0$.

### 4.7 Lemma (moment shifts are paid for by Pen; bathtub)
*Unweighted shift.* Maximize $\int\sin\bar\varphi\,D$ over $0\le D\le D_{\max}$ with $\int\omega_D|w|D\le\mathrm{Pen}$. This is a linear program with box constraints. By the bathtub principle its maximum $\mu_0^{\max}(\mathrm{Pen})$ is attained by $D=D_{\max}$ on a superlevel set of $\sin\bar\varphi/(\omega_D|w|)$. The code computes it exactly on a fine grid, using cellwise sup/inf so the bound is conservative. Here $\omega_D=\xi\cos\bar\varphi$ on $E$ and $\zeta$ on $L$, and $D_{\max}=a_2-a_1\cos\delta+\varepsilon\max\bar v^2$.
*Weighted shift.* $\le c_w\mathrm{Pen}$ (§4.4).
*A-priori penalty bound.* By Lemma 4.0, $\mathrm{Pen}\le\mathrm{Pen}_{\max}:=\big(\xi/(c_E(1-c_{\rm abs}))+\zeta\big)E_0$. Hence
$$W_z-J_0\le U_{\rm tot}:=V_\lambda+\max_{0\le\mathrm{Pen}\le\mathrm{Pen}_{\max}}\Big[\rho_0\big(M^v_0+\mu_0^{\max}(\mathrm{Pen})\big)^2+\rho_w\big(M^v_w+c_w\mathrm{Pen}\big)^2-\mathrm{Pen}\Big].$$
On a grid, the maximum is bounded by pairing right-endpoint shifts with the left-endpoint Pen. *Audit repairs.* (W2) For R1 the weight in $\int\hat c|\dot h|^2$ must be a pointwise upper bound integrated exactly. The code uses $\hat c(s)=\varepsilon\frac{J_a}{J_t}\frac{\tau_r}{J_a}s/\cos\bar\varphi_{\rm sub}$, which is linear on each quadrature sub-cell, so Gauss quadrature is exact. (W3) The remainder constants use the sup of $|w|$ at the cell endpoints, not the maximum over Gauss nodes. Both repairs are in `certificate2.py`; [verify-tvc] confirmed that the stored certificates pass with them. *Remainder (Lemma 4.6′):* the Finsler terms are split with their own parameter $\tau_\rho=0.2$. Since $|g_0''|\le a_2$ and $|g_w''|\le a_2\max(s^*,t_f-s^*)$, their contribution is $\le(1/\tau_\rho-1)\big(\rho_0g_0''^2+\rho_wg_w''^2\big)h_c^4t_f/64$.

### 4.8 The witness (planar dive-then-brake, ORDINARY control)
Planar meridian $b=\cos\psi\,e_z+\sin\psi\,u$, landing with $\psi,\dot\psi=0$ at both ends.
- On $E$: $T=\rho_1$ and the gimbal sits at **full** deflection $\pm\delta$ in the plane, so $p=a_1\cos\delta$ and $\ddot\psi=\pm K_1$. The optimized profile is piecewise constant on 100 cells. Every early cell whose value $n_k$ has $|n_k|<K_1$ is flown as exact bang-bang $(+K_1,-K_1,+K_1)$ (or its mirror) with switch times $a=(h-d)/2$, $b=(h+d)/2$, $d=h(1-|n_k|/K_1)/2$. This reproduces $\psi$ and $\dot\psi$ at the cell end exactly (`segments_bangbang`). Fix of [adversary-6dof] finding (1): v1 evaluated such cells with $p=a_1\cos\delta$, which silently assumed chattering. A partial-deflection realization loses 95% of the gain; the bang-bang realization loses $3\cdot10^{-9}$.
- On $L$: $T=\rho_2$ and the gimbal angle $\mu$ satisfies $a_2\sin\mu=\varepsilon|n|$, so $p=\sqrt{a_2^2-\varepsilon^2n^2}$.

$W_z=\int w(p-\varepsilon\dot\psi^2)\cos\psi$ is evaluated segment by segment, with closed-form $\psi$ and midpoint quadrature on about 40000 sub-steps per second. The end state is upright at rest to $10^{-16}$. For the state constraints, $v_z<0$ on $[0,t_f)$ gives $r_z>0$ (in fact $y_z>\varepsilon$, so $r_z>\varepsilon(1-\cos\psi)\ge0$, as noted by [adversary-6dof]); $\min r_z/|r_h|$ gives the admissible glide slope. By Lemma 2.4 the rotated witness lands from $R_\pi\theta_w$. The witness is an ordinary control, so $\theta_w,R_\pi\theta_w\in F^{\mathcal X}$ with no closure argument.

### 4.9 Conclusion and quantitative bound
If $\theta\in F$ with $\|\theta-\theta_m\|\le d$, then $|v_{0h}|,|r_{0h}|\le d$, which replaces $M^v_j$ by $M^v_j+d$, and $\ell(\theta)\ge\ell(\theta_m)-d\sqrt{1+s^{*2}}$. So $G_w-d\sqrt{1+s^{*2}}\le U_{\rm tot}(d)$. Bisection gives $d_*$. ∎

## 5. Variants and scope

### 5.1 Box gimbal
The box satisfies $\mathcal C_{\rm box}(b)\subseteq\mathcal C_{\delta^*}(b)$ with $\delta^*=\arccos(\cos^215^\circ)$. The witness runs along a diagonal: at the corner it gives $p=a_1\cos\delta^*$, $|q|=a_1\sin\delta^*$, and late gimbal angles $\le\delta^*$ along the diagonal are available. With $\omega_3\equiv0$ the box does not rotate, and $R_\pi$ maps the box to itself. So TVC-1 applies with $\delta=\delta^*$ (table row "box").
### 5.2 Glide slope
The witness has $\min_{t<t_f} r_z/\|r_h\|$ as in the table, so every $\gamma_{gs}$ with $\tan\gamma_{gs}$ below it is covered. The competitor bound uses no state constraint.
### 5.3 Gimbal-rate limit
The competitor class shrinks, so $U_{\rm tot}$ stays valid. The witness must be rate-feasible from a centred gimbal. `witness_ratelim.py` optimizes it (state $\mu$, $|\dot\mu|\le100^\circ$/s, free throttle): for a gimbal centred at $t=0$ and slewing at 100°/s, the best witness found has gain $-4.8\cdot10^{-3}$ against $J_0$. The baseline $J_0$ assumes instantaneous full deflection on $E$. Reaching 15° takes 0.15 s, 60% of the dive, and that alone costs about $a_1(1-\cos\delta)\int(s^*-s)\approx5\cdot10^{-3}$. **The rate-limited class therefore needs its own certificate**, with the baseline replaced by the rate-limited optimum of the vertical problem. Open. (The optimizer also fails to recover the unlimited witness at $10^5$°/s, so these rate-limited numbers are inconclusive as an optimum. The baseline mismatch is the robust part.)

*Rate-limited class: why a new certificate is needed (analysis).* Even against the rate-limited baseline $J_0^{\rm rl}=-\int_E(s^*-s)a_1\cos\delta(s)+a_2(t_f-s^*)^2/2$, with $\delta(s)=\min(\dot\gamma s,\delta)$, the best rate-limited witness has a **negative** gain: $-1.5\cdot10^{-3}$ ($t_f=1$, $s^*=0.25$) and $-7.4\cdot10^{-3}$ ($t_f=3$, $s^*=0.5$); see `witness_rl.py`. The reason is that without chattering, early deflection produces torque, so the deflection credit in $J_0^{\rm rl}$ is unattainable. The correct baseline is the vertical one, $J_0^{\rm vert}=-\int_E(s^*-s)a_1+a_2(t_f-s^*)^2/2$. The deflection credit $a_1-\sqrt{a_1^2-\varepsilon^2|\ddot h|^2}\le\varepsilon^2|\ddot h|^2/(a_1(1+\cos\delta))$ then enters $\mathcal Q$ as a gain term **quadratic in $\ddot h$**. With only $|\ddot h|\le K$, the S-procedure must pay for it pointwise: high-frequency $\ddot h$ yields this gain at no tilt cost, which is exactly chattering. So the rate limit itself has to enter the bound. **Route (open):** add the jerk constraint $|\dddot h|\lesssim a\dot\gamma/\varepsilon$, which comes from $|\dot\mu|\le\dot\gamma$, with its own S-procedure multiplier. Discretize with continuous piecewise-linear $\ddot h$; remainders become cell-local again. This is a genuine extension of the certificate and has not been done.

*Numerics for the rate-limited GTPL model.* Full 6DOF ([adversary-6dof]'s `m3tvc.py` via `exp3.py`): quaternion attitude, Euler equations, gimbal angle as a state with 100°/s per axis from centred, **mass depletion**, roll free, $r_z\ge0$ at every node, upright at rest, $N=60$–80. Outputs: `numerics/proof-tvc/ratelim_numerics/`.

| gimbal (100°/s, centred) | tf (s) | s* (s) | free max ℓ (m) | zero-lateral max ℓ (m) | gap (m) | robustness | source |
|---|---|---|---|---|---|---|---|
| Cardan box | 3 | 0.75 | 8.66714 | 8.65451 | 1.26e-2 | zero-lateral starts agree to 2e-5 | proof-tvc run of `exp3.py` |
| cone | 3 | 0.5 | 9.60118 | 9.59859 | 2.6e-3 | **weak**: zero-lateral starts spread 4e-3, free starts spread 4.5e-3 | proof-tvc run |
| Cardan box | 5 | 0.5 | 31.01143 | 31.00658 | 4.8e-3 | one zero-lateral optimum + continuation | proof-tvc run |
| Cardan box | 5 | 1.0 | 26.44276 | 26.41461 | 2.8e-2 | < 1e-5 | [adversary-6dof] |
| Cardan box | 7 | 1.0 | 58.63996 | 58.60733 | 3.3e-2 | 6e-4 | [adversary-6dof] |

Verdict: the rate-limited GTPL landing set is **nonconvex but unproved** on the dive-then-brake face. It is not "possibly convex": every horizon tried shows a positive gap, with free maximizers that have nonzero lateral data. The NLPs are discretized and local (2–3 starts), so the gaps are evidence, not bounds; the cone $t_f=3$ entry is within optimizer spread.

### 5.4 Free final time
By RR-LS (math/redteam-reform §4) it suffices that $\theta_m(t^\circ)\notin\bigcup_{t\in W}F_t$. Since $\Lambda$ does not depend on the horizon, a competitor at horizon $t$ satisfies $\ell(\theta)\le J_0(t)+\kappa(t)+U_{\rm tot}(t)$. Here $J_0(t)+\kappa(t)$ is increasing in $t$ (derivative $A_b(t-s^*)>0$). Taking $t^\circ=t_b$ gives a sufficient condition:
$$G_w(t_b)>\max_{t\in[t_a,t_b]}\Big[U_{\rm tot}(t)-\tfrac{A_b}2\big((t_b-s^*)^2-(t-s^*)^2\big)\Big].$$
This needs certificates on a continuum of $t$. We have checked it only on a grid, so TVC-F remains conditional.
### 5.6 Long horizons ($t_f\ge3$ s)
**(A2) removed.** $\Pi=a_2-fb_z\ge b_z|a_2-f|$ for either sign of $f$: if $f\ge0$, $\Pi=(a_2-f)+f(1-b_z)$; if $f<0$, $\Pi=a_2+|f|b_z\ge b_z(a_2+|f|)$. The moment penalty therefore uses $\omega_D=\zeta\cos\bar\varphi$ late. No assumption $f\ge0$ is needed anywhere.
**(A1) remains.** We need $b_z>0$ throughout.
- Without a cap, the crude speed lemma gives (A1) only for $K_2t_f^2/8<\pi/2$, i.e. $t_f\lesssim2.3$ s.
- With $b_z\ge0$ one has $\Pi\ge0$. When $b_z<0$, $\Pi<0$ requires $\varepsilon v^2>a_2+a_1\cos\delta$, i.e. $v>3.6$ rad/s, a fast upside-down spin.
- A lemma excluding tumbling for competitors with gain $\ge0$ would remove (A1) altogether. It is open; the obstacle is that $v$ has no a-priori bound beyond $K_2\min(s,t_f-s)$.

**Tilt-capped class.** If the problem class includes a tilt cap $b_z\ge\cos\theta_{\max}$ with any $\theta_{\max}<90^\circ$, then (A1) holds at every horizon. GTPL's flight software aborts at 30°, and Szmuk-type 6DOF formulations carry such a cap. Lemma 4.0 then localizes, with the splitting $\kappa$ chosen adaptively so that $c_{\rm abs}\le\frac12$. GTPL, cap 30°:

| $t_f$ | $s^*$ | $G_w$ (m) | ideal zero-lateral bound / $G_w$ | rigorous certificate |
|---|---|---|---|---|
| 1 | 0.25 | 7.27e-5 | 0.67 | PASS (§3) |
| 3 | 0.5 | 1.358e-3 | 0.70 | not certified (see below) |
| 5 | 0.5 | 1.359e-3 | — | — |
| 5 | 0.75 | 7.58e-3 | — | localization gives $\bar v=2.0$ rad/s, tilt bound reaches the cap |

**Bootstrap localization.** A tilt bound $\varphi\le\varphi_1$ proved in one pass for *all* competitors with gain $\ge0$ may be used as $b_z\ge\cos\varphi_1$ in the next pass; iterate to a fixed point (`localize.py`). This is not circular, because each pass is rigorous for the whole class. With it, any cap $\theta_{\max}<90^\circ$ gives the same localized bounds as a 30° cap. At $t_f=3$, $s^*=0.5$ the bounds are tilt $\le0.23$ rad and $v\le0.83$ rad/s, for cap 30° or 80° alike. In the uncapped class at $t_f=2$, where (A1) holds a priori, the bounds are the same.

**Rigorous attempts at $t_f\ge2$, none of which passes yet:**

| run | SDP part | remainder floor | moment term | vs $G_w=1.356\cdot10^{-3}$ |
|---|---|---|---|---|
| $t_f=2$ uncapped, $N=80$ Clarabel, $(\rho_0,\rho_w)=(0.3,30)$ | 1.25e-3 | 5.6e-4 (inside SDP part) | 4.4e-3 | FAIL |
| $t_f=2$ uncapped, $N=100$ SCS | solver obj. 9.6e-4 | — | — | SCS inaccurate; repair failed |
| $t_f=3$ cap 30°, $N=150$ SCS | solver obj. 1.37e-3 | — | — | FAIL |

**Obstacles, quantified.**
- (i) The *moment-shift* term. The bathtub cap is $\rho_0\lesssim\omega_D/(4H^2D_{\max})$ with $H=\bar\varphi_{\rm loc}(s^*)$. Localization only gives $H\approx0.23$ rad, against a witness tilt of $0.04$ rad, so $\rho_0\lesssim0.05$, and $c_w\mathrm{Pen}_{\max}$ is large. A sharper localization is needed: energy relative to the gain threshold $G_w$ instead of $E_0\approx6G_w$, or a two-sided (time-sliced) Agmon bound near $s^*$.
  *Why (i) is structural for this face.* On the face $\int(s-s^*)fb_z$, throttle near the switch time $s^*$ is first-order free, because the weight vanishes there. A zero-lateral competitor can shift $v_{0h}$ by $\mu\approx h(s^*)\,Y$, where $Y=\int_{|w|<\eta}D$, at cost $\approx Y^2/(4D_{\max})$. The true price of a moment shift is therefore $\approx1/(4D_{\max}h(s^*)^2)$, about 20 for witness-scale tilt. Our bound must replace $h(s^*)$ by an a-priori $H$ (0.23 rad, against 0.04) and the penalty by a fraction $\omega\approx0.1$. Together these lose a factor of about 300. Any product bound $h^2\mathrm{Pen}\le\theta H^2\mathrm{Pen}+(1-\theta)\mathrm{Pen}_{\max}h^2$ leaves either a large $\rho_0H^2$ or a large rank-one term $\propto\mathrm{Pen}_{\max}x(s^*)^2$. The fix needs a localization of $\mathrm{Pen}$ relative to $G_w$ (not $E_0\approx6G_w$), or a face whose weight does not vanish where the throttle switches.
- (ii) The *discretization floor*, $\propto h_c^2\times$ the weights. These weights grow with $t_f$ because $|w|\le t_f-s^*$. That needs $N\gtrsim150$ on $[0,3]$, beyond accurate dense interior-point solves here (SCS is inaccurate at $2N=300$). The fix is a banded/sparse SDP formulation, since the form is a sum of cell-local and low-rank terms, or a higher-degree cell basis with an $(h/3\pi)^2$-type Wirtinger constant.
- (iii) The ideal (no-remainder) ratio stays favourable: 0.70 at $t_f=3$. So the obstruction is in the rigorous overheads, not in the geometry. [adversary-6dof]'s full-6DOF numerics at $t_f=5,7$ (gaps $\approx3\cdot10^{-2}$ m with $s^*=1$) support the same conclusion.

The witness gain depends on $s^*$ but not on $t_f$, once the brake phase is long enough to return upright. **Caveat:** the capped class is a different problem class. Nonconvexity of $F^{\rm cap}$ does not imply nonconvexity of the uncapped $F$, and vice versa.

### 5.7 Theorem TVC-2: $t_f=2$ s, no tilt cap, via a state-space (Riccati) certificate
**Statement.** Setting of TVC-1 (constant mass, $\omega_3\equiv0$, cone 15°, unlimited gimbal rate, upright at rest, $r_z\ge0$, glide slope with $\tan\gamma_{gs}\le37$), GTPL wet constants, **$t_f=2$ s, no tilt cap**, face $s^*=0.5$ s. Then $F^{\mathcal X}_{t_f}$ is nonconvex, and $\operatorname{dist}(\theta_m,F_{t_f})\ge9.2\cdot10^{-5}$ m. That distance is 10× the $t_f=1$ value.

**Proof.** It is the inequality chain of §4 with the following changes:
- (A2) is not used; see §5.6, where $\Pi\ge b_z|a_2-f|$ and $\omega_D=\zeta\cos\bar\varphi$.
- (A1) holds a priori at $t_f=2$, since $K_2t_f^2/8=1.20<\pi/2$.
- Lemma 4.0 is iterated to a fixed point (bootstrap). The result is tilt $\le0.23$ rad and $v\le0.83$ rad/s.
- Parameters: $\zeta=\xi=0.15$, $\kappa=0.03$, $\lambda_{\max}=0.01$, $(\rho_0,\rho_w)=(0.1,45)$, $\tau=0.03$, $\tau'=0.01$, $\tau_\rho=0.2$.
- **The discrete matrix inequality is checked by a backward Riccati recursion instead of a dense SDP.** Write $n=a_k+b_k(t-c_k)$ on cell $k$, and use the state $z=(x,\dot x,m_0,m_w)$, where $m_0,m_w$ are the running moment integrals. The quadratic form of (C), with the multiplier, is $\sum_k[z_k;u_k]^\top S_k[z_k;u_k]$ plus the terminal Finsler/clamp form, with $z_0=0$ and $z_{k+1}=T_k[z_k;u_k]$. The cellwise $\lambda_kL_k$ terms are now kept exactly, not replaced by $\lambda_{\max}$. The form is negative definite if every pivot block $H^{uu}_k$ of the backward recursion $H_k=S_k+T_k^\top P_{k+1}T_k$, $P_k=H^{zz}_k-H^{zu}_k(H^{uu}_k)^{-1}H^{uz}_k$ is negative definite (dynamic programming).
  - Cost is $O(N)$, so we use $N_f=600$ cells ($h=1/300$). The Lemma 4.6′ remainder floors are then negligible.
  - The multiplier $\lambda$ comes from a coarse no-floor SDP ($N_c=60$; *not* part of the proof). It is interpolated, scaled by the smallest feasible factor (0.979) times a safety factor of 1.02, and the floors are added.
  - The recursion is re-run in **Arb ball arithmetic** (256 bits) on rationalized data, with the stage matrices inflated by $10^{-10}\cdot\max|S_k|\cdot I$ in the PSD (conservative) direction. Every $-H^{uu}_k$ is certified positive definite via $-H^{uu}_{11}>0$ and $\det>0$.
  - The routine was cross-validated against the dense eigenvalue test at $t_f=1$, $N=20$, where the two agree in sign at all tested scalings.

**Numbers** (`riccati_cert.py`, `verify_riccati.py`; data `riccati_2.0_0.5_none_600.npz`):

| $V_\lambda$ | moment term | $U_{\rm tot}$ | $G_w$ (ordinary bang-bang witness) | margin |
|---|---|---|---|---|
| 1.23404e-3 | 1.29e-5 | 1.24692e-3 | 1.35610e-3 | 8.05% |

The witness lands upright at rest to $10^{-16}$, with $v_z<0$ on $[0,t_f)$.

**Status: CONFIRMED (computer-assisted).** [verify-tvc] independently re-certified the result (math/verify-tvc-report.md §9). They re-assembled every stage matrix by exact polynomial integration (fmpq × Arb, exact $h=1/300$, exact $g_0,g_w$) and ran the recursion in Arb with no inflation: all 600 $-H^{uu}_k\succ0$. The certified values are $U\le1.246811\cdot10^{-3}$, rigorous $G_w\ge1.356101\cdot10^{-3}$, margin 8.06%, $d_*\ge9.23\cdot10^{-5}$ m. The moment term is $\le1.2771\cdot10^{-5}$ (Arb LP dual). [adversary-6dof]: SURVIVES. Minor fix W1′: an exact rational correction of the last two witness cells, so the end state is exactly upright at rest; $G_w$ is unchanged. Glide-slope ratio 37.8.
**Scope of TVC-2:** roll held (R0), 15° cone, constant mass, unlimited gimbal rate. The box and roll-free (R1) cases at $t_f=2$ are not run. The float-rounding of $g_0,g_w$ in my own Arb run is moot after the auditor's exact rebuild.

**Tilt-capped $t_f=3$:** see §5.6. The same pipeline applies; the result is in the table there.

### 5.8 Theorem TVC-3: $t_f=3$ s, tilt-capped class
**Statement.** Setting of TVC-2, but in the **problem class with a tilt cap** $b_z\ge\cos\theta_{\max}$, for either $\theta_{\max}=80^\circ$ or $30^\circ$ (the certificate is identical). GTPL wet, $t_f=3$ s, $s^*=0.5$ s, altitude $r_z\ge0$. The glide slope is *not* claimed: the witness's $\min r_z/|r_h|$ is only $1.5\cdot10^{-4}$. Then $F^{\mathcal X,\rm cap}_{t_f}$ is nonconvex, with $\operatorname{dist}(\theta_m,F^{\rm cap}_{t_f})\ge4.78\cdot10^{-5}$ m.
**Proof.** As in TVC-2, with the Riccati certificate on $N_f=900$ cells ($h=1/300$).
- The cap is used only for (A1). The bootstrap localization gives the same bounds for every cap $<90^\circ$: tilt $\le0.228$ rad and $v\le0.829$ rad/s.
- The multiplier is the certified TVC-2 multiplier, extended by $0$ on $(2,3]$ (where $M_{\rm late}$ dominates). It is scaled by the smallest feasible factor (1.0044) times a 1.02 safety factor, plus the fine floors.

| $V_\lambda$ | moment term | $U_{\rm tot}$ | $G_w$ | margin | float recursion | Arb recursion |
|---|---|---|---|---|---|---|
| 1.28909e-3 | 1.30e-5 | 1.30211e-3 | 1.35849e-3 | 4.15% | worst pivot $-9.1\cdot10^{-5}$ | PASS |

Data: `riccati_3.0_0.5_{30,80}_900.npz`. Re-check: `ETA1=0.0667 ZETA=0.15 LAMMAX=0.01 KAP=0.03 python verify_riccati.py 3.0 0.5 900 80 0.1:45`.
**Status: CONFIRMED (computer-assisted).** [verify-tvc] gives an exact re-certification for both caps: $U\le1.302013\cdot10^{-3}$, rigorous $G_w\ge1.358494\cdot10^{-3}$ after the W1′ terminal correction, margin 4.16%, $d_*\ge4.79\cdot10^{-5}$ m, all 900 Arb pivots certified, moment term $\le1.2923\cdot10^{-5}$ (math/verify-tvc-report.md §10). *Glide slope:* the auditor's full 6DOF simulation of the witness gives $\min r_z/|r_h|=87.8$ over $t<t_f$. My evaluator's $1.5\cdot10^{-4}$ is a near-touchdown artefact of its backward position integration. So the glide slope with $\tan\gamma_{gs}\lesssim87$ holds, per the auditor's simulation. **Caveat:** this is a theorem about the tilt-capped class; uncapped $t_f=3$ would need a tumbling-exclusion lemma for (A1).

### 5.9 Theorem TVC-5: $t_f=5$ s, tilt-capped class (a realistic horizon)
**Statement.** Setting of TVC-3 (tilt cap $80^\circ$ or $30^\circ$, roll held, 15° cone, constant mass, unlimited gimbal rate, upright at rest, $r_z\ge0$). GTPL wet, **$t_f=5$ s**, $s^*=0.5$ s. Then $F^{\rm cap}_{t_f}$ is nonconvex, with $\operatorname{dist}(\theta_m,F^{\rm cap}_{t_f})\ge2.3\cdot10^{-6}$ m.
**Certificate.** Riccati/DP on $N_f=1500$ cells ($h=1/300$).
- The multiplier is the TVC-2 multiplier, zero-extended and scaled by 1.0726. It is then reduced by two sweeps of block-coordinate descent (60 blocks), each block checked with the fine recursion, with safety factor 1.002.
- The witness is re-optimized on 500 cells and flown as ordinary bang-bang. It ends upright at rest to $10^{-15}$, with $v_z<0$.

| $V_\lambda$ | moment term | $U_{\rm tot}$ | $G_w$ | margin | Arb recursion | fresh re-check |
|---|---|---|---|---|---|---|
| 1.348479e-3 | 1.34e-5 | 1.361833e-3 | 1.364543e-3 | **0.20%** | PASS | PASS (both caps) |

The margin is thin: $2.7\cdot10^{-6}$ m absolute. It is still about 1000× the float and quadrature error estimates (≤ $10^{-9}$). Data: `riccati_5.0_0.5_{30,80}_1500.npz` (= `tvc5_cap80_cert.npz`) and `witness_cone_5.0_0.5.npy` (the $N=500$ witness).
**Status: CONFIRMED (computer-assisted).** [verify-tvc] re-certified it exactly for both caps (math/verify-tvc-report.md §11): $U\le1.361771\cdot10^{-3}$, rigorous $G_w\ge1.364543\cdot10^{-3}$ ($\pm5\cdot10^{-13}$) after the exact terminal correction, margin $2.77\cdot10^{-6}$ m, $d_*\ge2.48\cdot10^{-6}$ m, all 1500 Arb pivots certified, glide ratio 299 in the 6DOF sim. Caveat from the audit: the Arb ball radius grows roughly exponentially with $N_f$, so use higher precision for longer horizons.

### 5.5 Variable $\varepsilon$, mass depletion
Not covered. With $\alpha>0$, $\varepsilon(m(t))$ gives $\ddot y$ the extra terms $2\dot\varepsilon\dot b+\ddot\varepsilon b$, and $\ddot\varepsilon$ contains $\dot T$, which is unbounded for relaxed throttle. The late baseline also moves by $\alpha\rho_2(\rho_2-\rho_1)s^*/m^2\cdot\int_Lw\approx4\cdot10^{-3}$ m, which is far larger than the gap. A certificate for the $\alpha>0$ class needs the competitor's own mass history inside Pen ([adversary-6dof] A2). **Open.** TVC-1 is a theorem about the constant-mass class. That class is the standard LCvx idealization, but it is not literally GTPL.

## 6. What remains open

**Final state (2026-11-07 ~03:40).**
- **Certified, computer-assisted, CONFIRMED by [verify-tvc] in exact arithmetic.** Constant mass, roll held (plus roll-free at $t_f=1$), 15° cone (plus box at $t_f=1$), unlimited gimbal rate, upright at rest, $r_z\ge0$:
  - TVC-1, $t_f=1$, uncapped;
  - **TVC-2, $t_f=2$, uncapped**;
  - TVC-3, $t_f=3$, tilt cap 80°/30°;
  - **TVC-5, $t_f=5$, tilt cap 80°/30°** (margin 0.20%).
- **Numerical only.**
  - $t_f=7$: the certificate fails by 4.8%, with the best generator from $t_f=5$. The idealized bound is still below $G_w$, so a better multiplier generator should close it.
  - The rate-limited, mass-depleting full-6DOF model is nonconvex in [adversary-6dof]'s simulations (§5.3).
- **Open:** all items below.

**Long-horizon method (implemented; §5.7–5.9).** The dense SDP is replaced by a state-space (Riccati/DP) recursion, cost $O(N)$, re-run in Arb. The multipliers come from a coarse SDP at $t_f=2$, then zero-extended and block-reduced.
- Coarse dense SDPs at $t_f\ge3$ fail numerically (Clarabel). A Kelley cutting-plane search on the fine recursion was tried and did not converge in 1600 cuts.
- To reach $t_f\ge6$, the remaining work is a proper multiplier optimizer on the recursion, e.g. a bundle/trust-region method or a dual (covariance) formulation.

**(Historical) route proposed before the Riccati certificate was implemented.** Replace the dense $2N\times2N$ SDP by a **state-space (Riccati/dissipation) certificate**. Use the augmented state $z=(x,\dot x,\int f_0x,\int wf_0x)$ and a time-varying quadratic storage $z^\top P(t)z$ satisfying a pointwise LMI, i.e. a Riccati differential inequality; the Finsler terms become terminal costs. This scales linearly in $t_f$, removes the dense-SDP size wall, and can be validated with interval ODE enclosures. Combine it with the moment lemma $\mu_0\le|h(s^*)|\,Y+\bar v\int|w|D$. That lemma replaces the crude tilt $H$ at $s^*$ by the competitor's own $h(s^*)$, through a rank-one PSD term $\propto x(s^*)^2$, at the price $4\rho_0D_{\max}\mathrm{Pen}_{\max}/\omega$.
1. **Realistic horizons (5–8 s), uncapped.** (A2) is removed (§5.6). (A1), i.e. $b_z>0$, fails for $t_f\gtrsim2.3$ s with the crude a-priori bounds of Lemma 2.2; the tilt-capped class (§5.6) avoids it. A localization lemma would extend the method: a competitor with gain $\ge0$ has small late tilt and rate, by an energy bound plus Lipschitz bootstrap. The certificate would also need to scale, roughly $N\propto t_f$, and the SDP cost grows with $N$.
2. Mass depletion / varying $\varepsilon$ (§5.5).
3. A rate-limited witness that beats $U_{\rm tot}$, or a bound tailored to the rate-limited class (§5.3).
4. Non-axisymmetric $J$, aerodynamic torque, wind (wind breaks the $R_\pi$ symmetry).
5. A formal (interval-arithmetic or Lean) check of the SDP certificate. The rest of the proof is Lean-ready (math/03 §Pure TVC).
6. A *non*-thin face for the constrained problem (practical ε-impossibility). As for M1 (math/02 Rem. 10.2), none is known.
