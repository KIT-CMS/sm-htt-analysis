#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import ROOT
import numpy
from array import array
from multiprocessing import Pool

import argparse
import logging
logger = logging.getLogger()


def setup_logging(output_file, level=logging.DEBUG):
    logger.setLevel(level)
    formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    file_handler = logging.FileHandler(output_file, "w")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Calculate fake factors and create friend trees.")
    parser.add_argument(
        "--directory",
        required=True,
        type=str,
        help="Directory with Artus outputs.")
    parser.add_argument(
        "--et-friend-directory",
        default=None,
        type=str,
        help=
        "Directory arranged as Artus output and containing a friend tree for et."
    )
    parser.add_argument(
        "--mt-friend-directory",
        default=None,
        type=str,
        help=
        "Directory arranged as Artus output and containing a friend tree for mt."
    )
    parser.add_argument(
        "--tt-friend-directory",
        default=None,
        type=str,
        help=
        "Directory arranged as Artus output and containing a friend tree for tt."
    )
    parser.add_argument(
        "-o",
        "--output-directory",
        required=True,
        type=str,
        help=
        "Directory arranged as Artus output and to write friend trees into.")
    parser.add_argument(
        "--et-fake-factor-directory",
        required=True,
        type=str,
        help="Directory containing et fake factor inputs.")
    parser.add_argument(
        "--mt-fake-factor-directory",
        required=True,
        type=str,
        help="Directory containing mt fake factor inputs.")
    parser.add_argument(
        "--tt-fake-factor-directory",
        required=True,
        type=str,
        help="Directory containing tt fake factor inputs.")
    parser.add_argument(
        "--era", type=str, required=True, help="Experiment era.")
    parser.add_argument(
        "--num-threads",
        default=32,
        type=int,
        help="Number of threads to be used.")
    return parser.parse_args()


def determine_fractions(era, categories):
    hist_file = ROOT.TFile("fake-factors/%s_ff_yields.root" % era)
    composition = {
        "mt": {
            "data": ["data_obs"],
            "W": ["W", "VVJ", "ZJ"],
            "TT": ["TTJ"],
            "QCD": ["QCD"],
            "real": ["ZTT", "ZL", "TTT", "VVT"]
        },
        "et": {
            "data": ["data_obs"],
            "W": ["W", "VVJ", "ZJ"],
            "TT": ["TTJ"],
            "QCD": ["QCD"],
            "real": ["ZTT", "ZL", "TTT", "VVT"]
        },
        "tt": {
            "data": ["data_obs"],
            "W": ["W", "VVJ"],
            "TT": ["TTJ"],
            "QCD": ["QCD"],
            "DY": ["ZJ"],
            "real": ["ZTT", "ZL", "TTT", "VVT"]
        }
    }
    fractions = {}
    for channel in categories.keys():
        subdict = {}
        for category in categories[channel]:
            subsubdict = {"QCD": 0.0}
            for fraction in composition[channel].keys():
                if fraction == "QCD":
                    continue
                subsubdict[fraction] = sum(
                    ROOT.TH1F(
                        hist_file.Get(
                            "#{ch}#{ch}_{cat}#{proc}#smhtt#Run{era}#1.0#125#".
                            format(
                                ch=channel,
                                cat=category,
                                proc=process,
                                era=era))).Integral()
                    for process in composition[channel][fraction])
                if fraction == "data":
                    subsubdict["QCD"] += subsubdict[fraction]
                else:
                    subsubdict["QCD"] -= subsubdict[fraction]
            total_yield = subsubdict["data"]
            for fraction in composition[channel].keys():
                subsubdict[fraction] /= total_yield
            subdict[category] = subsubdict
        fractions[channel] = subdict
    hist_file.Close()
    return fractions


