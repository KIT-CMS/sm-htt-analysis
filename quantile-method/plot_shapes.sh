#!/bin/bash

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh

mkdir -p plots
./quantile-method/plot_shapes.py -i impact_parameter_shapes.root --png -c $@
