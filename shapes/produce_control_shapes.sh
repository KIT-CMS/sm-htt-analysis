#!/bin/bash
renice -n 19 -u `whoami`

BINNING=shapes/binning.yaml

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh
source utils/setup_samples_2017.sh

## Produce shapes
#python shapes/produce_control_shapes.py \
#    --directory $ARTUS_OUTPUTS \
#    --datasets $KAPPA_DATABASE \
#    --binning $BINNING \
#    --channels mt  \
#    --fake-factor-friend-directory /storage/b/akhmet/SM_Htautau/ntuples/Artus_2018-09-01/fake_factor_friends/ \
#    --num-threads 15

# Produce shapes
python shapes/produce_control_shapes.py \
    --directory $ARTUS_OUTPUTS \
    --datasets $KAPPA_DATABASE \
    --binning $BINNING \
    --channels et \
    --num-threads 18

## Produce shapes
#python shapes/produce_control_shapes.py \
#    --directory $ARTUS_OUTPUTS \
#    --datasets $KAPPA_DATABASE \
#    --binning $BINNING \
#    --channels tt \
#    --fake-factor-friend-directory /storage/b/akhmet/SM_Htautau/ntuples/Artus_2018-09-01/fake_factor_friends/ \
#    --num-threads 15
#    
## Produce shapes
#python shapes/produce_control_shapes.py \
#    --directory $ARTUS_OUTPUTS \
#    --datasets $KAPPA_DATABASE \
#    --binning $BINNING \
#    --channels em \
#    --num-threads 15
