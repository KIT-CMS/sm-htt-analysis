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
OUTPUT_PATH=output/ml/${ERA}_${CHANNEL}_${TAG} 
LOG_FILE=${OUTPUT_PATH}/condor_logs/log.txt 

#Check for other jobs on same dataset
# If there is a lockfile in the output and there is a logfile for the condor job in the output:
if [ -f "${OUTPUT_PATH}/lockfile.txt" ] && [ -f "${LOG_FILE}" ]; then
  # Ask if the old condor job should be aborted
  OLD_JOB_ID=$(cat ${LOG_FILE} | grep -o '000 ([0-9]*.' | sed 's/000 (//;s/\.//')
  echo "Script paused because of lockfile in ${OUTPUT_PATH}."
  echo "There is already a training running for ${ERA}_${CHANNEL}_${TAG} (${OLD_JOB_ID})."
  read -p "Are you sure you want to start a new training [y/n] " -n 1 -r
  echo ""
  # If yes:
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Reset lockfile and remove old job from condor, then restart this script with the same parameters
    echo "Previous training will be overwritten"
    rm ${OUTPUT_PATH}/lockfile.txt
    echo "Removing old job from condor (${OLD_JOB_ID})"
    condor_rm ${OLD_JOB_ID}
    ./ml_condor/setup_condor_training.sh ${ERA} ${CHANNEL} ${TAG}
  else
    echo "Abort new training job"
  fi
  # End this script
  exit 0
else
  echo "This is the lock file for the dataset ${ERA}_${CHANNEL}_${TAG}.
It is used to allow only one training on the condor cluster at once.
If there is no training running on the cluster and this file still exists
the training was aborted during a previous run and the file should be deleted." > ${OUTPUT_PATH}/lockfile.txt
fi

#remove possible remnants from previous trainings
if [ -f "condor_output" ]; then
  rm -r condor_output*
fi
#create condor_logs directory if needed
if [ ! -d "${OUTPUT_PATH}/condor_logs" ]; then
  mkdir ${OUTPUT_PATH}/condor_logs
fi
if [ -f "${OUTPUT_PATH}/condor_logs/log.txt" ]; then
  rm ${OUTPUT_PATH}/condor_logs/*.txt
fi
#build .tar from htt-ml and utils if it doesn't exist
if [ ! -f "ml_condor/httml.tar.gz" ]; then
  tar --dereference -czf httml.tar.gz htt-ml utils
fi

#---2---
#write submission file
./ml_condor/write_condor_submission.sh ${ERA} ${CHANNEL} ${TAG}

#---3---
#start condor job
condor_submit ${OUTPUT_PATH}/submission.jdl


START_ID=$(cat ${LOG_FILE} | grep -o '000 ([0-9]*.' | sed 's/000 (//;s/\.//')
condor_working=true
job_waiting=true

#Check status of job during runtime
while ${condor_working}; do
  CURRENT_ID=$(cat ${LOG_FILE} | grep -o '000 ([0-9]*.' | sed 's/000 (//;s/\.//')
  if [ ${START_ID} -ne ${CURRENT_ID} ] || [ ! -f "${LOG_FILE}" ]; then
    #if another job ist started on same datatset this will abort this job
    echo "."
    echo "Condor job (${START_ID}) or logfile was changed/deleted during runtime"
    exit 1
  elif cat ${LOG_FILE} | grep -q "Job was held"; then
    echo "."
    echo "Condor job was held"
    condor_working=false
  elif cat ${LOG_FILE} | grep -q "(return value 0)"; then
    echo "."
    echo "Condor job was completed succesfully"
    condor_working=false
  elif cat ${LOG_FILE} | grep -q "(return value 1)"; then
    echo "."
    echo "Condor job encountered an error. Logfiles are in ${OUTPUT_PATH}/condor_logs/"
    condor_working=false
  else 
    if cat ${LOG_FILE} |grep -q "Job executing on host" && ${job_waiting}; then
      echo "."
      echo "The job started execution"
      job_waiting=false
    else 
      echo -n "."
    fi
    sleep 5
  fi
done

#---4---
#move results to matching directory
mv condor_output_${ERA}_${CHANNEL}_${TAG}/* ${OUTPUT_PATH}
rm -r condor_output_${ERA}_${CHANNEL}_${TAG}

#lift lock forjobs on same dataset
rm ${OUTPUT_PATH}/lockfile.txt
