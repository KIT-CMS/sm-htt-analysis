#!/bin/bash

echo "### Begin of job"

CHANNEL=$1
echo "Channel:" $CHANNEL

VARIABLE=$2
echo "Variable:" $VARIABLE

OUTPUT_DIR=/storage/jbod/wunsch/jobs_gof/${CHANNEL}_${VARIABLE}
echo "Output directory:" $OUTPUT_DIR

BASE_PATH=/portal/ekpbms1/home/wunsch/sm-htt-analysis
echo "Base repository path:" $BASE_PATH

echo "Hostname:" `hostname`

echo "How am I?" `id`

echo "Where am I?" `pwd`

echo "### Start working"

cp -r $BASE_PATH src
cd src

sed -i "s%CMSSW_7_4_7%${BASE_PATH}/CMSSW_7_4_7%g" utils/setup_cmssw.sh

./utils/clean.sh
./gof/produce_shapes.sh $CHANNEL $VARIABLE
./gof/run_gof.sh $CHANNEL $VARIABLE

mkdir -p $OUTPUT_DIR
cp -r plots/ gof.* $OUTPUT_DIR

echo "### End of job"
