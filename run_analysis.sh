#!/bin/bash
set -e
# Parse arguments
ERA=$1               # options: 2016, 2017
IFS=',' read -r -a CHANNELS <<< $2
CHANNELSARG=$2
TAG="default"

source utils/bashFunctionCollection.sh

# Error handling to ensure that script is executed from top-level directory of
# this repository
for DIRECTORY in shapes datacards combine plotting utils
do
    if [ ! -d "$DIRECTORY" ]; then
        echo "[FATAL] Directory $DIRECTORY not found, you are not in the top-level directory of the analysis repository?"
        exit 1
    fi
done
ensureoutdirs
# Clean-up workspace
#./utils/clean.sh


# Create shapes of systematics
#./shapes/produce_shapes.sh $ERA $CHANNELSARG $TAG

# Apply blinding strategy
#./shapes/apply_blinding.sh $ERA

# Convert shapes to synced format
for CHANNEL in ${CHANNELS[@]}; do
    logandrun ./shapes/convert_to_synced_shapes.sh $ERA $CHANNEL $TAG &
done
wait

# Write datacard
STXS_SIGNALS="stxs_stage0"  # options: stxs_stage0, stxs_stage1p1
CATEGORIES="stxs_stage1p1"    # options: stxs_stage0, stxs_stage1p1
JETFAKES=1                  # options: 0, 1
EMBEDDING=1                 # options: 0, 1
DATACARDDIR=output/datacards/${ERA}-${TAG}-smhtt-ML/${STXS_SIGNALS}
[ -d $DATACARDDIR ] || mkdir -p $DATACARDDIR
./datacards/produce_datacard.sh ${ERA} $STXS_SIGNALS $CATEGORIES $JETFAKES $EMBEDDING ${TAG} ${CHANNELSARG}

# Combine datacards
# The following line combines datacards of different eras.
# The era name "combined" is used for the resulting datacards and can be fitted using this
# as ERA variable in the following.
#./datacards/combine_datacards.sh 2016 2017

# Build workspace
STXS_FIT="inclusive"        # options: stxs_stage0, stxs_stage1p1, inclusive
./datacards/produce_workspace.sh $ERA $STXS_FIT $TAG | tee ${ERA}_produce_workspace_${STXS_FIT}.log

# Run statistical inference
#./combine/significance.sh $ERA | tee ${ERA}_significance.log
#./combine/signal_strength.sh $ERA $STXS_FIT $DATACARDDIR/cmb/125 cmb ${TAG}
# ./combine/signal_strength.sh $ERA "robustHesse" $DATACARDDIR/cmb/125 cmb ${TAG}
# ./combine/diff_nuisances.sh $ERA
#./combine/nuisance_impacts.sh $ERA

# Make prefit and postfit shapes

./combine/prefit_postfit_shapes.sh ${ERA} ${STXS_FIT} ${DATACARDDIR}/cmb/125 ${TAG}
EMBEDDING=1
JETFAKES=1
./plotting/plot_shapes.sh $ERA $TAG ${CHANNELSARG} $STXS_SIGNALS $STXS_FIT $CATEGORIES $JETFAKES $EMBEDDING

#./plotting/plot_signals.sh $ERA $STXS_SIGNALS $CATEGORIES $CHANNELS
