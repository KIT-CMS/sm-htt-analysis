#!/bin/bash

source utils/setup_cmssw.sh

# et
./plotting/plot_shapes.py -i datacard_shapes_prefit.root -f et_ZTT_prefit et_ZLL_prefit et_QCD_prefit et_W_prefit et_TT_prefit et_HTT_prefit --title "e#tau_{h}"

./plotting/plot_shapes.py -i datacard_shapes_postfit_sb.root -f et_ZTT_postfit et_ZLL_postfit et_QCD_postfit et_W_postfit et_TT_postfit et_HTT_postfit --title "e#tau_{h}"

# mt
./plotting/plot_shapes.py -i datacard_shapes_prefit.root -f mt_ZTT_prefit mt_ZLL_prefit mt_QCD_prefit mt_W_prefit mt_TT_prefit mt_HTT_prefit --title "#mu#tau_{h}"

./plotting/plot_shapes.py -i datacard_shapes_postfit_sb.root -f mt_ZTT_postfit mt_ZLL_postfit mt_QCD_postfit mt_W_postfit mt_TT_postfit mt_HTT_postfit --title "mu#tau_{h}"
