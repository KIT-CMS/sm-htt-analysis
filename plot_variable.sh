#!/bin/bash

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
CHANNELS=$1
VARIABLE=$2

./shapes/produce_shapes_variables.sh $CHANNELS $VARIABLE
./datacards/produce_datacard_variables.sh $CHANNELS $VARIABLE

#./combine/significance.sh | tee significance.log
#./combine/signal_strength.sh | tee signal_strength.log
#./combine/2D_signal_strength.sh | tee 2D_signal_strength.log
#./combine/diff_nuisances.sh
#./combine/nuisance_impacts.sh

# Make prefit and postfit shapes
./combine/prefit_shapes.sh
./plotting/plot_shapes_variables.sh $CHANNELS $VARIABLE
