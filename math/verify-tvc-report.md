# VERIFY-TVC: independent audit of the pure-TVC computer-assisted proof (math/06, TVC-1 / 1q / B / 1R / L)

Auditor: [verify-tvc], 2026-11-07. Brief: `comms/briefs/verify-tvc.md`. Scripts: `numerics/verify-tvc/` (own venv: numpy, scipy,
mpmath, python-flint 0.9.0 (FLINT/Arb), casadi). Audited versions: `math/06-pure-tvc.md` (mtime 01:53, 222 lines; the
long-horizon §5.6 added during the audit is **not** covered), `numerics/proof-tvc/{certificate2.py, localize.py,
verify_cert.py, witness_nl.py}` and the stored certificates `cert2_*_1.0_0.25_*.npz`, witnesses `witness_{cone,box}_1.0_0.25.npy`.

## 0. Verdict

| Component | Verdict | Notes |
|---|---|---|
| Model reduction (Lemma 2.1 CoP identity, 2.2, 2.3, 2.4; relaxed ⊇ ordinary) | **CERTIFIED** | Re-derived. Relaxation of $u=Td/m$ is valid because both force and torque are affine in $u$. The rotation-midpoint argument is correct, and "zero lateral data" ($r_{0h}=v_{0h}=0$) is exactly the condition $\theta_m$ satisfies. |
| Witness (§4.8) | **NEEDS FIX → repaired and CERTIFIED** | **W1:** the stored witness is **not** bang-bang. All 25 early cells have $\lvert n\rvert<K_1$ (cell 9 is at $0.865K_1$). Evaluated with $p=a_1\cos\delta$, it is therefore a *relaxed* (chattering) control, which contradicts §3 Remark and §4.8. Flown literally without chattering, its gain is only $3.5\cdot10^{-6}$, so the certificate would fail. **Repair:** an explicit ordinary control, bang-bang $\pm\delta$ with cell-moment matching. Its gain is $G_w\in[7.269369140\cdot10^{-5}\pm3\cdot10^{-15}]$ (Arb, rigorous). It lands exactly upright at rest, satisfies $r_z>0$ and the glide slope, and is confirmed by a full quaternion rigid-body simulation. |
| Pointwise majorants §4.2, torque remainders §4.3, moments §4.4, S-procedure/Finsler §4.5 | **CERTIFIED** | Every inequality re-derived. The remainder constants are correct, and they hold on the localized region (localized bounds are used only for competitors with gain ≥ 0; the crude bounds are used for (A1)/(A2)). |
| Localization Lemma 4.0 (TVC-L) | **CERTIFIED** | Re-derived. An independent re-implementation (closed-form $E_0$ and $c_{\rm abs}$, closed-form $\bar Y$ and Agmon) gives bounds that proof-tvc's step functions dominate on all 20000 cells (R0 cone, R0 box, R1). |
| Discretization → continuum, Lemma 4.6′ | **CERTIFIED** | Every step checked: cell-locality of $x'',\dot x''$; Wirtinger constant $(h/2\pi)^2$ (correct, because $\dot x''$ has zero ends *and* zero mean); $\lVert x''\rVert_\infty^2\le h^3/4\pi^2\lVert n''\rVert^2$; Finsler remainder $h^2/8\,\sup\lvert F''\rvert\sqrt{t_f}$; exact orthogonality of the $\lambda$ and $M_{\rm late}$ terms; PSD/NSD splitting. Numerically, the continuous form restricted to 3× and 6× refined spaces has top eigenvalue $-5.1\cdot10^{-6}<0$. Minor non-rigour W3: `remainder_constants` takes the max over interior Gauss nodes, not the sup. Recomputed with the true sup, it still passes. |
| SDP certificate inequality (numerical rigour) | **CERTIFIED (exact)** | `verify_cert.py` is a floating-point check only; its Cholesky test has a zero margin. I re-assembled every matrix **independently by exact polynomial integration**: fmpq for the polynomial part, Arb balls for the transcendental coefficients. It agrees with proof-tvc's matrix to $1.2\cdot10^{-12}$ (scaled). I then decided $-M\succ0$ by **exact integer Sylvester minors** (FLINT determinants of the 64-bit-rounded, congruence-scaled midpoint matrix, minus the Frobenius bound on ball radius and rounding). The remainder conditions, absorption (i), $\lambda\le\lambda_{\max}$, $V_\lambda$ and the moment term were all checked in Arb. |
| TVC-1R (free roll RCS) | **NEEDS FIX → repaired and CERTIFIED** | **W2:** the gyro lateral-force weight $\int c\lvert\dot h\rvert^2$ (`Vall`) is computed by Gauss quadrature of a non-polynomial weight at node values, so it is not an upper bound. With the crude sub-cell sup weight the same $\lambda$ **fails** (top eigenvalue $+1.05\cdot10^{-7}$). With the exact linear upper weight $\hat c(s)=\varepsilon\frac{J_a}{J_t}\frac{\tau_r}{J_a}s/\cos\bar\varphi_{\rm sub}$, integrated exactly, it **passes** exactly (margin 3.99%). |
| **Overall (TVC-1 cone, TVC-B box, TVC-1R, TVC-1q, TVC-L at $t_f=1$ s)** | **CERTIFIED, subject to repairs W1 and W2** (both carried out and verified here) | No BROKEN item. The claimed numbers are reproduced: margins 13.70% / 5.40% / 3.99%, $d_*$ = 9.63e-6 / 7.34e-6 / 2.81e-6 m. |