def apply_fake_factors(config):
    args = config[0]
    datafile = config[1]
    fractions = config[2]
    categories = config[3]

    unc_shifts = {  #documented in https://twiki.cern.ch/twiki/bin/viewauth/CMS/HiggsToTauTauJet2TauFakes
        "et": [
            "ff_qcd_syst", "ff_qcd_dm0_njet0_stat", "ff_qcd_dm0_njet1_stat",
            "ff_qcd_dm1_njet0_stat", "ff_qcd_dm1_njet1_stat", "ff_w_syst",
            "ff_w_dm0_njet0_stat", "ff_w_dm0_njet1_stat",
            "ff_w_dm1_njet0_stat", "ff_w_dm1_njet1_stat", "ff_tt_syst",
            "ff_tt_dm0_njet0_stat", "ff_tt_dm0_njet1_stat",
            "ff_tt_dm1_njet0_stat", "ff_tt_dm1_njet1_stat"
        ],
        "mt": [
            "ff_qcd_syst", "ff_qcd_dm0_njet0_stat", "ff_qcd_dm0_njet1_stat",
            "ff_qcd_dm1_njet0_stat", "ff_qcd_dm1_njet1_stat", "ff_w_syst",
            "ff_w_dm0_njet0_stat", "ff_w_dm0_njet1_stat",
            "ff_w_dm1_njet0_stat", "ff_w_dm1_njet1_stat", "ff_tt_syst",
            "ff_tt_dm0_njet0_stat", "ff_tt_dm0_njet1_stat",
            "ff_tt_dm1_njet0_stat", "ff_tt_dm1_njet1_stat"
        ],
        "tt": [
            "ff_qcd_syst", "ff_qcd_dm0_njet0_stat", "ff_qcd_dm0_njet1_stat",
            "ff_qcd_dm1_njet0_stat", "ff_qcd_dm1_njet1_stat", "ff_w_syst",
            "ff_tt_syst", "ff_w_frac_syst", "ff_tt_frac_syst",
            "ff_dy_frac_syst"
        ]
    }

    #determine channel
    if "SingleElectron" in datafile:
        channel = "et"
    elif "SingleMuon" in datafile:
        channel = "mt"
    else:  #sanity check of filenames already done in main
        channel = "tt"

    #prepare data inputs
    input_file = ROOT.TFile(os.path.join(args.directory, datafile), "READ")
    input_friend_file = ROOT.TFile(
        os.path.join(getattr(args, "%s_friend_directory" % channel), datafile),
        "READ")
    input_tree = input_file.Get("%s_nominal/ntuple" % channel)
    input_friend = input_friend_file.Get("%s_nominal/ntuple" % channel)
    input_tree.AddFriend(input_friend)

    #load fake factors histograms
    ff_file = ROOT.TFile.Open(
        getattr(args, "%s_fake_factor_directory" % channel))
    ff = ff_file.Get('ff_comb')

    #prepare output
    logger.debug(
        "...initialize %s" % os.path.join(args.output_directory, datafile))
    os.mkdir(os.path.join(args.output_directory, os.path.dirname(datafile)))
    output_file = ROOT.TFile(
        os.path.join(args.output_directory, datafile), "RECREATE")
    output_root_dir = output_file.mkdir("%s_nominal" % channel)
    output_root_dir.cd()
    output_tree = ROOT.TTree("ntuple", "ntuple")

    suffix = {  #one fake factor per tau is needed
        "et": [2],
        "mt": [2],
        "tt": [1, 2]
    }
    output_buffer = {}
    for x in suffix[channel]:
        output_buffer["nom_%i" % x] = numpy.zeros(1, dtype=float)
        output_tree.Branch("ff%i_nom" % x, output_buffer["nom_%i" % x],
                           "d0_1_calib/D")
        for syst in unc_shifts[channel]:
            for shift in ["up", "down"]:
                output_buffer["%s_%s_%i" % (syst, shift, x)] = numpy.zeros(
                    1, dtype=float)
                output_tree.Branch("ff%i_%s_%s" % (x, syst, shift),
                                   output_buffer["%s_%s_%i" %
                                                 (syst, shift,
                                                  x)], "d0_1_calib/D")

    #fill tree
    for event in input_tree:
        for x in suffix[channel]:
            inputs = []
            cat_fractions = fractions[channel][categories[channel][int(
                getattr(event, "%s_max_index" % channel) +
                (0.5 * len(categories[channel])
                 if channel == "tt" and x == 2 else 0.0))]]
            if channel == "tt":
                inputs = [
                    getattr(event, "pt_%i" % x),
                    getattr(event, "pt_%i" % (3 - x)),
                    getattr(event, "decayMode_%i" % x), event.njets,
                    event.m_vis
                ]
                inputs.extend((cat_fractions["QCD"], cat_fractions["W"],
                               cat_fractions["TT"], cat_fractions["DY"]))
            else:
                inputs = [
                    event.pt_2, event.decayMode_2, event.njets, event.m_vis,
                    event.mt_1, event.iso_1
                ]
                inputs.extend((cat_fractions["QCD"], cat_fractions["W"],
                               cat_fractions["TT"]))
            output_buffer["nom_%i" % x][0] = ff.value(
                len(inputs), array('d', inputs))
            for syst in unc_shifts[channel]:
                for shift in ["up", "down"]:
                    output_buffer["%s_%s_%i" % (syst, shift, x)][0] = ff.value(
                        len(inputs), array('d', inputs), "%s_%s" % (syst,
                                                                    shift))
        output_tree.Fill()

    #save
    output_tree.Write()
    logger.debug("Successfully finished %s" % os.path.join(
        args.output_directory, datafile))

    #clean up
    ff.Delete()
    ff_file.Close()
    input_friend_file.Close()
    input_file.Close()


