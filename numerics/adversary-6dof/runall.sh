#!/bin/bash
cd "$(dirname "$0")"
for args in "1.0 60 1 cone 0" "1.0 60 0 box 0" "1.0 60 1 box 1" "1.0 60 0 cone 1" "1.0 120 0 cone 0" "2.0 60 1 cone 1" "0.5 60 0 cone 0"; do
  n=$(echo $args | tr ' ' '_')
  .venv/bin/python exp1.py $args 2>&1 | grep -v -e WARNING -e "^$" > out_$n.txt &
done
wait
