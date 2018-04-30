#!/bin/bash

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
./utils/clean.sh

# Produce shapes
./gof/produce_shapes.sh $ERA $CHANNEL $VARIABLE

# Create datacard
./gof/produce_datacard.sh $ERA $CHANNEL $VARIABLE

# Run goodness of fit test
./gof/gof.sh $ERA

# Plot prefit and postfit shapes
./combine/signal_strength.sh $ERA
./combine/prefit_postfit_shapes.sh $ERA
./gof/plot_shapes.sh $ERA $CHANNEL $VARIABLE
