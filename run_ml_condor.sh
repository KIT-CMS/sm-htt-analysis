#!/bin/bash
set -e

# This script runs the nmssm analysis. The training of the neural network is performed using the condor cluster. 
# If the GPU of the cluster is used is decided by the image used in ml_condor/wite_condor_submission.sh
# This script can be called by multi_run_ml.sh
# 1. The training dataset is constructed from skimmed data
# 2. The training on the cluster is started
# 3. The trained modells are tested

ERA_NAME=$1 # Can be 2016, 2017, 2018 or "all"
CHANNEL=$2 # Can be et, mt or tt
MASS=$3 # only train on mH=500 GeV
BATCH=$4 # only train on mh' in 85, 90, 95, 100 GeV (see ml/get_nBatches.py for assignment)
OPTIONS=$5 # recalculate certain stages of the programm: "1" datasets, "2" training, "3" testing,
# "c" for using cpu instead of gpu, "f" to run training on cluster even if training on same data is already running. 
#Can be combined (13, 2c3). No option is equivalent to "123" (but not "123c")

SET=${ERA_NAME}_${CHANNEL}_${MASS}_${BATCH}
OUTPUT_PATH=output/ml/${SET}
CEPH_PATH=/ceph/srv/${USER}/nmssm_data/${SET}

echo "ERA=${ERA}, CHANNEL=${CHANNEL}, MASS=${MASS}, BATCH=${BATCH}, OPTIONS=${OPTIONS}"

if [[ ${ERA_NAME} == "all_eras" ]]; then
  ERAS="2016 2017 2018"
else
  ERAS=${ERA_NAME}
fi

#---1---
# Create directories if needed
if [[ ! -d ${CEPH_PATH} ]]; then
  echo create ${CEPH_PATH}
  mkdir ${CEPH_PATH}
fi
if [[ ! -d output/log/logandrun ]]; then
  echo create output/log/logandrun
  mkdir -p output/log/logandrun
fi

# If dataset creation specified: 
if [[ -z ${OPTIONS} ]] || [[ ${OPTIONS} == *"1"* ]]; then
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
#---2---
# If training is specified:
if [[ -z ${OPTIONS} ]] || [[ ${OPTIONS} == *"2"* ]]; then
  # Setup and run the training on condor 
  echo "training modells"
  if [[ ${OPTIONS} == *"c"* ]]; then
    CALC=cpu
    echo "The training is using CPUs"
  else
    CALC=gpu
    echo "The training is using GPUs"
  fi
  if [[ ${OPTIONS} == *"f"* ]]; then
    FORCE=True
  else
    FORCE=False
  fi
  ./ml_condor/setup_condor_training.sh ${ERA_NAME} ${CHANNEL} ${MASS}_${BATCH} ${FORCE} ${CALC}
  grep Timestamp ${OUTPUT_PATH}/condor_logs_${CALC}/out.txt > ${OUTPUT_PATH}/condor_logs_${CALC}/times.txt
else
  echo "no new training needed"
fi

#---3---
# If testing is specified:
if [[ -z ${OPTIONS} ]] || [[ ${OPTIONS} == *"3"* ]]; then
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
