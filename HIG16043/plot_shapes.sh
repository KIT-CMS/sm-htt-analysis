#!/bin/bash

source utils/setup_cmssw.sh

if [[ " $@ " =~ " et " ]]; then
    ./plotting/plot_shapes.py \
        -i datacard_shapes_prefit.root \
        -f et_ztt_prefit et_0jet_prefit et_vbf_prefit et_boosted_prefit \
        --title "e#tau_{h}"

    ./plotting/plot_shapes.py \
        -i datacard_shapes_postfit_sb.root \
        -f et_ztt_postfit et_0jet_postfit et_vbf_postfit et_boosted_postfit \
        --title "e#tau_{h}"
fi

if [[ " $@ " =~ " mt " ]]; then
    ./plotting/plot_shapes.py \
        -i datacard_shapes_prefit.root \
        -f mt_ztt_prefit mt_0jet_prefit mt_vbf_prefit mt_boosted_prefit \
        --title "#mu#tau_{h}"

    ./plotting/plot_shapes.py \
        -i datacard_shapes_postfit_sb.root \
        -f mt_ztt_postfit mt_0jet_postfit mt_vbf_postfit mt_boosted_postfit \
        --title "#mu#tau_{h}"
fi

if [[ " $@ " =~ " tt " ]]; then
    ./plotting/plot_shapes.py \
        -i datacard_shapes_prefit.root \
        -f tt_ztt_prefit tt_0jet_prefit tt_vbf_prefit tt_boosted_prefit \
        --title "t t"

    ./plotting/plot_shapes.py \
        -i datacard_shapes_postfit_sb.root \
        -f tt_ztt_postfit tt_0jet_postfit tt_vbf_postfit tt_boosted_postfit \
        --title "t t"
fi