def main(args):
    categories = {
        "et": ["ggh", "qqh", "ztt", "zll", "w", "tt", "ss", "misc"],
        "mt": ["ggh", "qqh", "ztt", "zll", "w", "tt", "ss", "misc"],
        "tt": [
            "tt1_ggh", "tt1_qqh", "tt1_ztt", "tt1_noniso", "tt1_misc",
            "tt2_ggh", "tt2_qqh", "tt2_ztt", "tt2_noniso", "tt2_misc"
        ]
    }
    fractions = determine_fractions(args.era, categories)

    #find paths to data files the fake factors are appended
    datafiles = []
    for entry in os.listdir(args.directory):
        if "Run%s" % args.era in entry and ("Single" in entry
                                            or "Tau" in entry):
            path = os.path.join(entry, "%s.root" % entry)

            #check whether expected files exist
            if not os.path.isfile(os.path.join(args.directory, path)):
                logger.critical(
                    "Expected file %s does not exist. Check --directory option!"
                )
                raise Exception
            if "SingleElectron" in entry:
                if not os.path.isfile(
                        os.path.join(args.et_friend_directory, path)):
                    logger.critical(
                        "Expected file %s does not exist. Check --et-friend-directory option!"
                    )
                    raise Exception
            elif "SingleMuon" in entry:
                if not os.path.isfile(
                        os.path.join(args.mt_friend_directory, path)):
                    logger.critical(
                        "Expected file %s does not exist. Check --mt-friend-directory option!"
                    )
                    raise Exception
            elif "Tau" in entry:
                if not os.path.isfile(
                        os.path.join(args.tt_friend_directory, path)):
                    logger.critical(
                        "Expected file %s does not exist. Check --tt-friend-directory option!"
                    )
                    raise Exception
            else:
                logger.critical(
                    "Filename %s does not match assumed naming scheme!")
                raise Exception

            datafiles.append(path)

    #create output directory
    if os.path.exists(args.output_directory):
        logger.critical(
            "Output directory %s already exists. I don't want to overwrite it!"
            % args.output_directory)
        raise Exception
    else:
        os.mkdir(args.output_directory)
        logger.info("Createt output directory")

    logger.info("Create friend trees...")

    pool = Pool(processes=args.num_threads)
    pool.map(apply_fake_factors, [[args, datafile, fractions, categories]
                                  for datafile in datafiles])
    pool.close()
    pool.join()
    del pool


if __name__ == "__main__":
    args = parse_arguments()
    setup_logging("{}_calculate_fake_factors.log".format(args.era),
                  logging.INFO)
    main(args)
