#!/bin/bash

MODE=$1

if [[ $MODE == *"inclusive"* ]]
then
    rm -rf 2017_plots/ 2017_signal_strength_inclusive.log 2017_signal_strength_robustHesse.log 2017_workspace.root 2017_datacard_shapes_postfit_sb.root 2017_datacard_shapes_prefit.root
elif [[ $MODE == *"stage0"* ]]
then
    rm -rf 2017_plots/ 2017_signal_strength_stxs_stage0.log 2017_signal_strength_robustHesse.log 2017_workspace.root 2017_datacard_shapes_postfit_sb.root 2017_datacard_shapes_prefit.root
elif [[ $MODE == *"images"* ]]
then
    rm -rf *.pdf *.png *.yaml
else
    echo "Command not found"
fi