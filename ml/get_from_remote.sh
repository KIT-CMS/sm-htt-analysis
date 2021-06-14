#!/bin/bash

ERA=$1 # Can be 2016, 2017, 2018 or "all"
CHANNEL=$2 # Can be et, mt or tt
MASS=$3 # only train on mH=500 GeV
BATCH=$4 # only train on mh' in 85, 90, 95, 100 GeV (see ml/get_nBatches.py for assignment)
ALT_USER=$5
ALT_PATH=$6

if [[ ! -z ${ALT_USER} ]]; then
    USE_USER=${ALT_USER}
else
    USE_USER=${USER}
fi

if [[ ! -z ${ALT_PATH} ]]; then
    USE_PATH=${ALT_PATH}
else
    USE_PATH=for_condor
fi

#Check if script is run on HTCondor cluster or locally and set path to remote files accordingly
# echo ${_CONDOR_JOB_IWD}
if [[ ${_CONDOR_JOB_IWD} == "/var/lib/condor/execute/dir"* ]]; then
    echo "Running on HTCondor"
    cephpath=root://ceph-node-a.etp.kit.edu:1094//${USE_USER}/${USE_PATH}
else
    echo "Running locally"
    cephpath=/ceph/srv/${USE_USER}/${USE_PATH}
fi

#Fetch files depending on parameters
#When all_eras is set as era, the root files for the eras 2016, 2017, 2018 are fetched
folder=${ERA}_${CHANNEL}_${MASS}_${BATCH}
if [[ $ERA == "all_eras" ]]; then
    for _ERA in "2016" "2017" "2018"; do
        _folder=${_ERA}_${CHANNEL}_${MASS}_${BATCH}
        #Create directories if necessary
        if [[ ! -d output/ml/${_folder} ]]; then
            mkdir -p output/ml/${_folder}
        fi
        #Copy remote root files with xrootd
        xrdcp ${cephpath}/${_folder}/fold0_training_dataset.root ${cephpath}/${_folder}/fold1_training_dataset.root output/ml/${_folder}/
    done;
else
    #Create directory if necessary
    if [[ ! -d output/ml/${folder} ]]; then
        mkdir -p output/ml/${folder}
    fi
    #Copy remote root files with xrootd
    xrdcp ${cephpath}/${folder}/fold0_training_dataset.root ${cephpath}/${folder}/fold1_training_dataset.root output/ml/${folder}/
fi
#Create directory if necessary
if [[ ! -d output/ml/${folder} ]]; then
    mkdir -p output/ml/${folder}
fi
#Copy config file with xrootd
xrdcp ${cephpath}/${folder}/dataset_config.yaml output/ml/${folder}/

#(Optional) modify config files after copying it. Will not chenge them on remote source. The first \1 in the replacement is NOT part of the replacing value
# 's@\(early_stopping: \).*$@\120@g transforms' 'early_stopping: ???' into 'early_stopping: 20'
sed -e 's@\(early_stopping: \).*$@\130@g' -i output/ml/${folder}/dataset_config.yaml
# sed -e 's@\(epochs: \).*$@\1100000@g' -i output/ml/${folder}/dataset_config.yaml
sed -e 's@\(eventsPerClassAndBatch: \).*$@\1512@g' -i output/ml/${folder}/dataset_config.yaml
sed -e 's@\(name: \).*$@\1smhtt_dropout_tanh_large@g' -i output/ml/${folder}/dataset_config.yaml
# sed -e 's@\(save_best_only: \).*$@\1true@g' -i output/ml/${folder}/dataset_config.yaml
sed -e 's@\(steps_per_epoch: \).*$@\1128@g' -i output/ml/${folder}/dataset_config.yaml
