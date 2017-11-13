#!/bin/bash

echo "### Begin of job"

CHANNEL=$1
echo "Channel:" $CHANNEL

VARIABLE=$2
echo "Variable:" $VARIABLE

OUTPUT_DIR=/storage/jbod/wunsch/jobs_gof/${CHANNEL}_${VARIABLE}
echo "Output directory:" $OUTPUT_DIR

echo "Hostname:" `hostname`

echo "How am I?" `id`

echo "Where am I?" `pwd`

echo "### Start working"

cp -r /portal/ekpbms3/home/wunsch/workspace/sm-htt-analysis src
cd src

./utils/clean.sh
./gof/produce_shapes.sh $CHANNEL $VARIABLE
./gof/run_gof.sh $CHANNEL $VARIABLE

mkdir -p $OUTPUT_DIR
cp -r plots/ gof.* $OUTPUT_DIR

echo "### End of job"
