#!/bin/bash

ERA=$1
CHANNEL=$2

./ml/translate_models.sh $ERA $CHANNEL
./ml/export_lwtnn.sh $ERA $CHANNEL
