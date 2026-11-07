#!/bin/zsh
# [verifier-sdp] sequential queue (one heavy process at a time in this chain)
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
cd /Users/aneesh/Documents/GitHub/GTPL/lcvx-5dof-research/numerics/verifier-sdp
while pgrep -f "run_fixed.py reduced" >/dev/null; do sleep 15; done
../.venv/bin/python run_ext.py throttle > results/ext_throttle.log 2>&1
../.venv/bin/python run_m.py > results/m_cert.log 2>&1
../.venv/bin/python run_ext.py altitude > results/ext_altitude.log 2>&1
../.venv/bin/python run_ext.py fuel > results/ext_fuel.log 2>&1
echo QUEUE-DONE > results/queue.done
