#!/bin/bash

echo "### Begin of job"

SHAPES=/storage/jbod/wunsch/jobs_gof/shapes.root
echo "Shapes:" $SHAPES

CHANNEL=$2
echo "Channel:" $CHANNEL

VARIABLE=$3
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
./gof/run_gof.sh $SHAPES $CHANNEL $VARIABLE

mkdir -p $OUTPUT_DIR
cp -r plots/ gof.* $OUTPUT_DIR

echo "### End of job"
