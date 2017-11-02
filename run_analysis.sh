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
ARTUS_OUTPUTS=/storage/jbod/wunsch/Run2Analysis_alex_classified2
KAPPA_DATABASE=/portal/ekpbms3/home/wunsch/CMSSW_7_4_7/src/Kappa/Skimming/data/datasets.json
./shapes/produce_shapes.sh $ARTUS_OUTPUTS $KAPPA_DATABASE

# Make control plots of produced shapes
./plotting/plot_control.sh

# Write datacard
./datacards/produce_datacard.sh $TRAINING

# Run statistical inference
./combine/significance.sh | tee significance.log
./combine/signal_strength.sh | tee signal_strength.log
./combine/nuisance_impacts.sh

# Make prefit and postfit shapes
./combine/prefit_postfit_shapes.sh
./plotting/plot_shapes.sh
