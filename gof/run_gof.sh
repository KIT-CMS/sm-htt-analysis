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
NUM_THREADS=1
./gof/produce_shapes.sh $ERA $CHANNEL $VARIABLE $NUM_THREADS

# Apply blinding strategy
./shapes/apply_blinding.sh $ERA

# Convert shapes to synced format
./shapes/convert_to_synced_shapes.sh $ERA

# Create datacard
JETFAKES=1
EMBEDDING=1
./gof/produce_datacard.sh $ERA $CHANNEL $VARIABLE $JETFAKES $EMBEDDING

# Build workspace
./datacards/produce_workspace.sh $ERA "inclusive" | tee ${ERA}_produce_workspace_inclusive.log

# Run goodness of fit test
./gof/gof.sh $ERA

# Plot prefit shapes
./gof/prefit_postfit_shapes.sh $ERA
./gof/plot_shapes.sh $ERA $CHANNEL $VARIABLE $JETFAKES $EMBEDDING
