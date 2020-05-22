#!/bin/bash

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh

ERA=$1
OUTPUTS=$2
CLASSIFICATION=""
[ ! -z $3 ] && CLASSIFICATION="--classification $3"
VARIABLES=gof/variables.yaml

for CHANNEL in et mt tt em
do
    ./gof/plot_gof.py $VARIABLES $OUTPUTS $CHANNEL $ERA $CLASSIFICATION
done
