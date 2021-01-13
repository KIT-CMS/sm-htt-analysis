#!/bin/bash

# This script runs the nmssm analysis. The training of the neural network is performed using the condor cluster. If the GPU of the cluster is used is decided by the image used in ml_condor/wite_condor_submission.sh
#This script can be called by multi_run_ml.sh
# a. The training dataset is constructed from skimmed data
# b. The training on the cluster is started
# c. The trained modells are tested

ERA_NAME=$1 # Can be 2016, 2017, 2018 or "all"
CHANNEL=$2 # Can be et, mt or tt
MASS=$3 # only train on mH=500 GeV
BATCH=$4 # only train on mh' in 85, 90, 95, 100 GeV (see ml/get_nBatches.py for assignment)
OPTIONS=$5 # recalculate certain stages of the programm: "1" datasets, "2" training, "3" testing, "c" for using cpu instead of gpu. Can be combined (13, 2c3)

#for MASS in 240 280 320 360 400 450 500 550 600 700 800 900 1000 1200 
#do
#for BATCH in `python ml/get_nBatches.py ${MASS}`
#do

SET=${ERA_NAME}_${CHANNEL}_${MASS}_${BATCH}
OUTPUT_PATH=output/ml/${SET}
CEPH_PATH=/ceph/srv/${USER}/nmssm_data/${SET}

# use the above loops if you want to train on multiple masses sequentially (this was done for the analysis to derive the 68 trainings)

echo "ERA=${ERA}, CHANNEL=${CHANNEL}, MASS=${MASS}, BATCH=${BATCH}, OPTIONS=${OPTIONS}"

if [[ ${ERA_NAME} == "all_eras" ]]; then
  ERAS="2016 2017 2018"
else
  ERAS=${ERA_NAME}
fi

#---a---
# Create directories if needed
if [[ ! -d ${CEPH_PATH} ]]; then
  echo create ${CEPH_PATH}
  mkdir ${CEPH_PATH}
fi
if [[ ! -d output/log/logandrun ]]; then
  echo create output/log/logandrun
  mkdir -p output/log/logandrun
fi
#Test if needed trainings data is on ceph
CEPH_TEST=false
for ERA in ERAS; do
  LOOP_CEPH_PATH=/ceph/srv/${USER}/nmssm_data/${ERA}_${CHANNEL}_${MASS}_${BATCH}
  if [[ $(ls -1 ${LOOP_CEPH_PATH}/* 2>/dev/null | wc -l ) -lt 2 ]]; then
    CEPH_TEST=true
  fi
done
# If no datasets on ceph and no parts specified or if dataset creation specified: 
if ( ( ${CEPH_TEST} || [[ ! -f ${OUTPUT_PATH}/dataset_config.yaml ]] ) && [[ -z ${OPTIONS} ]] ) || [[ ${OPTIONS} == *"1"* ]]; then
  # Run dataset creation
  echo "creating Datasets"
  if [[ ${ERA_NAME} == "all_eras" ]]; then
    for ERA in "2016" "2017" "2018"; do
      ./ml/create_training_dataset.sh ${ERA} ${CHANNEL} ${MASS} ${BATCH} &
    done
    wait
    ./ml/combine_configs.sh ${ERA_NAME} ${CHANNEL} ${MASS}_${BATCH}
  else
    ./ml/create_training_dataset.sh ${ERA_NAME} ${CHANNEL} ${MASS} ${BATCH}
  fi
  # Remove data on ceph
  for ERA in ${ERAS}; do
    LOOP_CEPH_PATH=/ceph/srv/${USER}/nmssm_data/${ERA}_${CHANNEL}_${MASS}_${BATCH}
    rm ${LOOP_CEPH_PATH}/*
  done
  # Upload dataset to ceph
  for ERA in ${ERAS}; do
    LOOP_OUTPUT_PATH=output/ml/${ERA}_${CHANNEL}_${MASS}_${BATCH}
    LOOP_CEPH_PATH=/ceph/srv/tvoigtlaender/nmssm_data/${ERA}_${CHANNEL}_${MASS}_${BATCH}
    # create directories if needed
    if [[ ! -d ${LOOP_CEPH_PATH} ]]; then
      mkdir -p ${LOOP_CEPH_PATH}
    fi
    xrdcp ${LOOP_OUTPUT_PATH}/fold*.root ${LOOP_CEPH_PATH}
    rm -r ${LOOP_OUTPUT_PATH}/*.root
  done
else
  echo "No new datasets needed"
fi
#---b---
# If there are at least two model files (two are created by (b)) and no parts are specified or if training is specified:
if ( [[ $(ls -1 ${OUTPUT_PATH}/*.h5 2>/dev/null | wc -l ) -lt 2 ]] && [[ -z ${OPTIONS} ]] ) || [[ ${OPTIONS} == *"2"* ]]; then
  # Setup and run the training on condor 
  echo "training modells"
  if [[ ${OPTIONS} == *"2"* ]]; then
    force=true
  else
    force=false
  fi
  if [[ ${OPTIONS} == *"c"* ]]; then
    CALC=cpu
    echo "The training is using CPUs"
  else
    CALC=gpu
    echo "The training is using GPUs"
  fi
  ./ml_condor/setup_condor_training.sh ${ERA_NAME} ${CHANNEL} ${MASS}_${BATCH} ${force} ${CALC}
  grep Timestamp ${OUTPUT_PATH}/condor_logs_${CALC}/out.txt > ${OUTPUT_PATH}/condor_logs_${CALC}/times.txt
else
  echo "no new training needed"
fi

#---c---
# If there are not enough pictures (.png) in the output directory and no part is specified or if testing is specified:
if ( [[ $(ls -1 ${OUTPUT_PATH}/*.png 2>/dev/null | wc -l ) -lt 10 ]] && [[ -z ${OPTIONS} ]] ) || [[ ${OPTIONS} == *"3"* ]]; then
  # Export for testing and test modells
  echo "testing new models"
  for ERA in ${ERAS}; do
    LOOP_OUTPUT_PATH=output/ml/${ERA}_${CHANNEL}_${MASS}_${BATCH}
    LOOP_CEPH_PATH=/ceph/srv/tvoigtlaender/nmssm_data/${ERA}_${CHANNEL}_${MASS}_${BATCH}
    xrdcp ${LOOP_CEPH_PATH}/fold*.root ${LOOP_OUTPUT_PATH}
  done
  ./ml/export_for_application.sh ${ERA_NAME} ${CHANNEL} ${MASS}_${BATCH}
  if [[ ${ERA_NAME} == "all_eras" ]]
  then
    for ERA in "2016" "2017" "2018"; do
      ./ml/run_testing_all_eras.sh ${ERA} ${CHANNEL} ${MASS}_${BATCH}
    done
  else
    ./ml/run_testing.sh ${ERA_NAME} ${CHANNEL} ${MASS}_${BATCH}
  fi
  for ERA in ${ERAS}; do
    rm ${LOOP_OUTPUT_PATH}/fold*.root
  done
else
  echo "no new testing needed"
fi

#done
#done

# Use friend_tree_producer afterwards with lwtnn files to produce NNScore friend trees.