## 1. Mathematics (hostile pass over math/06)

**M1. Model and relaxation.**
- Ordinary controls: $T\in[\rho_1,\rho_2]$ and $\angle(d,b)\le\delta$. Torque $\tau_\perp=-LTb\times d=-Lm\,b\times u$ is affine in $u=Td/m$, and so is the force. Relaxed trajectories are therefore exactly those with $u(s)\in\operatorname{conv}=\mathcal C(b(s))$.
- §1 PT6 describes $\mathcal C$ correctly: the convex hull of the cap $\{ad\}$ is cone ∩ ball ∩ $\{\langle u,b\rangle\ge a_1\cos\delta\}$. Only "$\subseteq$" is needed.
- Hence $F\subseteq F^{\rm rel}$, and $\theta_m\notin F^{\rm rel}$ implies $\theta_m\notin F$. This step is valid.
- Under R0, axisymmetric $J$ and gimbal torque $\perp b$ give $J_a\dot\omega_3=\tau_3=0$, so $\omega_3\equiv0$ needs no RCS effort.

**M2. CoP identity, Lemma 2.1.** $\varepsilon\nabla\dot b=-q+\varepsilon\frac{J_a}{J_t}\omega_3b\times\dot b$ and $\ddot y=fb+\gamma_3-g_0e_z$.
- Re-derived. For the witness it is confirmed independently: the full rigid-body simulation (§3) reproduces the CoP-model gain to $10^{-11}$.

**M3. Lemmas 2.2–2.4.**
- 2.2: $\frac{d}{dt}v=\langle\dot b,\nabla\dot b\rangle/v$, and the gyro term is $\perp\dot b$. So $\lvert\dot v\rvert\le\lvert q\rvert/\varepsilon\le K_2$, which holds for relaxed $u$ since $\lvert q\rvert\le a_2\sin\delta$. Both ends at rest then give $\bar v=K_2\min(s,t_f-s)$.
- 2.3: the landing identity was re-integrated: $r_0=\int s\,\ddot y$, $v_0=-\int\ddot y$, $\kappa=g_0t_f(s^*-t_f/2)$.
- 2.4: $R_\pi$ invariance holds for the cone. It also holds for the Cardan box, with $R(0)=I$ fixed: conjugating by $R_\pi$ maps $d_b\mapsto(-d_x,-d_y,d_z)$, which stays in the box. $\theta_m$ has zero lateral data and the same $\ell$.
- So "zero lateral" is exactly the right midpoint condition. Proving $\theta_m\notin F$ (unconstrained) is stronger than needed.

**M4. Gain decomposition and majorants (§4.1–4.2).**
- The decomposition is exact.
- Early: $1-b_z=\lvert h\rvert^2/(1+b_z)$ and $v^2\le\lvert\dot h\rvert^2/b_z^2$ (since $b_z\dot b_z=-h\cdot\dot h$). The authors' $1/\cos^2$ is conservative; $1/\cos$ would suffice.
- Late: $a_2-pb_z\ge(\lvert q\rvert^2b_z^2+a_2^2\lvert h\rvert^2)/(2a_2)$, via $a_2-\sqrt Y\ge(a_2^2-Y)/2a_2$ for $Y\le a_2^2$.
- $\Pi\ge\lvert a_2-f\rvert$, because $f\le p\le a_2$.
- Gyro: $(b\times\dot b)_z=(h\times\dot h)_z$. All checked.

