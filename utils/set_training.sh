#!/bin/bash

sed -i -e "s/$1/$2/g" \
    shapes/produce_shapes.py \
    datacards/produce_datacard.py \
    plotting/plot_control.sh
