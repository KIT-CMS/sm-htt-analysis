#!/bin/bash

source utils/setup_cmssw.sh
source utils/setup_python.sh

mkdir -p plots
./HIG16043/plot_shapes.py -i datacard_shapes_prefit.root -c $@ --x-label "Unrolled distribution"
