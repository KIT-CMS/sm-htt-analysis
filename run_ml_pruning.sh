#!/bin/bash

ERA=$1
CHANNEL=$2
LOSS=$3
CLASS=$4

for i in {1..18}
do
   ./ml/run_pruning.sh $ERA $CHANNEL $CLASS
   ./ml/run_train_pruning.sh $ERA $CHANNEL $LOSS
   ./ml/run_test_pruning.sh $ERA $CHANNEL
done

./ml/run_plot_recall_precision.sh $ERA $CHANNEL
