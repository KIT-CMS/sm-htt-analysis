#!/bin/bash
set -e
# Parse arguments
ERA=$1               # options: 2016, 2017
IFS=',' read -r -a CHANNELS <<< $2
CHANNELSARG=$2
METHOD="default"

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

# Clean-up workspace
#./utils/clean.sh


# Create shapes of systematics
#./shapes/produce_shapes.sh $ERA $CHANNELSARG $METHOD

# Apply blinding strategy
#./shapes/apply_blinding.sh $ERA

# Convert shapes to synced format
for CHANNEL in ${CHANNELS[@]}; do
    logandrun ./shapes/convert_to_synced_shapes.sh $ERA $CHANNEL $METHOD &
done
wait

# Write datacard
STXS_SIGNALS="stxs_stage0"  # options: stxs_stage0, stxs_stage1p1
CATEGORIES="stxs_stage1p1"    # options: stxs_stage0, stxs_stage1p1
JETFAKES=1                  # options: 0, 1
EMBEDDING=1                 # options: 0, 1
DATACARDDIR=output/datacards/${ERA}-${METHOD}-smhtt-ML/${STXS_SIGNALS}
[ -d $DATACARDDIR ] || mkdir -p $DATACARDDIR
./datacards/produce_datacard.sh ${ERA} $STXS_SIGNALS $CATEGORIES $JETFAKES $EMBEDDING ${METHOD} ${CHANNELSARG}

# Combine datacards
# The following line combines datacards of different eras.
# The era name "combined" is used for the resulting datacards and can be fitted using this
# as ERA variable in the following.
#./datacards/combine_datacards.sh 2016 2017

# Build workspace
STXS_FIT="inclusive"        # options: stxs_stage0, stxs_stage1p1, inclusive
./datacards/produce_workspace.sh $ERA $STXS_FIT $METHOD | tee ${ERA}_produce_workspace_${STXS_FIT}.log

# Run statistical inference
#./combine/significance.sh $ERA | tee ${ERA}_significance.log
./combine/signal_strength.sh $ERA $STXS_FIT $DATACARDDIR/cmb/125 cmb ${METHOD}
# ./combine/signal_strength.sh $ERA "robustHesse" $DATACARDDIR/cmb/125 cmb ${METHOD}
# ./combine/diff_nuisances.sh $ERA
#./combine/nuisance_impacts.sh $ERA

# Make prefit and postfit shapes

# ./combine/prefit_postfit_shapes.sh ${ERA} ${STXS_FIT} ${DATACARDDIR}/cmb/125 ${METHOD}

# PREFITFILE="${DATACARDDIR}/prefitshape-${era}-${METHOD}-${STXS_FIT}.root"
# PLOTDIR=output/plots/${era}-${METHOD}_prefit-plots
# [ -d $PLOTDIR ] || mkdir -p $PLOTDIR

# ./plotting/plot_shapes.py -i $PREFITFILE -o $PLOTDIR -c ${CHANNELS[@]} -e $era $OPTION --categories $CATEGORIES --fake-factor --embedding --normalize-by-bin-width -l --train-ff $TRAINFF --train-emb $TRAINEMB

#./plotting/plot_signals.sh $ERA $STXS_SIGNALS $CATEGORIES $CHANNELS
