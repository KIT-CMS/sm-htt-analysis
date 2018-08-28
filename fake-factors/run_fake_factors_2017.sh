#!/bin/bash

ERA=$1
CONFIGKEY=$2

./fake-factors/produce_shapes_2017.sh $ERA $CONFIGKEY
./fake-factors/calculate_fake_factors_2017.sh $ERA $CONFIGKEY
