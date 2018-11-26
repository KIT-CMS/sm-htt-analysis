#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import yaml
import ROOT
import numpy
import copy
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
        "-c",
        "--config",
        required=True,
        type=str,
        help="Key of desired config in yaml config file.")
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
    parser.add_argument(
        "--category-mode", type=str, help="Category mode. If 'inclusive' fake factors are calculated inclusively, otherwise depending on NN categories")
    parser.add_argument(
        "-w",
        "--fractions-from-worspace",
        action="store_true",
        default=False,
        help="Use fractions from workspace."
    )
    parser.add_argument(
        "--workspace", type=str, help="Path to workspace for fractions if -w option is set")
    return parser.parse_args()


def determine_fractions(args, categories):
    hist_file = ROOT.TFile("fake-factors/%s_ff_yields.root" % args.era)
    era_labels = {
        "2016" : "Run2016",
        "2017" : "Run2017ReReco31Mar"
            }
    composition = {
        "mt": {
            "data": ["data_obs"],
            "W": ["W", "VVJ", "ZJ"],
            "TT": ["TTJ"],
            "QCD": ["QCD"],
            "real": ["EMB", "ZL", "TTL", "VVL"] #["ZTT", "ZL", "TTT", "TTL", "VVT", "VVL"]
        },
        "et": {
            "data": ["data_obs"],
            "W": ["W", "VVJ", "ZJ"],
            "TT": ["TTJ"],
            "QCD": ["QCD"],
            "real": ["EMB", "ZL", "TTL", "VVL"] #["ZTT", "ZL", "TTT", "TTL", "VVT", "VVL"]
        },
        "tt": {
            "data": ["data_obs"],
            "W": ["W", "VVJ", "ZJ"],
            "TT": ["TTJ"],
            "QCD": ["QCD"],
            "real": ["EMB", "ZL", "TTL", "VVL"] #["ZTT", "ZL", "TTT", "TTL", "VVT", "VVL"]
        }
    }
    fractions = {}
    for channel in categories.keys():
        subdict = {}
        for category in categories[channel]:
            subsubdict = {}
            for fraction in composition[channel].keys():
                subsubdict[fraction] = copy.deepcopy(
                    hist_file.Get(
                        "#{ch}#{ch}_{cat}#data_obs#smhtt#{era}#{expr}#125#".
                        format(
                            ch=channel,
                            cat=category,
                            era=era_labels[args.era],
                            expr=args.config)))
                subsubdict[fraction].Reset()
            for fraction in composition[channel].keys():
                if fraction == "QCD":
                    continue
                for process in composition[channel][fraction]:
                    subsubdict[fraction].Add(
                        hist_file.Get(
                            "#{ch}#{ch}_{cat}#{proc}#smhtt#{era}#{expr}#125#".
                            format(
                                ch=channel,
                                cat=category,
                                proc=process,
                                era=era_labels[args.era],
                                expr=args.config)))
                if fraction == "data":
                    subsubdict["QCD"].Add(subsubdict[fraction], 1.0)
                else:
                    subsubdict["QCD"].Add(subsubdict[fraction], -1.0)
            #normalize to data to get fractions
            denominator_hist = copy.deepcopy(subsubdict["data"])
            for fraction in composition[channel].keys():
                subsubdict[fraction].Divide(denominator_hist)
            #sanity check: if QCD negative i.e. data < MC, normalize to MC
            for i in range(subsubdict["QCD"].GetNbinsX()+2):
                qcd_fraction = subsubdict["QCD"].GetBinContent(i)
                if qcd_fraction < 0.0:
                    logger.info("Found bin with negative QCD fraction (%s, %s, index %i). Set fraction to zero and rescale other fractions..."%(channel, category, i))
                    subsubdict["QCD"].SetBinContent(i, 0)
                    for fraction in composition[channel].keys():
                        if not fraction == "data":
                            subsubdict[fraction].SetBinContent(i, subsubdict[fraction].GetBinContent(i) / (1.0 - qcd_fraction))
                            logger.debug("Rescaled %s fraction to %f"%(fraction, subsubdict[fraction].GetBinContent(i)))
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
            "ff_w_syst", "ff_w_dm0_njet0_stat", "ff_w_dm0_njet1_stat",
            "ff_tt_syst", "ff_tt_dm0_njet0_stat", "ff_tt_dm0_njet1_stat"
        ],
        "mt": [
            "ff_qcd_syst", "ff_qcd_dm0_njet0_stat", "ff_qcd_dm0_njet1_stat",
            "ff_w_syst", "ff_w_dm0_njet0_stat", "ff_w_dm0_njet1_stat",
            "ff_tt_syst", "ff_tt_dm0_njet0_stat", "ff_tt_dm0_njet1_stat"
        ],
        "tt": [
            "ff_qcd_syst", "ff_qcd_dm0_njet0_stat", "ff_qcd_dm0_njet1_stat",
            "ff_w_syst", "ff_tt_syst", "ff_w_frac_syst", "ff_tt_frac_syst"
        ]
    }

    #determine channel
    channels = ["et", "mt", "tt"]
    pipelines = ["nominal"]
    if "SingleElectron" in datafile or "_ElTau" in datafile:
        channels = ["et"]
    elif "SingleMuon" in datafile or "_MuTau" in datafile:
        channels = ["mt"]
    elif ("Tau" in datafile and "Run%s"%args.era in datafile) or "_TauTau" in datafile:
        channels = ["tt"]
    else:
        channels = ["et", "mt", "tt"]
    if not "Run%s"%args.era in datafile:
        pizero="PiZeros" if args.era=="2016" else "OnePiZero"
        pipelines = ["nominal", "tauEsOneProngUp", "tauEsOneProngDown",
                     "tauEsOneProng%sUp"%pizero, "tauEsOneProng%sDown"%pizero,
                     "tauEsThreeProngUp", "tauEsThreeProngDown"]
    for channel in channels:
        for pipeline in pipelines:
            
            #prepare data inputs
            input_file = ROOT.TFile(os.path.join(args.directory, datafile), "READ")
            #input_friend_file = ROOT.TFile(
            #    os.path.join(getattr(args, "%s_friend_directory" % channel), datafile),
            #    "READ")
            input_tree = input_file.Get("%s_%s/ntuple" %(channel, pipeline))
            #input_friend = input_friend_file.Get("%s_%s/ntuple" %(channel, pipeline))
            #input_tree.AddFriend(input_friend)

            #load fake factors histograms
            ff_file = ROOT.TFile.Open(
                getattr(args, "%s_fake_factor_directory" % channel))
            ff = ff_file.Get('ff_comb')

            #prepare output
            logger.debug(
                "...initialize %s" % os.path.join(args.output_directory, datafile))
            if not os.path.exists(os.path.join(args.output_directory, os.path.dirname(datafile))):
                os.mkdir(os.path.join(args.output_directory, os.path.dirname(datafile)))
            output_file = ROOT.TFile(
                os.path.join(args.output_directory, datafile), "UPDATE")
            output_root_dir = output_file.mkdir("%s_%s" %(channel, pipeline))
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
                                "ff%i_nom/D" % x)
                for syst in unc_shifts[channel]:
                    for shift in ["up", "down"]:
                        output_buffer["%s_%s_%i" % (syst, shift, x)] = numpy.zeros(
                            1, dtype=float)
                        output_tree.Branch("ff%i_%s_%s" % (x, syst, shift),
                                        output_buffer["%s_%s_%i" %
                                                        (syst, shift,
                                                        x)], "ff%i_%s_%s/D" % (x, syst, shift))

            #fill tree
            for event in input_tree:
                for x in suffix[channel]:
                    inputs = []
                    cat_index = -1 if args.category_mode=="inclusive" else int(
                        getattr(event, "%s_max_index" % channel) +
                        (0.5 * len(categories[channel])
                        if channel == "tt" and x == 2 else 0.0))
                    qcd_fraction = 0.0
                    w_fraction = 0.0            
                    tt_fraction = 0.0
                    if args.fractions_from_worspace:
                        fractions.var("cat").setVal(-1 if args.category_mode=="inclusive" else getattr(event, "%s_max_index" % channel))
                        fractions.var("m_vis").setVal(event.m_vis)
                        fractions.var("njets").setVal(event.njets)
                        fractions.var("aiso").setVal(x)
                        qcd_fraction = fractions.function("%s_frac_qcd"%channel[0]).getVal()
                        w_fraction = fractions.function("%s_frac_w"%channel[0]).getVal()
                        tt_fraction = fractions.function("%s_frac_tt"%channel[0]).getVal()
                    else:
                        varvalue = 0.0
                        if args.config=="njets_mvis":
                            varvalue = 300.0*min(event.njets, 2.0) + min(290.0, event.m_vis)
                        else:
                            varvalue = getattr(event, args.configdict[channel]["expression"])
                        cat_fractions = fractions[channel][categories[channel][cat_index]]
                        bin_index = cat_fractions["data"].GetXaxis().FindBin(varvalue)
                        qcd_fraction = cat_fractions["QCD"].GetBinContent(bin_index)
                        w_fraction = cat_fractions["W"].GetBinContent(bin_index)
                        tt_fraction = cat_fractions["TT"].GetBinContent(bin_index)
                    fraction_sum = qcd_fraction + w_fraction + tt_fraction
                    qcd_fraction /= fraction_sum
                    w_fraction /= fraction_sum
                    tt_fraction /= fraction_sum
                    if channel == "tt":
                        inputs = [
                            getattr(event, "pt_%i" % x),
                            getattr(event, "pt_%i" % (3 - x)),
                            getattr(event, "decayMode_%i" % x), event.njets,
                            event.m_vis, qcd_fraction,
                            w_fraction,
                            tt_fraction
                        ]
                    else:
                        inputs = [
                            event.pt_2, event.decayMode_2, event.njets, event.m_vis,
                            event.mt_1, event.iso_1,
                            qcd_fraction,
                            w_fraction,
                            tt_fraction
                        ]
                    output_buffer["nom_%i" % x][0] = ff.value(
                        len(inputs), array('d', inputs))
                    if not (output_buffer["nom_%i" % x][0] >= 0.0 and output_buffer["nom_%i" % x][0] <= 999.0):
                        output_buffer["nom_%i" % x][0] = 0.0
                    for syst in unc_shifts[channel]:
                        for shift in ["up", "down"]:
                            output_buffer["%s_%s_%i" % (syst, shift, x)][0] = ff.value(
                                len(inputs), array('d', inputs), "%s_%s" % (syst,
                                                                            shift))
                            if not (output_buffer["%s_%s_%i" % (syst, shift, x)][0] >= 0.0 and output_buffer["%s_%s_%i" % (syst, shift, x)][0] <= 999.0):
                                #output_buffer["%s_%s_%i" % (syst, shift, x)][0] = 0.0
                                print syst + shift
                                print output_buffer["%s_%s_%i" % (syst, shift, x)][0]
                                print inputs
                                output_buffer["%s_%s_%i" % (syst, shift, x)][0] = 0.0
                output_tree.Fill()

            #save
            output_tree.Write()
            logger.debug("Successfully finished %s" % os.path.join(
                args.output_directory, datafile))

            #clean up
            ff.Delete()
            ff_file.Close()
            #input_friend_file.Close()
            input_file.Close()
            output_file.Close()


