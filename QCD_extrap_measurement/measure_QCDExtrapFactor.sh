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
CHANNELS=$@
./QCD_extrap_measurement/produce_shapes.sh $CHANNELS

for CHANNEL in $CHANNELS; do
# Write datacard
./QCD_extrap_measurement/produce_datacard.sh $CHANNEL

# Run statistical inference
./QCD_extrap_measurement/signal_strength.sh | tee QCD_extrap_measurement/signal_strength.log
#./combine/diff_nuisances.sh
#./combine/nuisance_impacts.sh

# Make prefit and postfit shapes
./QCD_extrap_measurement/prefit_postfit_shapes.sh
./QCD_extrap_measurement/plot_shapes.sh $CHANNEL
done
