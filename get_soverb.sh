#!/bin/bash

ERA=$1

source utils/setup_cvmfs_sft.sh
source utils/setup_samples.sh $ERA

# Produce shapes
python get_soverb.py \
    --directory $ARTUS_OUTPUTS \
    --et-friend-directory $ARTUS_FRIENDS_ET \
    --mt-friend-directory $ARTUS_FRIENDS_MT \
    --tt-friend-directory $ARTUS_FRIENDS_TT \
    --era $ERA \
    --num-threads 16 \
    --postfit-file combined_datacard_shapes_postfit_sb.root \
    --output-directory /ceph/swozniewski/SM_Htautau/ntuples/SoverSBfriends/${ERA}
