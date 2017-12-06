#!/bin/bash

source utils/setup_cmssw.sh

if [[ " $@ " =~ " et " ]]; then
    ./plotting/plot_control.py -v et_max_score -c et_ztt et_zll et_w et_tt et_ss et_misc --scale-signal 50 --channel et
fi

if [[ " $@ " =~ " mt " ]]; then
    ./plotting/plot_control.py -v mt_max_score -c mt_ztt mt_zll mt_w mt_tt mt_ss mt_misc --scale-signal 50 --channel mt
fi

if [[ " $@ " =~ " tt " ]]; then
    ./plotting/plot_control.py -v tt_max_score -c tt_ztt tt_noniso tt_misc --scale-signal 50 --channel tt
fi