**M5. Torque remainders (§4.3).**
- $\lvert\ddot h\rvert\le\lvert q\rvert/\varepsilon+\bar v^2\lvert h\rvert+c_3\lvert\dot h\rvert$ with $c_3=\frac{J_a}{J_t}\bar\omega_3/\cos\bar\varphi$.
- Early bound: $\lvert q\rvert^2/\varepsilon^2\le K_1^2+\kappa_D\Delta p$, using $\lvert q\rvert\le p\tan\delta$ and $\Delta p^2\le(a_2-a_1\cos\delta)\Delta p$. The constant $\kappa_D$ is correct.
- Late inverse bound with $1+\kappa'=1/(1-\vartheta)$: $\lvert q\rvert^2/\varepsilon^2\ge(1-\vartheta)\lvert\ddot h\rvert^2-(1/\vartheta-1)R^2$, with $R^2\le2(\bar v^4\lvert h\rvert^2+c_3^2\lvert\dot h\rvert^2)$.
- The code's $A_2^{\rm eff},B_2^{\rm eff}$ use $1/(2a_2)\ge C_2$, which is conservative. Any sub-cell choice of $\vartheta\in(0,1)$ is valid if it is used consistently in $A_2^{\rm eff}$ and in $c_2$. It is, and $M_{\rm late}$ takes the cell minimum.
- The remainders are homogeneous quadratics in $(h,\dot h)$, so attack A1 is genuinely fixed.

**M6. Moments, S-procedure, Finsler (§4.4–4.5, 4.7).**
- From $v_{0h}=0$ and $\Lambda_h=0$: $m_0=-\int[(f-f_0)h+\gamma_{3h}]$ and $m_w=-\int w[\cdots]$.
- $\lvert f-f_0\rvert\le\Delta p+\varepsilon v^2$ on $E$, and $=\lvert a_2-f\rvert$ on $L$.
- The bathtub/knapsack constraint $\int\omega_D\lvert w\rvert D\le\mathrm{Pen}$ matches the definition of Pen. $D_{\max}$ is correct on both phases.
- Absorption (i) cancels the early $\Delta p$ terms down to $-\xi\int_E\lvert w\rvert\cos\bar\varphi\Delta p$. The last $\eta_1$ cells use $\bar N=K_2$, which needs no absorption.
- Separability: every term is a sum over the two components of $h$, so the vector bound equals the scalar bound.
- The chain $W_z-J_0\le V_\lambda+\rho_0\lvert m_0\rvert^2+\rho_w\lvert m_w\rvert^2-\mathrm{Pen}$ is correct.
- For R1, the Cauchy–Schwarz step $(\int c\lvert\dot h\rvert)^2\le\int\hat c\int\hat c\lvert\dot h\rvert^2$ is valid for any $\hat c\ge c$ pointwise. Different upper weights may be used in the two factors.
- The split $(a+b)^2\le(1+\kappa_g)a^2+(1+1/\kappa_g)b^2$ produces the `kgf` and `coefV` factors.

