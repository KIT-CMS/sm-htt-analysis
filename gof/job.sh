#!/bin/bash

echo "### Begin of job"

ERA=$1
echo "Era:" $ERA

CHANNEL=$2
echo "Channel:" $CHANNEL

VARIABLE=$3
echo "Variable:" $VARIABLE

OUTPUT_DIR=/ceph/mburkart/jobs_gof_2017_2020-01-31/${ERA}_${CHANNEL}_${VARIABLE}
echo "Output directory:" $OUTPUT_DIR

BASE_PATH=/portal/ekpbms3/home/mburkart/workdir/postprocessing/sm-htt-analysis
echo "Base repository path:" $BASE_PATH

echo "Hostname:" `hostname`

echo "How am I?" `id`

echo "Where am I?" `pwd`

echo "### Start working"

rsync -a --exclude="*.root" --exclude="*.png" --exclude="*.pdf" --exclude="*.html" --exclude="*_plots" ${BASE_PATH}/ workspace
cd workspace

mkdir -p output/log
mkdir output/shapes

sed -i "s%CMSSW_10_2_16_UL%${BASE_PATH}/CMSSW_10_2_16_UL%g" utils/setup_cmssw.sh

# TODO: Source correct version of LCG stack on cluster
./gof/run_gof.sh $ERA $CHANNEL $VARIABLE

mkdir -p $OUTPUT_DIR
cp -r ${ERA}_plots/ gof*.* htt_${CHANNEL}_300*.* nuisances.html ${ERA}_shapes.root $OUTPUT_DIR

echo "### End of job"
