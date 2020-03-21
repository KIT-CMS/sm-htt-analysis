#!/usr/bin/env python

import argparse
import os
import sys
import yaml
import copy

def build_cat_names(channel):
    # Read in binning dictionary.
    if (sys.version_info.major <= 2
            and sys.version_info.minor <= 7
            and sys.version_info.micro <= 15):
        binning = yaml.load(open("cutbased_shapes/binning.yaml"))
    else:
        binning = yaml.load(open("cutbased_shapes/binning.yaml"),
                            Loader=yaml.FullLoader)
    categories = []
    for cat in binning["cutbased"][channel]:
        categories.append(cat)
        if cat in ["nobtag_lowmsv"]:
            for subcat in binning["stxs_stage1p1_v2"][channel]:
                categories.append("_".join([cat, subcat]))
    return categories

def main():
    tmp_str = "{} {} {} {} {} {} {}\n"
    mass_dict = {
        "2016": {
            "ggH": [80, 90, 100, 110, 120, 130, 140, 160, 180, 200, 250, 300, 350, 400, 450, 500, 600, 700, 800, 900, 1000, 1200, 1400, 1500, 1600, 1800, 2000, 2300, 2600, 2900, 3200],
            "bbH": [80, 90, 110, 120, 130, 140, 160, 180, 200, 250, 350, 400, 450, 500, 600, 700, 800, 900, 1000, 1200, 1400, 1600, 1800, 2000, 2300, 2600, 2900, 3200],
        },
        "2017": {
            "ggH": [80, 90, 100, 110, 120, 130, 140, 180, 200, 250, 300, 350, 400, 450, 600, 700, 800, 900, 1200, 1400, 1500, 1600, 1800, 2000, 2300, 2600, 2900, 3200],
            "bbH": [80, 90, 100, 110, 120, 125, 130, 140, 160, 180, 200, 250, 300, 350, 400, 450, 500, 600, 700, 800, 900, 1000, 1200, 1400, 1600, 1800, 2000, 2300, 2600, 2900, 3200, 3500],
        },
        "2018": {
            "ggH": [80, 90, 100, 110, 120, 130, 140, 160, 180, 200, 250, 300, 350, 400, 450, 600, 700, 800, 900, 1200, 1400, 1500, 1600, 1800, 2000, 2300, 2600, 2900, 3200],
            "bbH": [80, 90, 100, 110, 120, 125, 130, 140, 160, 180, 200, 250, 300, 350, 400, 450, 500, 600, 700, 800, 900, 1000, 1200, 1400, 1600, 1800, 2000, 2300, 2600, 2900, 3200, 3500],
        }
    }
    processes = {
        "mt" : ["data_obs", "EMB", "jetFakes", "ZL", "TTL", "VVL", "WH125", "ZH125", "ttH125", "ggHWW125", "qqHWW125", "ZHWW125", "WHWW125", "ggH125", "qqH125"],
        "et" : ["data_obs", "EMB", "jetFakes", "ZL", "TTL", "VVL", "WH125", "ZH125", "ttH125", "ggHWW125", "qqHWW125", "ZHWW125", "WHWW125", "ggH125", "qqH125"],
        "tt" : ["data_obs", "EMB", "jetFakes", "ZL", "TTL", "VVL", "WH125", "ZH125", "ttH125", "ggHWW125", "qqHWW125", "ZHWW125", "WHWW125", "ggH125", "qqH125"],
        "em" : ["data_obs", "EMB", "W", "ZL", "TTL", "VVL", "QCD", "WH125", "ZH125", "ttH125", "ggHWW125", "qqHWW125", "ZHWW125", "WHWW125", "ggH125", "qqH125"],
    }

    with open("arguments.txt", "w") as f:
        for year in ['2016', '2017', '2018']:
            for ch in processes:
                for category in build_cat_names(ch):
                    variable = "m_sv_puppi" if "nobtag_lowmsv" in category else "mt_tot_puppi"
                    process_list = copy.deepcopy(processes[ch])
                    for ggH_contr in ["ggh_t", "ggh_b", "ggh_i", "ggH_t", "ggH_b", "ggH_i", "ggA_t", "ggA_b", "ggA_i"]:
                        process_list += ["_".join([ggH_contr,str(m)]) for m in mass_dict[year]["ggH"]]
                    process_list += ["_".join(["bbH",str(m)]) for m in mass_dict[year]["bbH"]]
                    for process in process_list:
                        f.write(
                            tmp_str.format(
                                os.getcwd(),
                                1,
                                year,
                                variable, # category dependent
                                process,
                                category,
                                ch)
                            )
    return


if __name__ == "__main__":
    main()
