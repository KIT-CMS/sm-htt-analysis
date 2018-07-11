#!/bin/bash
set -e
# Error handling to ensure that script is executed from top-level directory of
# this repository
for DIRECTORY in shapes datacards combine plotting utils
do
    if [ ! -d "$DIRECTORY" ]; then
        echo "[FATAL] Directory $DIRECTORY not found, you are not in the top-level directory of the analysis repository?"
        exit 1
    fi
done

# Clean-up workspace
#./utils/clean.sh

# Create shapes of systematics
ERA=$1
CHANNELS=$2
VARIABLE=$3

./shapes/produce_shapes_variables_nominal.sh $ERA $CHANNELS $VARIABLE
./Dumbledraw/plot_variable.sh $ERA $CHANNELS $VARIABLE
