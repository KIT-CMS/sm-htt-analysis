#!/bin/bash
# Called by run_ml_condor.sh

#This script is used to run the training of the neural networks (tensorflow) of the nmssm analysis on the GPU of the condor-cluster
#1. It will be checked if there is already a training on the same dataset ongoing
#2. A matching submision file and jobfile are created
#3. The job is sent to the cluster and monitored for interruption/completion
#4. The results are copied to the proper directory

#---1---
ERA=$1 #2018
CHANNEL=$2 #tt
TAG=$3 #500_2
FORCE=$4
CALC=$5
OUTPUT_PATH=output/ml/${ERA}_${CHANNEL}_${TAG}
LOG_DIR=condor_logs_${CALC}
LOG_FILE=${OUTPUT_PATH}/${LOG_DIR}/log.txt
echo ${LOG_FILE}
#Check for other jobs on same dataset
# If there is a lockfile in the output and there is a logfile for the condor job in the output:
if [[ -f "${OUTPUT_PATH}/lockfile.txt" ]] && [[ -f "${LOG_FILE}" ]]; then
  OLD_JOB_ID=$(grep -o "000 ([0-9]*." ${LOG_FILE} | sed "s/000 (//;s/\.//")
  if [[ ${FORCE} == "True" ]]; then
    OVERWRITE=True
  else
     # Ask if the old condor job should be aborted
    echo "Script paused because of lockfile in ${OUTPUT_PATH}."
    echo "There is already a training running for ${ERA}_${CHANNEL}_${TAG} (${OLD_JOB_ID})."
    read -p "Are you sure you want to start a new training [y/n] " -n 1 -r
    echo ""
    # If yes:
    if [[ ${REPLY} =~ ^[Yy]$ ]]; then
      OVERWRITE=True
    else
      OVERWRITE=False
    fi
  fi
  if [[ ${OVERWRITE} == "True" ]]; then
    # Reset lockfile and remove old job from condor, then restart this script with the same parameters
    echo "Previous training will be overwritten"
    rm ${OUTPUT_PATH}/lockfile.txt
    echo "Removing old job from condor (${OLD_JOB_ID})"
    condor_rm ${OLD_JOB_ID}
  else
    # End this script
    echo "Abort new training job"
    exit 1
  fi
fi
  echo "This is the lock file for the dataset ${ERA}_${CHANNEL}_${TAG}.
It is used to allow only one training on the condor cluster at once.
If there is no training running on the cluster and this file still exists
the training was aborted during a previous run and the file should be deleted." > ${OUTPUT_PATH}/lockfile.txt

#remove possible remnants from previous trainings
if [ -f "condor_output" ]; then
  echo "removing all condor_output*"
  rm -r condor_output*
fi
#create condor_logs directory if needed
if [ ! -d "${OUTPUT_PATH}/${LOG_DIR}" ]; then
  mkdir -p ${OUTPUT_PATH}/${LOG_DIR}
fi
if [ -f "${OUTPUT_PATH}/${LOG_DIR}/log.txt" ]; then
  rm ${OUTPUT_PATH}/${LOG_DIR}/*.txt
fi
#build .tar from htt-ml and utils if it doesn"t exist
if [ ! -f "ml_condor/httml.tar.gz" ]; then
  tar --dereference -czf httml.tar.gz htt-ml utils
fi

#---2---
#write submission file
./ml_condor/write_condor_submission.sh ${ERA} ${CHANNEL} ${TAG} ${CALC}

#---3---
#start condor job
condor_submit ${OUTPUT_PATH}/submission.jdl
START_ID=$(grep -o "000 ([0-9]*." ${LOG_FILE} | sed "s/000 (//;s/\.//")
trap "condor_rm ${START_ID}; rm ${OUTPUT_PATH}/lockfile.txt; exit 1" INT

condor_working=true
job_waiting=true

#Check status of job during runtime
while ${condor_working}; do
  CURRENT_ID=$(grep -o "000 ([0-9]*." ${LOG_FILE} | sed "s/000 (//;s/\.//")
  if [[ ${START_ID} -ne ${CURRENT_ID} ]] || [[ ! -f ${LOG_FILE} ]] || grep "Job was aborted" ${LOG_FILE} | grep ${CURRENT_ID}; then
    #if another job ist started on same datatset this will abort this job
    echo "."
    echo "Condor job with parameters ${ERA}_${CHANNEL}_${TAG} (${START_ID}) or its logfile was changed/deleted during runtime"
    echo "Logfiles are in ${OUTPUT_PATH}/${LOG_DIR}/"
    exit 1
  elif grep -q "Job was held" ${LOG_FILE}; then
    echo "."
    echo "Condor job with parameters ${ERA}_${CHANNEL}_${TAG}_${CALC} (${START_ID}) was held"
    echo "Logfiles are in ${OUTPUT_PATH}/${LOG_DIR}/"
    exit 1
  elif grep -q "(return value 0)" ${LOG_FILE}; then
    echo "."
    echo "Condor job with parameters ${ERA}_${CHANNEL}_${TAG}_${CALC} (${START_ID}) was completed succesfully"
    condor_working=false
  elif grep -q "(return value 1)" ${LOG_FILE}; then
    echo "."
    echo "Condor job with parameters ${ERA}_${CHANNEL}_${TAG}_${CALC} (${START_ID}) encountered an error"
    condor_working=false
  else
    if grep -q "Job executing on host" ${LOG_FILE} && ${job_waiting}; then
      echo "."
      echo "The job with parameters ${ERA}_${CHANNEL}_${TAG}_${CALC} (${START_ID}) started execution"
      job_waiting=false
    else
      echo -n "."
    fi
    sleep 10
  fi
done
echo "Logfiles are in ${OUTPUT_PATH}/${LOG_DIR}/"
#---4---
#move results to matching directory
mv condor_output_${ERA}_${CHANNEL}_${TAG}/* ${OUTPUT_PATH}
rm -r condor_output_${ERA}_${CHANNEL}_${TAG}

#lift lock forjobs on same dataset
rm ${OUTPUT_PATH}/lockfile.txt
