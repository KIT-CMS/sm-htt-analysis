#!/bin/bash

ERA=$1

source utils/setup_cmssw.sh

# Set stack size to unlimited, otherwise the T2W tool throws a segfault if
# combining all eras
ulimit -s unlimited

./combine/signal_strength.sh ${ERA} "robustHesse"

python combine/plot_poi_correlation.py fitDiagnostics${ERA}.root
