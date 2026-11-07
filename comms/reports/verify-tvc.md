# Report: verify-tvc (audit of the pure-TVC computer-assisted proof, math/06)

**Verdict: CERTIFIED (exact arithmetic), subject to two repairs that were carried out and verified in this audit. No component is BROKEN.**

| Component | Verdict |
|---|---|
| Model reduction (CoP identity, Lemmas 2.1–2.4, relaxed ⊇ ordinary, rotation midpoint) | CERTIFIED |
| Witness | NEEDS FIX (W1), repaired: rigorous G_w = 7.269369e-5 (cone), 1.404383e-4 (box) |
| Majorants, remainders, S-procedure/Finsler, bathtub | CERTIFIED |
| Localization Lemma 4.0 (TVC-L) | CERTIFIED (independent re-implementation dominated on all cells) |
| Discretization Lemma 4.6′ | CERTIFIED (refined-space test: top eig −5.1e-6) |
| SDP inequality, exact | CERTIFIED: exact integer Sylvester minors on an independently assembled matrix |
| TVC-1R | NEEDS FIX (W2: gyro weight quadrature), repaired, CERTIFIED (3.99%) |

Certified margins: cone N=120 13.70% (U ≤ 6.27316e-5); box N=60 5.40%; R1 3.99%.

**W1.** The stored witness has |n| < K1 on all early cells, so it is a relaxed (chattering) control. The text claims "ordinary, no chattering". Flown literally, it gains only 3.5e-6. The fix is an explicit fast ±δ bang-bang with cell-moment matching.

**W2.** The R1 gyro weight must be an exact upper weight, not Gauss-node values.

Residual non-rigour: the localization tables and constants are float, checked independently. d* and the glide ratio are float.

Details: math/verify-tvc-report.md. Code: numerics/verify-tvc/.
