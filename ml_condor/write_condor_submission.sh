#!/bin/bash

#This script is used to write the submission and the job file for setup_training_gpu.sh
#1. The variables for the submission are defined
#2. The job file is written (necessary as the proper options for the training can't be given in the submission file)
# "In this file the differentiation between cpu and gpu is made. By changing the used image" 
# "to one with the non-gpu version of tensorflow (tensorflow==1.12.0) only cpu will be used"
# "Minor changes to the run_condor_training_gpu.sh file may be necessary to use the correct $PATH."
#3. The submission file is written to match the used datasets and the usage of GPU

ERA=$1
CHANNEL=$2
TAG=$3
OUTPUT_PATH=output/ml/${ERA}_${CHANNEL}_${TAG}

#---1---
JOB_EXECUTABLE=ml_condor/condor_job.sh
EXECUTABLE=run_condor_training_gpu.sh
SUBMISSION_FILE=${OUTPUT_PATH}/submission.jdl
OUTLOG_FILE=${OUTPUT_PATH}/condor_logs/out.txt
ERRLOG_FILE=${OUTPUT_PATH}/condor_logs/err.txt
LOG_FILE=${OUTPUT_PATH}/condor_logs/log.txt
NUM_GPUS=1
ACC_GROUP=cms.higgs
# This is where he used image is defined###
DOCKER_IMAGE=tvoigtlaender/slc7-cuda9.0-tfgpu
###########################################
TRANSFERED_FILES_IN="ml_condor/${EXECUTABLE}, httml.tar.gz, ${OUTPUT_PATH}/dataset_config.yaml"
TRANSFERED_FILES_OUT="condor_output_${ERA}_${CHANNEL}_${TAG}"

#---2---
# Create Job file with correcr dataset
echo "#!/bin/bash" > ${JOB_EXECUTABLE}
echo "#This script runs inside the cluster." >> ${JOB_EXECUTABLE}
echo "#Written by ml_condor/write_condor_submission.sh" >> ${JOB_EXECUTABLE}
echo "#Called by condor container as startup following job request from ml_condor/setup_condor_training.sh" >> ${JOB_EXECUTABLE}
echo "./${EXECUTABLE} ${ERA} ${CHANNEL} ${TAG} ${USER}" >> ${JOB_EXECUTABLE}


#---3---
# Submit description file for test program
# Follow instructions from https://wiki.ekp.kit.edu/bin/view/EkpMain/EKPCondorCluster
########################"
echo "#Written by ./ml_condor/write_condor_submission.sh" > ${SUBMISSION_FILE}
echo "Executable = ${JOB_EXECUTABLE}" >> ${SUBMISSION_FILE}
echo "Universe = docker" >> ${SUBMISSION_FILE}
# Set log path
echo "Output = ${OUTLOG_FILE}" >> ${SUBMISSION_FILE}
echo "Error = ${ERRLOG_FILE}" >> ${SUBMISSION_FILE}
echo "Log = ${LOG_FILE}" >> ${SUBMISSION_FILE}
# Set # of used GPU
echo "request_GPUs = ${NUM_GPUS}" >> ${SUBMISSION_FILE}
echo 'requirements = Cloudsite == "topas"' >> ${SUBMISSION_FILE}
# For the ETP queue specifically"
echo "+RemoteJob = True" >> ${SUBMISSION_FILE}
# Set maximum runtime
## 1 hour walltime"
echo "+RequestWalltime = 3600" >> ${SUBMISSION_FILE}
# Set # of used CPU
## single CPU"
echo "RequestCPUs = 1" >> ${SUBMISSION_FILE}
# Set amount os used RAM
## 4GB RAM"
echo "RequestMemory = 4000" >> ${SUBMISSION_FILE}
## select accounting group
### belle, ams, 
### cms.top, cms.higgs, cms.production, cms.jet" 
echo "accounting_group = ${ACC_GROUP}" >> ${SUBMISSION_FILE}
# Choose a GPU-appropriate image to run inside"
echo "docker_image = ${DOCKER_IMAGE}" >> ${SUBMISSION_FILE}
# Specifying files to transfer between submission and execution host"
echo "should_transfer_files = YES" >> ${SUBMISSION_FILE}
# Conda:"
echo "transfer_input_files = ${TRANSFERED_FILES_IN}" >> ${SUBMISSION_FILE}
# PIP:"
#The following line is used to install needed python modules that are not included in the image
#transfer_input_files = main.py,requirements.txt" >> ${SUBMISSION_FILE}
echo "transfer_output_files = ${TRANSFERED_FILES_OUT}" >> ${SUBMISSION_FILE}
#echo transfer_output_remaps could be used at this point to send the files to an output directory. 
#This was not done here as it is only possibke with individual files, not directories.
echo "Queue" >> ${SUBMISSION_FILE}