def main(args):
    config = yaml.load(open("fake-factors/config.yaml"))
    if not args.config in config.keys():
        logger.critical("Requested config key %s not available in fake-factors/config.yaml!" % args.config)
        raise Exception
    if args.category_mode=="inclusive":
        logger.warning("Option to calculate fake factors inclusively has been set. No categorization applied!")
    args.configdict = config[args.config]
    args.output_directory = args.configdict["outputdir"]
    categories = {
        "et": ["ggh", "qqh", "ztt", "zll", "w", "tt", "ss", "misc", "inclusive"], # be careful with ordering as NN categories are accessed via index!!!
        "mt": ["ggh", "qqh", "ztt", "zll", "w", "tt", "ss", "misc", "inclusive"],
        "tt": [
            "tt1_ggh", "tt1_qqh", "tt1_ztt", "tt1_noniso", "tt1_misc", "tt1_inclusive",
            "tt2_ggh", "tt2_qqh", "tt2_ztt", "tt2_noniso", "tt2_misc", "tt2_inclusive"
        ]
    }
    fractions = None
    if args.fractions_from_worspace:
        logger.info("Loading workspace from %s"%args.workspace)
        f = ROOT.TFile(args.workspace)
        fractions = f.Get("w")
        f.Close()
    else:
        fractions = determine_fractions(args, categories)

    #find paths to data files the fake factors are appended
    datafiles = []
    for entry in os.listdir(args.directory):
        if not("HToTauTau" in entry
                or "DoubleEG" in entry
                or "DoubleMuon" in entry
                or "MuonEG" in entry
                or "WJets" in entry
                or "W1Jets" in entry
                or "W2Jets" in entry
                or "W3Jets" in entry
                or "W4Jets" in entry
                or "DYJetsToLLM10to50_RunIIFall17MiniAODv2_PU2017_13TeV_MINIAOD_madgraph-pythia8_ext1-v1" in entry
                or "DYJetsToLLM10to50_RunIIFall17MiniAODv2_PU2017_13TeV_MINIAOD_madgraph-pythia8_v1" in entry
                or "ZZTo4L_RunIIFall17MiniAODv2_PU2017newpmx_13TeV_MINIAOD_powheg-pythia8_v1" in entry
                or "TTToSemiLeptonic_RunIIFall17MiniAODv2_PU2017_13TeV_MINIAOD_powheg-pythia8_v2" in entry): #no et folder in this file
            path = os.path.join(entry, "%s.root" % entry)

            #check whether expected files exist
            if not os.path.isfile(os.path.join(args.directory, path)):
                logger.critical(
                    "Expected file %s does not exist. Check --directory option!"
                )
                raise Exception
            '''if "SingleElectron" in entry:
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
                raise Exception'''

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
