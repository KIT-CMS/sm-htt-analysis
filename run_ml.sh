#!/bin/bash

ERA=$1 # Can be 2016, 2017, 2018 or "all"
CHANNEL=$2 # Can be et, mt or tt
MASS=$3 # only train on mH=500 GeV
BATCH=$4 # only train on mh' in 85, 90, 95, 100 GeV (see ml/get_nBatches.py for assignment)


#for MASS in 240 280 320 360 400 450 500 550 600 700 800 900 1000 1200 
#do
#for BATCH in `python ml/get_nBatches.py ${MASS}`
#do

# use the above loops if you want to train on multiple masses sequentially (this was done for the analysis to derive the 68 trainings)

if [[ $ERA == *"all"* ]]; then
for ERA_2 in "2016" "2017" "2018"; do
./ml/create_training_dataset.sh $ERA_2 $CHANNEL $MASS $BATCH &
done
wait
./ml/combine_configs.sh all_eras $CHANNEL ${MASS}_${BATCH}
else
./ml/create_training_dataset.sh $ERA $CHANNEL $MASS $BATCH
fi

./ml/run_training.sh $ERA $CHANNEL ${MASS}_${BATCH}


./ml/export_for_application.sh $ERA $CHANNEL ${MASS}_${BATCH}

if [[ $ERA == *"all"* ]]
then
  for ERA_2 in "2016" "2017" "2018"; do
    ./ml/run_testing_all_eras.sh $ERA_2 $CHANNEL  ${MASS}_${BATCH}
  done
else
  ./ml/run_testing.sh $ERA $CHANNEL  ${MASS}_${BATCH}
fi

#done
#done

# Use friend_tree_producer afterwards with lwtnn files to produce NNScore friend trees.
