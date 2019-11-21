#!/bin/bash

ERA=$1
CHANNEL=$2

#./ml/create_training_dataset.sh $ERA $CHANNEL
#./ml/sum_training_weights.sh $ERA $CHANNEL

#for ERA_2 in "2016" "2017" "2018"; do
#  #./ml/create_training_dataset.sh $ERA_2 $CHANNEL
#  ./ml/sum_training_weights.sh $ERA_2 $CHANNEL
#done

./ml/run_training.sh $ERA $CHANNEL

if [[ $ERA == *"all"* ]]
then
  for ERA_2 in "2016" "2017" "2018"; do
    bash ml/run_testing_all_eras.sh $ERA_2 $CHANNEL
  done
else
  ./ml/run_testing.sh $ERA $CHANNEL
fi

./ml/export_for_application.sh $ERA $CHANNEL
./ml/run_application.sh $ERA $CHANNEL
 