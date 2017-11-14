#!/bin/bash

source utils/setup_cmssw.sh

if [[ " $@ " =~ " et " ]]; then
    ./plotting/plot_control.py -v et_keras21_max_score -c et_ZTT et_ZLL et_W et_TT et_QCD --scale-signal 50 --channel et
fi

if [[ " $@ " =~ " mt " ]]; then
    ./plotting/plot_control.py -v mt_keras21_max_score -c mt_ZTT mt_ZLL mt_W mt_TT mt_QCD --scale-signal 50 --channel mt
fi

if [[ " $@ " =~ " tt " ]]; then
    ./plotting/plot_control.py -v tt_keras4_max_score -c tt_ZTT tt_ZLL tt_W tt_TT tt_QCD --scale-signal 50 --channel tt
fi
