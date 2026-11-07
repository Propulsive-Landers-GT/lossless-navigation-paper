#!/bin/zsh
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
cd /Users/aneesh/Documents/GitHub/GTPL/lcvx-5dof-research/numerics/verifier-sdp
../.venv/bin/python thr_csd3.py > results/thr_csd3.log 2>&1
../.venv/bin/python run_m.py > results/m_cert.log 2>&1
../.venv/bin/python run_ext.py altitude > results/ext_altitude.log 2>&1
../.venv/bin/python run_ext.py fuel > results/ext_fuel.log 2>&1
echo done > results/chain.done
