#!/bin/bash

ERA=$1 # Can be 2016, 2017, 2018 or "all_eras"
CHANNEL=$2 # Can be et, mt or tt
MASS=$3 # only train on mH=500 GeV
BATCH=$4 # only train on mh' in 85, 90, 95, 100 GeV (see ml/get_nBatches.py for assignment)
cephpath=/ceph/srv/${USER}/nmssm_data
folder=${ERA}_${CHANNEL}_${MASS}_${BATCH}

# Create root files and config files
if [[ ${ERA} == *"all_eras"* ]]; then
    for ERA_2 in "2016" "2017" "2018"; do
        ./ml/create_training_dataset.sh ${ERA_2} ${CHANNEL} ${MASS} ${BATCH} &
    done
    wait
    ./ml/combine_configs.sh all_eras ${CHANNEL} ${MASS}_${BATCH}
else
    ./ml/create_training_dataset.sh ${ERA} ${CHANNEL} ${MASS} ${BATCH}
fi

# Copy to ceph
if [[ ${ERA} == *"all_eras"* ]]; then
    for ERA_2 in "2016" "2017" "2018"; do
        folder2=${folder2}
        if [[ ! -d ${cephpath}/${folder2} ]]; then
            mkdir -p ${cephpath}/${folder2}
        fi
        xrdcp output/ml/${folder2}/fold0_training_dataset.root output/ml/${folder2}/fold1_training_dataset.root output/ml/${folder2}/dataset_config.yaml ${cephpath}/${folder2}/
    done;
fi
if [[ ! -d ${cephpath}/${folder} ]]; then
    mkdir -p ${cephpath}/${folder}
fi
xrdcp output/ml/${folder}/fold0_training_dataset.root output/ml/${folder}/fold1_training_dataset.root output/ml/${folder}/dataset_config.yaml ${cephpath}/${folder}/
