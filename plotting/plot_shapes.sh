#!/bin/bash
set -e

source utils/bashFunctionCollection.sh
source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh

ERA=$1
TAG=$2
IFS=',' read -r -a CHANNELS <<< $3
STXS_SIGNALS=$4
STXS_FIT=$5
CATEGORIES=$6
JETFAKES=$7
EMBEDDING=$8

TRAINFF=True
TRAINEMB=True
if [[ $STXS_SIGNALS != "stxs_stage0" ]]
then
    echo "[ERROR] Plotting for STXS stage 1 signals is not yet implemented."
    exit 1
fi

EMBEDDING_ARG=""
if [ $EMBEDDING == 1 ]
then
    EMBEDDING_ARG="--embedding"
fi

JETFAKES_ARG=""
if [ $JETFAKES == 1 ]
then
    JETFAKES_ARG="--fake-factor"
fi

for channel in ${CHANNELS[@]}; do
    DATACARDDIR=output/datacards/${ERA}-${TAG}-smhtt-ML/${STXS_SIGNALS}/${channel}/125

    PLOTDIR=output/plots/${ERA}-${TAG}_prefit-plots
    [ -d $PLOTDIR ] || mkdir -p $PLOTDIR

    for FILE in "${DATACARDDIR}/postfitshape-${ERA}-${TAG}-${STXS_FIT}.root"  "${DATACARDDIR}/prefitshape-${ERA}-${TAG}-${STXS_FIT}.root"
    do
        [[ -f $FILE ]] || ( logerror $FILE not found && exit 2 )
        for OPTION in "" "--png"
        do
            logandrun ./plotting/plot_shapes.py -i $FILE -o $PLOTDIR -c $channel -e $ERA $OPTION --categories $CATEGORIES --fake-factor --embedding --normalize-by-bin-width -l --train-ff $TRAINFF --train-emb $TRAINEMB
        done
    done
done