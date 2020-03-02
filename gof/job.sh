#!/bin/bash

echo "### Begin of job"

ERA=$1
echo "Era:" $ERA

CHANNEL=$2
echo "Channel:" $CHANNEL

VARIABLE=$3
echo "Variable:" $VARIABLE

BASE_PATH=$4
echo "Base repository path:" $BASE_PATH

echo "Hostname:" `hostname`

echo "How am I?" `id`

echo "Where am I?" `pwd`

echo "### Start working"

pushd ${BASE_PATH}

source utils/bashFunctionCollection.sh
ensureoutdirs

# TODO: Source correct version of LCG stack on cluster
./gof/run_gof.sh $ERA $CHANNEL $VARIABLE

echo "### End of job"
