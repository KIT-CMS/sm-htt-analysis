#!/bin/bash

source utils/setup_cmssw.sh
source utils/setup_python.sh

./plotting/plot_uncertainties.py -i datacard_shapes.root -u 'CMS_htt_dyShape' 'CMS_scale_j' -c $@
./plotting/plot_uncertainties.py -i datacard_shapes.root --png -u 'CMS_htt_dyShape' 'CMS_scale_j' -c $@
