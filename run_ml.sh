#!/bin/bash

ERA=$1 # Can be 2016, 2017, 2018 or "all"
CHANNEL=$2 # Can be em, et, mt or tt

for MASS in 240 280 320 360 400 450 500 550 600 700 800 900 1000 1200 1400 1600 1800 2000 2500 3000
do
for BATCH in `python ml/get_nBatches.py ${MASS}`
do

for ERA_2 in "2016" "2017" "2018"; do
./ml/create_training_dataset.sh $ERA_2 $CHANNEL $MASS $BATCH &
done
wait



./ml/combine_configs.sh all_eras $CHANNEL ${MASS}_${BATCH}

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

done
done

# Use friend_tree_producer afterwards with lwtnn files to produce NNScore friend trees.
 
