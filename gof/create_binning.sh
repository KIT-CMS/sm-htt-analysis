#!/bin/bash

ERA=$1
BINNING=gof/${ERA}_binning.yaml
[[ ! -z $2 ]] && BINNING=$2

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh
source utils/setup_samples.sh $ERA

# Calculate binning from data distributions if file is not existent
for CHANNEL in em mt et tt
do
    python gof/calculate_binning.py \
        --era $ERA \
        --directory $ARTUS_OUTPUTS \
        --em-friend-directories $ARTUS_FRIENDS_EM \
        --et-friend-directories $ARTUS_FRIENDS_ET \
        --mt-friend-directories $ARTUS_FRIENDS_MT \
        --tt-friend-directories $ARTUS_FRIENDS_TT \
        --datasets $KAPPA_DATABASE \
        --output $BINNING \
        --variables gof/variables.yaml \
        --channel $CHANNEL
    mv $BINNING ${BINNING/.yaml/_${CHANNEL}.yaml}
done

head -1 ${BINNING/.yaml/_em.yaml} > $BINNING
tail -n +2 -q ${BINNING/.yaml/_em.yaml} ${BINNING/.yaml/_et.yaml} ${BINNING/.yaml/_mt.yaml} ${BINNING/.yaml/_tt.yaml} >> $BINNING
