#!/bin/bash

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh

ERA=$1
OUTPUTS=$2
VARIABLES=gof/variables.yaml

for CHANNEL in et mt tt
do
    ./gof/plot_gof.py $VARIABLES $OUTPUTS $CHANNEL $ERA
done
