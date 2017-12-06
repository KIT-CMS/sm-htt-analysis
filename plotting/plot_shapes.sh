#!/bin/bash

source utils/setup_cmssw.sh

if [[ " $@ " =~ " et " ]]; then
    ./plotting/plot_shapes.py \
        -i datacard_shapes_prefit.root \
        -f et_ztt_prefit et_zll_prefit et_ss_prefit et_w_prefit et_tt_prefit et_misc_prefit et_ggh_prefit et_qqh_prefit \
        --title "e#tau_{h}"

    ./plotting/plot_shapes.py \
        -i datacard_shapes_postfit_sb.root \
        -f et_ztt_postfit et_zll_postfit et_ss_postfit et_w_postfit et_tt_postfit et_misc_postfit et_ggh_postfit et_qqh_postfit \
        --title "e#tau_{h}"
fi

if [[ " $@ " =~ " mt " ]]; then
    ./plotting/plot_shapes.py \
        -i datacard_shapes_prefit.root \
        -f mt_ztt_prefit mt_zll_prefit mt_ss_prefit mt_w_prefit mt_tt_prefit mt_misc_prefit mt_ggh_prefit mt_qqh_prefit \
        --title "#mu#tau_{h}"

    ./plotting/plot_shapes.py \
        -i datacard_shapes_postfit_sb.root \
        -f mt_ztt_postfit mt_zll_postfit mt_ss_postfit mt_w_postfit mt_tt_postfit mt_misc_postfit mt_ggh_postfit mt_qqh_postfit \
        --title "#mu#tau_{h}"
fi

if [[ " $@ " =~ " tt " ]]; then
    ./plotting/plot_shapes.py \
        -i datacard_shapes_prefit.root \
        -f tt_ztt_prefit tt_noniso_prefit tt_misc_prefit tt_ggh_prefit tt_qqh_prefit \
        --title "#tau_{h}#tau_{h}"

    ./plotting/plot_shapes.py \
        -i datacard_shapes_postfit_sb.root \
        -f tt_ztt_postfit tt_noniso_postfit tt_misc_postfit tt_ggh_postfit tt_qqh_postfit \
        --title "#tau_{h}#tau_{h}"
fi
