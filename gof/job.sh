#!/bin/bash

set -e

echo "### Begin of job"

ERA=$1
echo "Era:" $ERA

CHANNEL=$2
echo "Channel:" $CHANNEL

VARIABLE=$3
echo "Variable:" $VARIABLE

OUTPUT_DIR=/ceph/wunsch/jobs_gof_${ERA}/${ERA}_${CHANNEL}_${VARIABLE}
echo "Output directory:" $OUTPUT_DIR

BASE_PATH=/portal/ekpbms2/home/wunsch/workspace/sm-htt-analysis
echo "Base repository path:" $BASE_PATH

echo "Hostname:" `hostname`

echo "How am I?" `id`

echo "Where am I?" `pwd`

echo "### Start working"

cp -r $BASE_PATH src
cd src

sed -i "s%CMSSW_7_4_7%${BASE_PATH}/CMSSW_7_4_7%g" utils/setup_cmssw.sh

./utils/clean.sh
./gof/run_gof.sh $ERA $CHANNEL $VARIABLE

mkdir -p $OUTPUT_DIR
cp -r plots/ gof.* $OUTPUT_DIR

echo "### End of job"
