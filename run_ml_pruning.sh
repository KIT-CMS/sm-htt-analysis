#!/bin/bash

ERA=$1
CHANNEL=$2

for i in {1..18}
do
   ./ml/run_training.sh $ERA $CHANNEL
   ./ml/run_testing.sh $ERA $CHANNEL
done
