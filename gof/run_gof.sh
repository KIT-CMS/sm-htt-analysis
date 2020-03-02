#!/bin/bash

source utils/bashFunctionCollection.sh
ensureoutdirs

ERA=$1
CHANNEL=$2
VARIABLE=$3

# Error handling to ensure that script is executed from top-level directory of
# this repository
for DIRECTORY in shapes datacards combine plotting utils gof
do
    if [ ! -d "$DIRECTORY" ]; then
        echo "[FATAL] Directory $DIRECTORY not found, you are not in the top-level directory of the analysis repository?"
        exit 1
    fi
done

# Clean-up workspace
# ./utils/clean.sh

if [[ ! -d output/gof/${ERA}-${CHANNEL}-${VARIABLE} ]]
then
    mkdir output/gof/${ERA}-${CHANNEL}-${VARIABLE}
fi

# Produce shapes
NUM_THREADS=1
logandrun ./gof/produce_shapes.sh $ERA $CHANNEL $VARIABLE $NUM_THREADS

# Apply blinding strategy
./shapes/apply_blinding.sh $ERA $CHANNEL $VARIABLE

# Convert shapes to synced format
./shapes/convert_to_synced_shapes.sh $ERA $CHANNEL $VARIABLE

# Create datacard
JETFAKES=1
EMBEDDING=1
./gof/produce_datacard.sh $ERA $CHANNEL $VARIABLE $JETFAKES $EMBEDDING $VARIABLE

# Build workspace
logandrun ./gof/produce_workspace.sh $ERA $CHANNEL $VARIABLE

# Run goodness of fit test
logandrun ./gof/gof.sh $ERA $CHANNEL $VARIABLE

# Run fit in order to extract postfit shapes
./gof/run_fit.sh $ERA $CHANNEL $VARIABLE

# Plot prefit shapes
./gof/prefit_postfit_shapes.sh $ERA $CHANNEL $VARIABLE
./gof/plot_shapes.sh $ERA $CHANNEL $VARIABLE $JETFAKES $EMBEDDING
