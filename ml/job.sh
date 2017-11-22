#!/bin/bash

echo "### Begin of job"

CHANNEL=$1
echo "Channel:" $CHANNEL

MODIFIER=$2
echo "Modifier:" $MODIFIER

BASE_PATH=/portal/ekpbms1/home/wunsch/sm-htt-analysis-ml
echo "Base repository path:" $BASE_PATH

OUTPUT_PATH=/storage/c/wunsch/trainings
OUTPUT_DIR=${CHANNEL}_keras_qqH${MODIFIER}
echo "Output: ${OUTPUT_PATH}/${OUTPUT_DIR}"

echo "Hostname:" `hostname`

echo "How am I?" `id`

echo "Where am I?" `pwd`

echo "### Start working"

# Copy source files
cp -r $BASE_PATH src
cd src

# Clean-up and set correct CMSSW path
./utils/clean.sh
sed -i "s%CMSSW_7_4_7%${BASE_PATH}/CMSSW_7_4_7%g" utils/setup_cmssw.sh

# Training
sed -i "s%MODIFIER%${MODIFIER}%g" ml/${CHANNEL}_training_config.yaml
./ml/run_training.sh $CHANNEL
./ml/run_testing.sh $CHANNEL

# Application
sed -i "s%${CHANNEL}_keras%${OUTPUT_DIR}%g" ml/${CHANNEL}_keras_application_config.yaml
./ml/run_application.sh $CHANNEL

# Combine
sed -i "s%${CHANNEL}_keras%${OUTPUT_DIR}%g" utils/setup_samples.sh
./run_analysis $CHANNEL

# Publish results
./utils/publish_analysis.sh ${OUTPUT_PATH}/${OUTPUT_DIR}

echo "### End of job"
