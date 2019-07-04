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
ERA=$1
CHANNELS=${@:2}

#./QCD_extrap_measurement/produce_shapes.sh $ERA $CHANNELS

python shapes/convert_to_synced_shapes.py ${ERA} ${ERA}_shapes.root .

for CHANNEL in $CHANNELS; do
# Write datacard
STXS_SIGNALS=stxs_stage0
CATEGORIES=stxs_stage0
JETFAKES=false
EMBEDDING=true
./QCD_extrap_measurement/produce_datacard.sh $ERA $STXS_SIGNALS $CATEGORIES $JETFAKES $EMBEDDING $CHANNEL

./datacards/produce_workspace.sh ${ERA} inclusive

# Run statistical inference
./QCD_extrap_measurement/signal_strength.sh ${ERA}
#./QCD_extrap_measurement/diff_nuisances.sh ${ERA}
#./QCD_extrap_measurement/nuisance_impacts.sh ${ERA}

# Make prefit and postfit shapes
./QCD_extrap_measurement/prefit_postfit_shapes.sh ${ERA}
#./QCD_extrap_measurement/plot_shapes.sh $CHANNEL

python combine/print_fitresult.py fitDiagnostics${ERA}.root
done
