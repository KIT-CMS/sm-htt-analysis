#!/usr/bin/env python

import argparse
import os
import sys
import yaml
import copy

def main():
    tmp_str = "{} {} {} {} {} {} {}\n"
    mass_dict = {
        "2016": {
            "bbH": [500, 1400],
        },
        "2017": {
            "bbH": [500, 1400],
        },
        "2018": {
            "bbH": [500, 1400],
        }
    }
    processes = {
        "mt" : ["data_obs", "EMB", "jetFakes", "ZL", "TTL", "VVL", "WH125", "ZH125", "ttH125", "ggHWW125", "qqHWW125", "ZHWW125", "WHWW125", "ggH125", "qqH125"],
        "et" : ["data_obs", "EMB", "jetFakes", "ZL", "TTL", "VVL", "WH125", "ZH125", "ttH125", "ggHWW125", "qqHWW125", "ZHWW125", "WHWW125", "ggH125", "qqH125"],
        "tt" : ["data_obs", "EMB", "jetFakes", "ZL", "TTL", "VVL", "WH125", "ZH125", "ttH125", "ggHWW125", "qqHWW125", "ZHWW125", "WHWW125", "ggH125", "qqH125"],
        "em" : ["data_obs", "EMB", "W", "ZL", "TTL", "VVL", "QCD", "WH125", "ZH125", "ttH125", "ggHWW125", "qqHWW125", "ZHWW125", "WHWW125", "ggH125", "qqH125"],
    }
    variables_per_cat = {
        "inclusive" : {
            "mt" : ['mt_1_puppi','nbtag'],
            "et" : ['mt_1_puppi','nbtag'],
            "tt" : ['nbtag'],
            "em" : ['pZetaPuppiMissVis','nbtag'],
        },
        "signal_region" : {
            "mt" : ['nbtag'],
            "et" : ['nbtag'],
            "tt" : ['nbtag'],
            "em" : ['nbtag'],
        },
        "nobtag_lowmsv" : {
            "mt" : ['DiTauDeltaR','mjj','pt_tt_puppi','jdeta','njets'],
            "et" : ['DiTauDeltaR','mjj','pt_tt_puppi','jdeta','njets'],
            "tt" : ['DiTauDeltaR','mjj','pt_tt_puppi','jdeta','njets'],
            "em" : ['DiTauDeltaR','mjj','pt_tt_puppi','jdeta','njets'],
        },
        "nobtag_lowmsv_2jet_lowdeltar_mediummjj" : {
            "mt" : ['m_sv_puppi_sm', 'mt_tot_puppi_sm'],
            "et" : ['m_sv_puppi_sm', 'mt_tot_puppi_sm'],
            "tt" : [],
            "em" : [],
        },
        "nobtag_lowmsv_2jet_lowdeltar_highmjj" : {
            "mt" : ['m_sv_puppi_sm', 'mt_tot_puppi_sm'],
            "et" : ['m_sv_puppi_sm', 'mt_tot_puppi_sm'],
            "tt" : [],
            "em" : [],
        },
        "btag_tightmt" : {
            "mt" : ['m_sv_puppi_bsm', 'mt_tot_puppi_bsm'],
            "et" : ['m_sv_puppi_bsm', 'mt_tot_puppi_bsm'],
            "tt" : [],
            "em" : [],
        },
    }

    with open("categorization_arguments.txt", "w") as f:
        for year in ['2016', '2017', '2018']:
            for ch in processes:
                for category in variables_per_cat:
                    for variable in variables_per_cat[category][ch]:
                        process_list = copy.deepcopy(processes[ch])
                        process_list += ["_".join(["bbH",str(m)]) for m in mass_dict[year]["bbH"]]
                        for process in process_list:
                            f.write(
                                tmp_str.format(
                                    os.getcwd(),
                                    8 if process in ["EMB", "QCD", "jetFakes", "TTL"] else 1,
                                    year,
                                    variable, # category dependent
                                    process,
                                    category,
                                    ch)
                                )
    return


if __name__ == "__main__":
    main()
