#!/bin/bash

ERA=$1 # Can be 2016, 2017, 2018 or "all_eras"
CHANNEL=$2 # Can be et, mt or tt
MASS=$3 # only train on mH=500 GeV
BATCH=$4 # only train on mh' in 85, 90, 95, 100 GeV (see ml/get_nBatches.py for assignment)
GET_REMOTE=$5

if [[ ${GET_REMOTE} == *"GET_REMOTE"* ]]; then
    ./ml/get_from_remote.sh ${ERA} ${CHANNEL} ${MASS} ${BATCH}
else
    if [[ ${ERA} == *"all_eras"* ]]; then
        for ERA_2 in "2016" "2017" "2018"; do
            ./ml/create_training_dataset.sh ${ERA_2} ${CHANNEL} ${MASS} ${BATCH} &
        done
        wait
        ./ml/combine_configs.sh all_eras ${CHANNEL} ${MASS}_${BATCH}
    else
        ./ml/create_training_dataset.sh ${ERA} ${CHANNEL} ${MASS} ${BATCH}
    fi
fi

./ml/run_training.sh ${ERA} ${CHANNEL} ${MASS}_${BATCH}


./ml/export_for_application.sh ${ERA} ${CHANNEL} ${MASS}_${BATCH}

if [[ ${ERA} == *"all_eras"* ]]; then
    for ERA_2 in "2016" "2017" "2018"; do
        ./ml/run_testing_all_eras.sh ${ERA_2} ${CHANNEL} ${MASS}_${BATCH}
    done
else
    ./ml/run_testing.sh ${ERA} ${CHANNEL} ${MASS}_${BATCH}
fi

# Use friend_tree_producer afterwards with lwtnn files to produce NNScore friend trees.
