#!/bin/bash

ERA=$1 # Can be 2016, 2017, 2018 or "all"
CHANNEL=$2 # Can be et, mt or tt
MASS=$3 # only train on mH=500 GeV
BATCH=$4 # only train on mh' in 85, 90, 95, 100 GeV (see ml/get_nBatches.py for assignment)

if [[ $ERA == *"all"* ]]; then
for ERA_2 in "all_eras" "2016" "2017" "2018"; do
if [[ ! -d output/ml/${ERA_2}_${CHANNEL}_${MASS}_${BATCH} ]]; then
mkdir output
mkdir output/ml
mkdir output/ml/${ERA_2}_${CHANNEL}_${MASS}_${BATCH}
fi
xrdcp /ceph/srv/tvoigtlaender/nmssm_data/${ERA_2}_${CHANNEL}_${MASS}_${BATCH}/* output/ml/${ERA_2}_${CHANNEL}_${MASS}_${BATCH}/
done;
wait
else
if [[ ! -d output/ml/${ERA}_${CHANNEL}_${MASS}_${BATCH} ]]; then
mkdir output
mkdir output/ml
mkdir output/ml/${ERA}_${CHANNEL}_${MASS}_${BATCH}
fi
xrdcp /ceph/srv/tvoigtlaender/nmssm_data/${ERA}_${CHANNEL}_${MASS}_${BATCH}/* output/ml/${ERA}_${CHANNEL}_${MASS}_${BATCH}/
fi