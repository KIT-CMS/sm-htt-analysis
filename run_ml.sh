#!/bin/bash

ERA=$1
CHANNEL=$2
LOSS=$3

#./ml/create_training_dataset.sh $ERA $CHANNEL
#./ml/sum_training_weights.sh $ERA
./ml/run_training.sh $ERA $CHANNEL $LOSS
if [[ $LOSS == *"standard"* ]]
then
    ./ml/run_testing.sh $ERA $CHANNEL
elif [[ $LOSS == *"custom"* ]]
then
    ./ml/run_testing_custom_loss.sh $ERA $CHANNEL
else
    echo "Loss name not implemented, try standard or custom"
fi
./ml/export_for_application.sh $ERA $CHANNEL
#./ml/run_application.sh $ERA $CHANNEL
