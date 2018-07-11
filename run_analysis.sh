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
ERA=$1
CHANNELS=${@:2}

# Create shapes of systematics
./shapes/produce_shapes.sh $ERA $CHANNELS

# Apply blinding strategy
#./shapes/apply_blinding.sh $ERA

# Write datacard
STXS_SIGNALS=0       # options: 0, 1
STXS_CATEGORIES=0    # options: 0, 1
STXS_FIT="inclusive" # options: inclusive, 0, 1
./datacards/produce_datacard.sh $ERA $STXS_SIGNALS $STXS_CATEGORIES $STXS_FIT $CHANNELS

# Run statistical inference
./combine/significance.sh $ERA | tee ${ERA}_significance.log
./combine/signal_strength.sh $ERA $STXS_FIT | tee ${ERA}_signal_strength.log
./combine/diff_nuisances.sh $ERA
#./combine/nuisance_impacts.sh $ERA

# Make prefit and postfit shapes
./combine/prefit_postfit_shapes.sh $ERA
./plotting/plot_shapes.sh $ERA $STXS_SIGNALS $STXS_CATEGORIES $CHANNELS
./plotting/plot_signals.sh $ERA $STXS_SIGNALS $STXS_CATEGORIES $CHANNELS