**M7. Localization (Lemma 4.0).** Re-derived line by line.
- $v\le K_1s+\beta Y$ with $\beta=\tan\delta/\varepsilon$ and $Y=\int_0^s\Delta p$; also $\varphi\le K_1s^2/2+\beta sY$.
- $\int_0^{s^*}(s^*-s)Y^2\le\Delta p_{\max}\frac{s^{*2}}2\int\lvert w\rvert\Delta p$, which gives $c_{\rm abs}=0.1572$ (cone) and 0.3340 (box).
- Closed form: $E_0=A_1(1+k)K_1^2s^{*6}/120+B_1(1+k)K_1^2s^{*4}/12$, i.e. 4.5243e-4 (code: 4.5288e-4, which includes a ×1.001 safety factor).
- The late integral bounds use $\Pi\ge\frac{a_2}2\lvert h\rvert^2$, $\Pi\ge\varepsilon c_0v^2$ and $\Pi\ge c_0^2\lvert q\rvert^2/2a_2$.
- Agmon $\sup g^2\le\lVert g\rVert^2/\ell+2\lVert g\rVert\lVert\dot g\rVert$ is correct. Here $\lvert\dot v\rvert\le\lvert q\rvert/\varepsilon$ and $\lvert\frac{d}{ds}\lvert h\rvert\rvert\le v$.
- $\bar Y$ is valid.
- The step-function padding (true $v$ is $K_2$-Lipschitz; true $\varphi$ is $v_{\max}$-Lipschitz) is valid.
- R1 extras: the early gyro term uses crude bounds; the late gyro is absorbed into $\theta_g\Pi$ by AM-GM (the code asserts both conditions); late bounds carry the factor lat_fac $=1/(1-\theta_g)$. This is correct.
- **`loc_check.py`:** proof-tvc's $\bar v$ exceeds mine by at least $4.7\cdot10^{-5}$ and their $\bar\varphi$ by at least $1.1\cdot10^{-8}$ on all 20000 cells (cone, box, roll). No cell violates this.
- Every certificate coefficient is monotone in $(\bar\varphi,\bar v)$, so larger bounds are always safe.

**M8. Discretization (Lemma 4.6′).**
- Split $n=\bar n+n''$ with $n''\perp\{1,t\}$ on each cell. Then $\dot x''$ and $x''$ vanish at every node, because $\int_{\rm cell}n''=\int_{\rm cell}(t_j-s)n''=0$, and $\dot x''$ has zero cell mean.
- With zero ends and zero mean, the Rayleigh minimum is $(2\pi/h)^2$: the antisymmetric mode $\sin(2\pi t/h)$; the symmetric constrained mode solves $\tan x=x$ and gives $80.8/h^2$. So $(h/2\pi)^2$ is correct.
- $\lvert x''\rvert\le\sqrt h\lVert\dot x''\rVert$. Finsler: $m(x'')=\int F n''$ with $F''=f_0$ (resp. $(s-s^*)f_0$), and the linear-interpolant error is $h^2/8\sup\lvert F''\rvert$. The clamp functionals have linear representers, so their remainder is 0. The $\lambda$ and $M_{\rm late}$ terms are cell constants, so the cross terms with $n''$ vanish exactly.
- The PSD/NSD split inequalities with $(1+\tau,1+1/\tau)$ and $(1-\tau',1/\tau'-1)$ are correct. They need $K_-$ to be NSD: all late coefficients are $>0$, which my assembly asserts.
- Basis, mass matrix ($h$, $h^3/12$) and clamp rows were re-derived.
- `disc_check.py` assembles the *continuous* form, with no split factors and no remainders, on 720- and 1440-dof refinements. Top eigenvalue: $-5.12\cdot10^{-6}$ (cone N=120) and $-5.0\cdot10^{-6}$ (box). This is stable under refinement and agrees with the lemma.

**M9. Small issues (no effect on validity).**
- (a) §4.6 "Original version" text refers to `certificate.py`, which the certified numbers do not use.
- (b) $D_{\max}$ and $c_w$ use step-cell values, which is consistent.
- (c) The $\lambda_{\max}\sum_k L_k$ replacement (FASTL) is conservative.
- (d) The (A1)/(A2) checks use the crude bounds, correctly.

## 2. The witness (TVC-1 hypothesis "$\theta_w\in F^{\mathcal X}$")

**Finding W1.**
- `witness_cone_1.0_0.25.npy` has $\lvert n_k\rvert/K_1\in[0.8650,\,0.999934]$ on $E$. Not one early cell is at $K_1$; IPOPT stopped inside the bound.
- `witness_nl.evaluate` uses $p=a_1\cos\delta$ on $E$ regardless of $n$. That is the relaxed value: an ordinary control with $T\ge\rho_1$ and $\lvert q\rvert<a_1\sin\delta$ has $p\ge\sqrt{a_1^2-\varepsilon^2n^2}>a_1\cos\delta$.
- So §3 Remark ("ordinary... no chattering") and §4.8 ("the optimized profile is bang-bang $\lvert n\rvert=K_1$") are **false**.
- Flown literally ($T=\rho_1$, $\lvert\mu\rvert<\delta$), the profile has gain $3.54\cdot10^{-6}$, far below $U_{\rm tot}$.
- The box witness behaves the same way: 0.866 in cell 9; literal gain $5.1\cdot10^{-6}$.

