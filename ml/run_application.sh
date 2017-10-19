#!/bin/bash

CHANNEL=$1

python ml/write_application_filelist.py \
    --directory /storage/jbod/wunsch/htt_2017-06-21_eleScale_classified \
    --database /portal/ekpbms3/home/wunsch/CMSSW_7_4_7/src/Kappa/Skimming/data/datasets.json \
    --channel ${CHANNEL} \
    --output ml/${CHANNEL}/application_filelist.yaml
