#!/bin/bash

source utils/setup_cmssw.sh

./plotting/plot_shapes.py -i datacard_shapes_prefit.root -f mt_ZTT_prefit mt_ZLL_prefit mt_QCD_prefit mt_W_prefit mt_TT_prefit mt_HTT_prefit

./plotting/plot_shapes.py -i datacard_shapes_postfit_sb.root -f mt_ZTT_postfit mt_ZLL_postfit mt_QCD_postfit mt_W_postfit mt_TT_postfit mt_HTT_postfit
