#!/bin/bash

CHANNEL=$1
VARIABLE=$2

# Error handling to ensure that script is executed from top-level directory of
# this repository
for DIRECTORY in shapes datacards combine plotting utils gof
do
    if [ ! -d "$DIRECTORY" ]; then
        echo "[FATAL] Directory $DIRECTORY not found, you are not in the top-level directory of the analysis repository?"
        exit 1
    fi
done

# Produce shapes
./gof/produce_shapes.sh $CHANNEL $VARIABLE

# Create datacard
./gof/produce_datacard.sh $CHANNEL $VARIABLE

# Run goodness of fit test
./gof/gof.sh

# Plot prefit and postfit shapes
./combine/signal_strength.sh
./combine/prefit_postfit_shapes.sh
./gof/plot_shapes.sh $CHANNEL $VARIABLE
