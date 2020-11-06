#!/bin/bash

ERA=$1
CHANNEL=$2
TAG=$3


./ml/translate_models.sh $ERA $CHANNEL $TAG
./ml/export_lwtnn.sh $ERA $CHANNEL $TAG
