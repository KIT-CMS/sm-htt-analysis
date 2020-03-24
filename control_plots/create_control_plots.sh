#!/bin/bash

ERA=$1
CHANNEL=$2
VARIABLE=$3
WORKDIR=$4

pushd $WORKDIR

source utils/bashFunctionCollection.sh
ensureoutdirs

# Error handling to ensure that script is executed from top-level directory of
# this repository
for DIRECTORY in shapes datacards combine plotting utils gof
do
    if [ ! -d "$DIRECTORY" ]; then
        echo "[FATAL] Directory $DIRECTORY not found, you are not in the top-level directory of the analysis repository?"
        exit 1
    fi
done

NUM_THREADS=1
logandrun ./shapes/produce_shapes_variables.sh $ERA $CHANNEL $VARIABLE $NUM_THREADS

# Apply blinding strategy
logandrun ./shapes/apply_blinding.sh $ERA $CHANNEL ${VARIABLE}-control

# Convert to synced shapes
./shapes/convert_to_synced_shapes.sh $ERA $CHANNEL ${VARIABLE}-control

# Create datacard
JETFAKES=1
for EMBEDDING in 0 1
do
    ./control_plots/produce_datacard.sh $ERA $CHANNEL $VARIABLE $JETFAKES $EMBEDDING $VARIABLE-control

    # Create workspace
    logandrun ./control_plots/produce_workspace.sh $ERA $CHANNEL $VARIABLE | tee ${ERA}_produce_workspace_inclusive.log

    # Get the prefit shapes
    ./control_plots/prefit_postfit_shapes.sh $ERA $CHANNEL $VARIABLE

    # Plot the prefit shapes
    ./control_plots/plot_shapes.sh $ERA $CHANNEL $VARIABLE $JETFAKES $EMBEDDING
done

popd
