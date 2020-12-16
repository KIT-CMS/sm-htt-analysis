#!/bin/bash

# This script runs the nmssm analysis. The training of the neural network is performed using the condor cluster. If the GPU of the cluster is used is decided by the image used in ml_condor/wite_condor_submission.sh
# a. The training dataset is constructed from skimmed data
# b. The training on the cluster is started
# c. The trained modells are tested

ERA_NAME=$1 # Can be 2016, 2017, 2018 or "all"
CHANNEL=$2 # Can be et, mt or tt
MASS=$3 # only train on mH=500 GeV
BATCH=$4 # only train on mh' in 85, 90, 95, 100 GeV (see ml/get_nBatches.py for assignment)
RECALC=$5 # recalculate certain stages of the programm: "a" datasets, "b" training, "c" testing. Can be combined (ac)

#for MASS in 240 280 320 360 400 450 500 550 600 700 800 900 1000 1200 
#do
#for BATCH in `python ml/get_nBatches.py ${MASS}`
#do

SET=${ERA_NAME}_${CHANNEL}_${MASS}_${BATCH}
OUTPUT_PATH=output/ml/${SET}
CEPH_PATH=/ceph/srv/${USER}/nmssm_data/${SET}

# use the above loops if you want to train on multiple masses sequentially (this was done for the analysis to derive the 68 trainings)

echo "ERA=$ERA, CHANNEL=$CHANNEL, MASS=$MASS, BATCH=$BATCH, RECALC=$RECALC"

if [[ $ERA_NAME == "all_eras" ]]; then
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
if ( ( ${CEPH_TEST} || [[ ! -f ${OUTPUT_PATH}/dataset_config.yaml ]] ) && [[ -z ${RECALC} ]] ) || [[ ${RECALC} == *"a"* ]]; then
  # If there is no config file in the output directory or if dataset creation is specified:
  if [[ ! -f ${OUTPUT_PATH}/dataset_config.yaml ]] || [[ ${RECALC} == *"a"* ]]; then
    # Run dataset creation
    echo "creating Datasets"
    if [[ $ERA_NAME == "all_eras" ]]; then
      for ERA in "2016" "2017" "2018"; do
        ./ml/create_training_dataset.sh $ERA $CHANNEL $MASS $BATCH &
      done
      wait
      ./ml/combine_configs.sh $ERA_NAME $CHANNEL ${MASS}_${BATCH}
    else
      ./ml/create_training_dataset.sh $ERA_NAME $CHANNEL $MASS $BATCH
    fi
    # If dataset creation specified:
    if [[ ${RECALC} == *"a"* ]]; then
      # Remove data on ceph
      for ERA in ${ERAS}; do
        LOOP_CEPH_PATH=/ceph/srv/${USER}/nmssm_data/${ERA}_${CHANNEL}_${MASS}_${BATCH}
        rm ${LOOP_CEPH_PATH}/*
      done
    fi
  fi
  # Upload dataset to ceph
  for ERA in ${ERAS}; do
    LOOP_OUTPUT_PATH=output/ml/${ERA}_${CHANNEL}_${MASS}_${BATCH}
    LOOP_CEPH_PATH=/ceph/srv/tvoigtlaender/nmssm_data/${ERA}_${CHANNEL}_${MASS}_${BATCH}
    # create directories if needed
    if [[ ! -d ${LOOP_CEPH_PATH} ]]; then
      mkdir -p ${LOOP_CEPH_PATH}
    fi
    xrdcp ${LOOP_OUTPUT_PATH}/fold0_training_dataset.root ${LOOP_OUTPUT_PATH}/fold1_training_dataset.root ${LOOP_CEPH_PATH}
  done
else
  echo "No new datasets needed"
fi
#---b---
# If there are at least two model files (two are created by (b)) and no parts are specified or if training is specified:
if ( [[ $(ls -1 ${OUTPUT_PATH}/*.h5 2>/dev/null | wc -l ) -lt 2 ]] && [[ -z ${RECALC} ]] ) || [[ ${RECALC} == *"b"* ]]; then
  # Setup and run the training on condor 
  echo "training modells"
  ./ml_condor/setup_condor_training.sh $ERA_NAME $CHANNEL ${MASS}_${BATCH}
else
  echo "no new training needed"
fi

#---c---
# If there are not enough pictures (.png) in the output directory and no part is specified or if testing is specified:
if ( [[ $(ls -1 ${OUTPUT_PATH}/*.png 2>/dev/null | wc -l ) -lt 10 ]] && [[ -z ${RECALC} ]] ) || [[ ${RECALC} == *"c"* ]]; then
  # Export for testing and test modells
  echo "testing new models"
  ./ml/export_for_application.sh $ERA_NAME $CHANNEL ${MASS}_${BATCH}
  if [[ $ERA_NAME == "all_eras" ]]
  then
    for ERA in "2016" "2017" "2018"; do
      ./ml/run_testing_all_eras.sh $ERA $CHANNEL ${MASS}_${BATCH}
    done
  else
    ./ml/run_testing.sh $ERA_NAME $CHANNEL ${MASS}_${BATCH}
  fi
else
  echo "no new testing needed"
fi

#done
#done

# Use friend_tree_producer afterwards with lwtnn files to produce NNScore friend trees.
