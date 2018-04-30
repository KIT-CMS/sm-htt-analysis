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

# Create shapes of systematics
ERA=$1
CHANNELS=${@:2}
./shapes/produce_shapes.sh $ERA $CHANNELS

# Apply blinding strategy
#./shapes/apply_blinding.sh

# Make control plots of produced shapes
#./plotting/plot_control.sh $CHANNELS

# Write datacard
./datacards/produce_datacard.sh $ERA $CHANNELS

# Run statistical inference
./combine/significance.sh | tee significance.log
./combine/signal_strength.sh | tee signal_strength.log
#./combine/2D_signal_strength.sh | tee 2D_signal_strength.log
./combine/diff_nuisances.sh
#./combine/nuisance_impacts.sh

# Make prefit and postfit shapes
./combine/prefit_postfit_shapes.sh
./plotting/plot_shapes.sh $ERA $CHANNELS
