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
    variables = {
        "mt" : ['pt_1','pt_2','eta_1','eta_2','m_vis','ptvis','pt_tt_puppi','DiTauDeltaR','puppimet','puppimetphi','puppimetcov01','puppimetcov11','mt_tot_puppi','m_sv_puppi','njets','nbtag','mt_1_puppi','mjj','jdeta','jeta_1','jeta_2','jpt_1','jpt_2','beta_1','beta_2','bpt_1','bpt_2','dijetpt'],
        "et" : ['pt_1','pt_2','eta_1','eta_2','m_vis','ptvis','pt_tt_puppi','DiTauDeltaR','puppimet','puppimetphi','puppimetcov01','puppimetcov11','mt_tot_puppi','m_sv_puppi','njets','nbtag','mt_1_puppi','mjj','jdeta','jeta_1','jeta_2','jpt_1','jpt_2','beta_1','beta_2','bpt_1','bpt_2','dijetpt'],
        "tt" : ['pt_1','pt_2','eta_1','eta_2','m_vis','ptvis','pt_tt_puppi','DiTauDeltaR','puppimet','puppimetphi','puppimetcov01','puppimetcov11','mt_tot_puppi','m_sv_puppi','njets','nbtag','mjj','jdeta','jeta_1','jeta_2','jpt_1','jpt_2','beta_1','beta_2','bpt_1','bpt_2','dijetpt'],
        "em" : ['pt_1','pt_2','eta_1','eta_2','m_vis','ptvis','pt_tt_puppi','DiTauDeltaR','puppimet','puppimetphi','puppimetcov01','puppimetcov11','mt_tot_puppi','m_sv_puppi','njets','nbtag','mjj','jdeta','jeta_1','jeta_2','jpt_1','jpt_2','beta_1','beta_2','bpt_1','bpt_2','dijetpt', 'pZetaPuppiMissVis'],
    }
    variables = {
        "mt" : ['m_vis'],
        "et" : ['m_vis'],
        "tt" : ['m_vis'],
        "em" : ['m_vis'],
    }

    with open("control_plot_arguments.txt", "w") as f:
        for year in ['2016', '2017','2018']:
            for ch in processes:
                for variable in variables[ch]:
                    process_list = copy.deepcopy(processes[ch])
                    process_list += ["_".join(["bbH",str(m)]) for m in mass_dict[year]["bbH"]]
                    for process in process_list:
                        f.write(
                            tmp_str.format(
                                os.getcwd(),
                                1,
                                year,
                                variable,
                                process,
                                "inclusive",
                                ch)
                            )
    return


if __name__ == "__main__":
    main()
