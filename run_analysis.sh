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
./utils/clean.sh

# Parse arguments
ERA=$1               # options: 2016
CHANNELS=${@:2}      # options: et, mt, tt

# Create shapes of systematics
./shapes/produce_shapes.sh $ERA $CHANNELS

# Apply blinding strategy
#./shapes/apply_blinding.sh $ERA

# Convert shapes to synced format
./shapes/convert_to_synced_shapes.sh $ERA

# Write datacard
STXS_SIGNALS="stxs_stage0"  # options: stxs_stage0, stxs_stage1
CATEGORIES="stxs_stage1"    # options: stxs_stage0, stxs_stage1
STXS_FIT="inclusive"        # options: stxs_stage0, stxs_stage1, inclusive
JETFAKES=1                  # options: 0, 1
EMBEDDING=1                 # options: 0, 1
./datacards/produce_datacard.sh $ERA $STXS_SIGNALS $CATEGORIES $STXS_FIT $JETFAKES $EMBEDDING $CHANNELS

# Run statistical inference
#./combine/significance.sh $ERA | tee ${ERA}_significance.log
./combine/signal_strength.sh $ERA $STXS_FIT | tee ${ERA}_signal_strength_${STXS_FIT}.log
./combine/diff_nuisances.sh $ERA
#./combine/nuisance_impacts.sh $ERA

# Make prefit and postfit shapes
./combine/prefit_postfit_shapes.sh $ERA
./plotting/plot_shapes.sh $ERA $STXS_SIGNALS $CATEGORIES $JETFAKES $EMBEDDING $CHANNELS
./plotting/plot_signals.sh $ERA $STXS_SIGNALS $CATEGORIES $CHANNELS
