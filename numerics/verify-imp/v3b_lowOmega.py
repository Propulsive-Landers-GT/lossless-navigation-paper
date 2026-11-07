"""verify-imp: low-Omega end of the Theorem S certified range (math/07 §4 claims (0, Omega_max])."""
import numpy as np, importlib.util, sys, io, contextlib
spec = importlib.util.spec_from_file_location("v3", "v3_lemmaS_table.py")
with contextlib.redirect_stdout(io.StringIO()):
    v3 = importlib.util.module_from_spec(spec); spec.loader.exec_module(v3)
for dd in [2, 5, 7, 10, 12]:
    oms = np.concatenate([np.geomspace(1e-3, 0.05, 15), np.arange(0.05, 0.6, 0.01)])
    res = [(Om, *v3.case(dd, 2, Om / 2, verbose=False)) for Om in oms]
    cert = [Om for Om, M, reg in res if M > 0 and reg]
    print(f"delta={dd}: certified Omega from {min(cert) if cert else None:.4f} to {max(cert) if cert else None:.3f};"
          f" M at Omega=1e-3: {res[0][1]:.3e}")
