#!/bin/bash

ERA=$1
CHANNEl=$2

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh

python check_hww/plot_2D_comparisons.py check_hww/${ERA}_${CHANNEl}/hww_vs_htt.root