**Repair (verified; `witness_check.py`).**
- **Early cells.** Split each early cell into $M$ sub-intervals. Each sub-interval gets a symmetric 3-piece pattern $\sigma K_1,-\sigma K_1,\sigma K_1$ with outer lengths $\alpha=\frac{h_s}4(1+\lvert\bar n\rvert/K_1)$. This is gimbal $\mp\delta$ at $T=\rho_1$, so $p=a_1\cos\delta$ holds *exactly*. Symmetry matches both $\int n$ and $\int(t_{k+1}-s)n$, so $\psi,\dot\psi$ agree with the profile at every node.
- **Late cells** keep $T=\rho_2$ and $\sin\mu=-\varepsilon n/a_2$, with $\lvert\mu\rvert\le2.3^\circ$.
- **Exact terminal attitude.** The last two cells are corrected by a rational $\Delta n\approx2.6\cdot10^{-13}$, which makes $\sum hn_k=\sum hn_k(t_f-c_k)=0$ exactly. Hence $\psi(t_f)=\dot\psi(t_f)=0$ exactly.

| quantity | cone 15° | Cardan box (corner plane) |
|---|---|---|
| rigorous $G_w$ (Arb, $M=8$) | $[7.269369140\cdot10^{-5}\pm2.5\cdot10^{-15}]$ | $[1.404382997\cdot10^{-4}\pm3.2\cdot10^{-14}]$ |
| rigorous $G_w$, coarsest $M=1$ | $7.269086\cdot10^{-5}$ (still $>U_{\rm tot}$) | — |
| relaxed value of the stored profile | 7.269374e-5 (reported 7.269e-5) | 1.404384e-4 |
| 6DOF quaternion sim (own RK4, Euler eqs., engine at $-Le_3$), $G_w=\ell-\kappa-J_0$ | 7.269369e-5 | 1.404383e-4 |
| $\lvert b(t_f)-e_z\rvert$, $\lvert\omega(t_f)\rvert$ | 1.5e-15, 1.4e-15 | 7.7e-15, 7.8e-15 |
| $r_0$, $v_0$ | (0.00782, 1.11582), (−0.02193, −0.79062) | lateral 0.01082 m, 0.03021 m/s along the corner azimuth |
| $\min_{t<t_f}r_z$; $v_z<0$ on $[0,t_f)$ | $>0$ (5e-10 at the last step); yes | same |
| $\min r_z/\lvert r_h\rvert$ (glide slope) | 116.3 (attained at $t\to t_f$) | 83.7 |
| max tilt; max gimbal | 0.451°; 15.000° (limit) | 0.627°; corner, Cardan angles ≤ 15.0000000000° |

- For the box, the segment from $e_3$ to the corner, taken in the corner-azimuth plane, lies in the Cardan box: $\lvert\sin\alpha\rvert=\sin\mu\sin\phi_c\le\sin15^\circ$ and $\tan\beta=\tan\mu\cos\phi_c\le\tan15^\circ$. The witness is planar in that vertical plane, with $\omega_3\equiv0$.
- **Scope remark:** the repaired witness makes explicit that TVC-1 uses the unlimited gimbal rate of (PT6) essentially. It needs 30° gimbal reversals on sub-millisecond intervals. This is consistent with TVC-R being open.

## 3. Numerical rigour of the certificate

**What `verify_cert.py` does.** It rebuilds the float matrix and calls `eigvalsh` (top eigenvalue $-2.98\cdot10^{-8}$). The Cholesky call `cholesky(-Ms + 0*I - 1e-14*I*0)` has **zero margin**. This is a floating-point check, not a proof, and the remainder constants use interior quadrature nodes (W3). I reproduced its output: U = 6.273567e-05, PASS.

