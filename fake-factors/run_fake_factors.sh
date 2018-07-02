#!/bin/bash

ERA=$1

./fake-factors/produce_shapes.sh $ERA
./fake-factors/calculate_fake_factors.sh $ERA /storage/c/swozniewski/SM_Htautau/ntuples/Artus_2018-06-24/fake_factor_friends
