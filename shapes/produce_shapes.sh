#!/bin/bash

ARTUS_OUTPUTS=$1
KAPPA_DATABASE=$2

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh

python shapes/produce_shapes.py --directory $ARTUS_OUTPUTS --datasets $KAPPA_DATABASE