**My pipeline (`exact_cert.py`, independent).**
1. Constants are exact rationals; $\delta=\pi/12$ (or $\arccos\cos^2(\pi/12)$) is an Arb ball at 200 bits.
2. On every sub-cell ($3N$ of them), the 2N basis functions are written as exact polynomials in $\sigma=s-{\rm lo}$. The matrices $\int\lvert s-s^*\rvert XX^\top$, $\int\lvert s-s^*\rvert\dot X\dot X^\top$, $\int XX^\top$, $\int\dot X\dot X^\top$ (and $\int s\dot X\dot X^\top$ for R1) are exact fmpq matrices. They are multiplied by Arb coefficients ($\cos\bar\varphi$, $\vartheta$, …). $G_0,G_w$ and the clamp rows are exact moments.
3. $M_{\rm late}$ is the exact minimum of the step-linear multiplier, taken as min(mine, theirs).
4. Congruence scaling uses rational $S\approx W_d^{-1/2}$. The result is rounded to $2^{-64}$, and the Frobenius bound on (ball radius + rounding + symmetrization), about $1.7\cdot10^{-17}$, is subtracted. **$-M\succ0$ is decided by all 2N leading principal minors $>0$, computed exactly** (FLINT `fmpz_mat.det`).
5. In Arb, for every cell: $\lambda_k+M_{{\rm late},k}\ge c_{{\rm loc},k}+c_g$, with $c_{\rm loc}$ built from the true sub-cell **sup** of the linear weights. Also checked: (i) absorption, (ii) $0\le\lambda_k\le\lambda_{\max}$, and $V_\lambda=h\sum\lambda_k\bar N_k^2$.
6. Moment term (`moment_check.py`): exact maximization over knapsack breakpoints in float, plus a rigorous Arb upper bound from piecewise LP duality.

**Results** (stored multipliers $\lambda$ of proof-tvc):

| instance | $\lVert M_{\rm mine}-M_{\rm theirs}\rVert_{\max}$ (scaled) | exact $-M\succ0$ | certified eigen-margin | worst remainder slack | $V_\lambda$ | moment (rigorous ≤) | $U_{\rm tot}\le$ | $G_w\ge$ | **certified margin** | $d_*$ |
|---|---|---|---|---|---|---|---|---|---|---|
| cone R0, N=120, $\rho=(1.5,100)$ | 1.2e-12 | **yes** | 2.9e-8 | 1.6e-5 | 6.267831935e-5 | 5.331e-8 | 6.273163e-5 | 7.269369e-5 | **9.962e-6 (13.70%)** | 9.63e-6 m |
| cone R0, N=60, $\rho=(1.5,15)$ | 1.5e-6 (Mlate only) | **yes** | 8e-11 | 3.1e-7 | 6.775854e-5 | 5.113e-8 | 6.780967e-5 | 7.269369e-5 | 4.884e-6 (6.72%) | 4.73e-6 m |
| box R0, N=60, $\rho=(1,15)$ | 1.2e-14 | **yes** | ≥ 0 | 3.0e-7 | 1.324690805e-4 | 3.908e-7 | 1.328599e-4 | 1.404383e-4 | **7.578e-6 (5.40%)** | 7.34e-6 m |
| cone R1, N=120, $\rho=(1,30)$, $\kappa_g=0.3$ (W2 repaired) | 3.2e-8 | **yes** | 5.4e-8 | 1.2e-5 | 6.975285485e-5 | 4.051e-8 | 6.979337e-5 | 7.269369e-5 | **2.900e-6 (3.99%)** | 2.81e-6 m |

- $d_*$ uses a float evaluation of the $d$-dependent moment term.
- proof-tvc's grid evaluation of the moment term is conservative: 5.73e-8 vs the exact 5.28e-8.

**Finding W2 (TVC-1R).**
- `certificate2.setup` evaluates the gyro weight $c(s)=\varepsilon\frac{J_a}{J_t}\bar\omega_3(s)/\cos\bar\varphi(s)$ at Gauss nodes, and the local $\bar\varphi$ there is not the sub-cell max. It then integrates $\int c\dot x^2$ by quadrature, which is exact only for polynomial weights. So `Vall` is not an upper bound.
- The certificate is so tight in this term that the conservative constant weight ($\bar\omega_3$ at the right end of each sub-cell) makes the same $\lambda$ fail: top eigenvalue $+1.05\cdot10^{-7}$, minor 147 negative.
- **Repair:** use the exact linear upper weight $\hat c(s)=\varepsilon\frac{J_a}{J_t}\frac{\tau_r}{J_a}\,s/\cos\bar\varphi_{\rm sub}$, with exact $\int s\,\dot X\dot X^\top$, $C_{g0}=\int\hat c$ and $C_{gw}=\int(s-s^*)^2\hat c$. The certificate then passes exactly with the stored $\lambda$.
- proof-tvc should adopt this in `certificate2.py` and `verify_cert.py`.

