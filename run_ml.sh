#!/bin/bash

ERA=$1 # Can be 2016, 2017, 2018 or "all"
CHANNEL=$2 # Can be em, et, mt or tt
TAG=$3 # Additional tag for naming purposes. Can be left empty, in this case it will be "default"

./ml/create_training_dataset.sh $ERA $CHANNEL $TAG
./ml/run_training.sh $ERA $CHANNEL $TAG

if [[ $ERA == *"all"* ]]
then
  for ERA_2 in "2016" "2017" "2018"; do
    ./ml/run_testing_all_eras.sh $ERA_2 $CHANNEL $TAG
  done
else
  ./ml/run_testing.sh $ERA $CHANNEL $TAG
fi

./ml/export_for_application.sh $ERA $CHANNEL $TAG

# Use friend_tree_producer afterwards with lwtnn files to produce NNScore friend trees.
 