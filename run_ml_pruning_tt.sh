#!/bin/bash

ERA=$1
LOSS=$2
CHANNEL="tt"

./ml/run_pruning.sh $ERA $CHANNEL ggh True

for i in {1..18}
do
   ./ml/run_pruning.sh $ERA $CHANNEL ggh False
   ./ml/run_train_pruning.sh $ERA $CHANNEL $LOSS
   ./ml/run_test_pruning.sh $ERA $CHANNEL
done

./ml/run_plot_recall_precision.sh $ERA $CHANNEL
./ml/run_pruning.sh $ERA $CHANNEL ggh True

for i in {1..18}
do
   ./ml/run_pruning.sh $ERA $CHANNEL qqh False
   ./ml/run_train_pruning.sh $ERA $CHANNEL $LOSS
   ./ml/run_test_pruning.sh $ERA $CHANNEL
done

./ml/run_plot_recall_precision.sh $ERA $CHANNEL
./ml/run_pruning.sh $ERA $CHANNEL qqh True

for i in {1..18}
do
   ./ml/run_pruning.sh $ERA $CHANNEL ztt False
   ./ml/run_train_pruning.sh $ERA $CHANNEL $LOSS
   ./ml/run_test_pruning.sh $ERA $CHANNEL
done

./ml/run_plot_recall_precision.sh $ERA $CHANNEL
./ml/run_pruning.sh $ERA $CHANNEL ztt True

for i in {1..18}
do
   ./ml/run_pruning.sh $ERA $CHANNEL noniso False
   ./ml/run_train_pruning.sh $ERA $CHANNEL $LOSS
   ./ml/run_test_pruning.sh $ERA $CHANNEL
done

./ml/run_plot_recall_precision.sh $ERA $CHANNEL
./ml/run_pruning.sh $ERA $CHANNEL noniso True

for i in {1..18}
do
   ./ml/run_pruning.sh $ERA $CHANNEL misc False
   ./ml/run_train_pruning.sh $ERA $CHANNEL $LOSS
   ./ml/run_test_pruning.sh $ERA $CHANNEL
done

./ml/run_plot_recall_precision.sh $ERA $CHANNEL

