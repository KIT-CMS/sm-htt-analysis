#!/bin/bash
set -e
# Parse arguments
ERA=$1            
IFS=',' read -r -a CHANNELS <<< $2
CHANNELSARG=$2
TAG="default"
VARIABLE=$3
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

for CHANNEL in ${CHANNELS[@]}; do
    logandrun ./cutbased_shapes/convert_to_synced_shapes.sh $ERA $CHANNEL $VARIABLE &
done
wait

MorphingMSSMvsSM --era=${ERA} --auto_rebin=1 --binomial_bbb=1 --variable=${VARIABLE} --categories="2btag"

# Combine datacards
# The following line combines datacards of different eras.
# The era name "combined" is used for the resulting datacards and can be fitted using this
# as ERA variable in the following.
#./datacards/combine_datacards.sh 2016 2017

# Build workspace
STXS_FIT="inclusive"        # options: stxs_stage0, stxs_stage1p1, inclusive
logandrun ./datacards/produce_workspace.sh $ERA $STXS_FIT $TAG | tee ${ERA}_produce_workspace_${STXS_FIT}.log

# Run statistical inference
#./combine/significance.sh $ERA | tee ${ERA}_significance.log
logandrun ./combine/signal_strength.sh $ERA $STXS_FIT $DATACARDDIR/cmb/125 cmb ${TAG}
logandrun ./combine/signal_strength.sh $ERA $STXS_FIT $DATACARDDIR/cmb/125 cmb ${TAG} "robustHesse"
 ./combine/diff_nuisances.sh $ERA
#./combine/nuisance_impacts.sh $ERA

# Make prefit and postfit shapes

logandrun ./combine/prefit_postfit_shapes.sh ${ERA} ${STXS_FIT} ${DATACARDDIR}/cmb/125 ${TAG}
EMBEDDING=1
JETFAKES=1
logandrun ./plotting/plot_shapes.sh $ERA $TAG ${CHANNELSARG} $STXS_SIGNALS $STXS_FIT $CATEGORIES $JETFAKES $EMBEDDING

#./plotting/plot_signals.sh $ERA $STXS_SIGNALS $CATEGORIES $CHANNELS
