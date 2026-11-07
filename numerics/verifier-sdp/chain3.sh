#!/bin/zsh
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
cd /Users/aneesh/Documents/GitHub/GTPL/lcvx-5dof-research/numerics/verifier-sdp
../.venv/bin/python glide_check.py > results/glide_check.log 2>&1
cd ../proof-csd2p
../.venv/bin/python index_check.py ../verifier-sdp/results/csd2p_16_24_32.jsonl,../verifier-sdp/results/bank_d0_conv.jsonl ../verifier-sdp/results/idx_full.jsonl 1000 > ../verifier-sdp/results/idx_full.log 2>&1
echo done > ../verifier-sdp/results/chain3.done