**Finding W3 (minor).** $c_{{\rm loc},k}$ takes the max of $\lvert c_A\rvert,\lvert c_B\rvert$ over interior Gauss nodes; the sup is at a sub-cell endpoint, a relative gap of about $10^{-4}$. The 2% factor on `lam_lb` in `solve_cert` absorbs this, and my sup-based check passes everywhere.

## 4. Sanity: what competitors actually achieve (`competitor_nlp.py`)

- Multistart NLP over **planar zero-lateral relaxed** competitors (cone, N=80, 8 starts, all converging to the same value): best gain $4.00\cdot10^{-5}$.
- So $\sup\in[4.00,\,6.27]\cdot10^{-5}<G_w=7.27\cdot10^{-5}$, consistent with the certificate.
- The spatial (two-component $h$) NLP was too slow to finish within the audit window.

## 5. Residual non-rigour and scope (honest list)

1. **Inputs taken from proof-tvc.**
   - The localized step functions $\bar\varphi,\bar v$ are computed in float. I validated them against an independent float implementation: all margins are positive, the smallest being $1.1\cdot10^{-8}$ rad in $\bar\varphi$, against float error of about $10^{-16}$.
   - Physical constants enter as their decimal values.
   - Neither is interval arithmetic. Both are dominated by many orders of magnitude.
2. $d_*$ (TVC-1q) and the glide-slope ratio 116 come from float/simulation evaluations, not intervals. The certified margins do not depend on them.
3. **Scope** (correctly stated in math/06, repeated here):
   - constant mass and constant $\varepsilon$ ($\alpha>0$ open);
   - unlimited gimbal rate (essential: see W1);
   - $\omega_3\equiv0$ for R0 competitors (R1 removes this);
   - axisymmetric $J$ with an on-axis pivot (GTPL's pivot offset (−0.02, −0.01) m and its products of inertia are ignored);
   - $t_f=1$ s only.
4. Not audited: §5.3 (rate limit), §5.4 (free $t_f$), §5.6 (long horizons, added during this audit), TVC-α.

## 6. Required text fixes in math/06 (for [proof-tvc])

- **§3 Remark, §4.8, PT6 last sentence:** replace "ordinary, bang-bang, no chattering" with the explicit chattering construction of §2 above, and cite the rigorous $G_w$. Also state that ordinary witnesses need sub-millisecond ±δ reversals, which (PT6) allows.
- **§3 table / TVC-1R:** the R1 certificate requires the exact linear gyro weight (W2). Also update the claim that the certificate was "re-verified by eigenvalue and Cholesky": that check was floating point. The exact check is in `numerics/verify-tvc/exact_cert.py`.
- **§6 item 5** ("a formal interval-arithmetic check of the SDP certificate"): now done for the matrix inequality and all scalar conditions, except the float-computed localization tables (item 1 above).

## 7. Reproduction

```
cd numerics/verify-tvc            # own venv: .venv (numpy, scipy, mpmath, python-flint, casadi)
../proof-tvc/.venv/bin/python dump_theirs.py 1.0 0.25 120 cone 0 1.5 100     # proof-tvc float matrix (for comparison only)
.venv/bin/python witness_check.py cone 8      # W1 + rigorous G_w + 6DOF sim   (also: box 8, cone 1)
.venv/bin/python loc_check.py cone            # localization (also: box, cone roll)
.venv/bin/python exact_cert.py 120 cone 0 1.5 100        # exact PSD + remainders  (60 box 0 1 15 ; 120 cone 1 1 30 3/10)
.venv/bin/python moment_check.py 120 cone 0 1.5 100      # moment term + FINAL margin + d*
.venv/bin/python disc_check.py 120 cone 0 1.5 100 2      # continuous form on refined space
.venv/bin/python competitor_nlp.py cone planar 8         # competitor lower bound
```
Outputs: `exact_*.out`, `exact_*.npy`, `moment_*.npy`, `witness_ordinary_*.npz`. Running times are under one minute each, except the NLP.
