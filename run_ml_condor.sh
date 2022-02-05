#!/bin/bash
# set -e

# This script runs the nmssm analysis using the HTCondor cluster.
# 1. The training dataset is constructed from skimmed data 
# 2. The training is performed
# 3. The trained modells are tested

ERA=$1 # Can be 2016, 2017, 2018 or all_eras
CHANNEL=$2 # Can be et, mt or tt
OPTIONS=$3

# Do all steps if none are specified
if [[ ! ${OPTIONS} =~ [1-3] ]]; then
  OPTIONS="${OPTIONS}123"
fi

# Set name of output directory and name of analysis. Standard is 68 trainings
ANALYSIS_NAME=final_test7
OUTPUT_PATH=output/ml/${ANALYSIS_NAME}

OUTDIR=${OUTPUT_PATH}/${ERA}_${CHANNEL}
CONDOR_OUTPUT=${OUTDIR}/condor_logs
CEPH_PATH=/ceph/srv/${USER}/${ANALYSIS_NAME}
CEPHDIR=${CEPH_PATH}/${ERA}_${CHANNEL}

shopt -s extglob
# Loop through all eras if all_eras is set
if [[ ${ERA} == "all_eras" ]]; then
  ERAS="2016 2017 2018"
else
  ERAS=${ERA}
fi

# Step 1: Create trainings datasets and move them to /ceph/srv
if [[ ${OPTIONS} == *"1"* ]]; then
  for ERA_ in ${ERAS}; do
    # Run job with ./ml/create_training_dataset.sh on HTCondor (will perform work in current directory)
    # Stdout and Stderr are streamed to ${CONDOR_OUTPUT}/dataset_creation_${ERA_}/
    custom_condor_scripts/custom_condor_run.sh "cd $(pwd)" "./ml/create_training_dataset.sh ${ERA_} ${CHANNEL} ${ANALYSIS_NAME}" \
      -s custom_condor_scripts/dataset_creation.jdl \
      -d ${CONDOR_OUTPUT}/dataset_creation_${ERA_}/ \
      -q -t &
  done
  wait
  # Modify dataset_config.yaml if all_eras is used
  if [[ ${ERA} == "all_eras" ]]; then
    ./ml/combine_configs.sh all_eras ${CHANNEL} ${ANALYSIS_NAME}
  fi
  for ERA_ in ${ERAS}; do
    OUTDIR_=${OUTPUT_PATH}/${ERA_}_${CHANNEL}
    CEPHDIR_=${CEPH_PATH}/${ERA_}_${CHANNEL}
    # Create directories if needed
    if [[ ! -d ${CEPHDIR_} ]]; then
      echo "create ${CEPHDIR_}"
      mkdir -p ${CEPHDIR_}
    fi
    # Copy relevant root files to /ceph/srv 
    echo "Copy ${OUTDIR_}/fold0_training_dataset.root and ${OUTDIR_}/fold1_training_dataset.root to ${CEPHDIR_}"
    xrdcp ${OUTDIR_}/fold0_training_dataset.root ${OUTDIR_}/fold1_training_dataset.root ${CEPHDIR_}/
    # Remove all root files from local directory
    rm ${OUTDIR_}/*.root
  done
  # Create directories if needed
  if [[ ! -d ${CEPHDIR} ]]; then
    echo "create ${CEPHDIR}"
    mkdir -p ${CEPHDIR}
  fi
  # Copy dataset_config.yaml to /ceph/srv 
  echo "Copy ${OUTDIR}/dataset_config.yaml to ${CEPHDIR}"
  xrdcp ${OUTDIR}/dataset_config.yaml ${CEPHDIR}/
  # Remove all root files from local directory
  rm ${OUTDIR}/dataset_config.yaml
else
  echo "No new datasets required."
fi

# Step 2: Perform training and export for application
if [[ ${OPTIONS} == *"2"* ]]; then
  # Run job with ./ml/run_training.sh and ./ml/export_for_application.sh on HTCondor (will NOT perform work in current directory)
  # Stdout and Stderr are streamed to ${CONDOR_OUTPUT}/NN_training/
  custom_condor_scripts/custom_condor_run.sh \
    "./ml/get_from_remote.sh ${ERA} ${CHANNEL} ${USER} ${ANALYSIS_NAME}" \
    "./ml/run_training.sh ${ERA} ${CHANNEL} ${ANALYSIS_NAME}" \
    "./ml/export_for_application.sh ${ERA} ${CHANNEL} ${ANALYSIS_NAME}" \
    -i ml/ htt-ml/ utils/ output/log/logandrun/ \
    -o "${OUTDIR}/"'*.h5' "${OUTDIR}/"'*.pickle' "${OUTDIR}/"'*.png' "${OUTDIR}/"'*.pdf' "${OUTDIR}/"'*.json' \
    -s custom_condor_scripts/NNtraining_testing.jdl \
    -d ${CONDOR_OUTPUT}/NN_training/ \
    -q -t
else
  echo "No training required."
fi

# Step 3: Perform testing
if [[ ${OPTIONS} == *"3"* ]]; then
  if [[ ${ERA} == "all_eras" ]]; then
    # Run job with ./ml/run_testing_all_eras.sh on HTCondor for all eras (will NOT perform work in current directory)
    # Stdout and Stderr are streamed to ${CONDOR_OUTPUT}/NN_testing_all_eras/
    custom_condor_scripts/custom_condor_run.sh \
      "./ml/get_from_remote.sh ${ERA} ${CHANNEL} ${USER} ${ANALYSIS_NAME}" \
      'for ERA_2 in 2016 2017 2018; do ./ml/run_testing_all_eras.sh ${ERA_2}'" ${CHANNEL} ${ANALYSIS_NAME}; done" \
      -i ml/ htt-ml/ utils/ output/log/logandrun/ ${OUTDIR}/*.h5 ${OUTDIR}/*.pickle \
      -o "${OUTDIR}/"'*.!(root)' \
      -s custom_condor_scripts/NNtraining_testing.jdl \
      -d ${CONDOR_OUTPUT}/NN_testing_all_eras/ \
      -q -t
  else
    # Run job with ./ml/run_testing.sh on HTCondor (will NOT perform work in current directory)
    # Stdout and Stderr are streamed to ${CONDOR_OUTPUT}/NN_testing/
    custom_condor_scripts/custom_condor_run.sh \
      "./ml/get_from_remote.sh ${ERA} ${CHANNEL} ${USER} ${ANALYSIS_NAME}" \
      "./ml/run_testing.sh ${ERA} ${CHANNEL} ${ANALYSIS_NAME}" \
      -i ml/ htt-ml/ utils/ output/log/logandrun/ ${OUTDIR}/*.h5 ${OUTDIR}/*.pickle \
      -o "${OUTDIR}/"'*.!(root)' \
      -s custom_condor_scripts/NNtraining_testing.jdl \
      -d ${CONDOR_OUTPUT}/NN_testing/ \
      -q -t
  fi
else
  echo "No testing required."
fi
shopt -u extglob
