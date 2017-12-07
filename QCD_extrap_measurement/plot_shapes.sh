#!/bin/bash

source utils/setup_cmssw.sh

if [[ " $@ " =~ " et " ]]; then
    ./plotting/plot_shapes.py \
        -i datacard_shapes_prefit.root \
        -f et_ztt_prefit et_zll_prefit et_ss_prefit et_w_prefit et_tt_prefit et_misc_prefit \
        --title "e#tau_{h}" \
        --QCD-extrap-fit

    ./plotting/plot_shapes.py \
        -i datacard_shapes_postfit_sb.root \
        -f et_ztt_postfit et_zll_postfit et_ss_postfit et_w_postfit et_tt_postfit et_misc_postfit \
        --title "e#tau_{h}" \
       	--QCD-extrap-fit
fi

if [[ " $@ " =~ " mt " ]]; then
    ./plotting/plot_shapes.py \
        -i datacard_shapes_prefit.root \
        -f mt_ztt_prefit mt_zll_prefit mt_ss_prefit mt_w_prefit mt_tt_prefit mt_misc_prefit \
        --title "#mu#tau_{h}" \
       	--QCD-extrap-fit

    ./plotting/plot_shapes.py \
        -i datacard_shapes_postfit_sb.root \
        -f mt_ztt_postfit mt_zll_postfit mt_ss_postfit mt_w_postfit mt_tt_postfit mt_misc_postfit \
        --title "#mu#tau_{h}" \
       	--QCD-extrap-fit
fi

if [[ " $@ " =~ " tt " ]]; then
    ./plotting/plot_shapes.py \
        -i datacard_shapes_prefit.root \
        -f tt_noniso_prefit tt_misc_prefit \
        --title "#tau_{h}#tau_{h}" \
       	--QCD-extrap-fit

    ./plotting/plot_shapes.py \
        -i datacard_shapes_postfit_sb.root \
        -f tt_noniso_postfit tt_misc_postfit \
        --title "#tau_{h}#tau_{h}" \
       	--QCD-extrap-fit
fi
