#!/usr/bin/env python
# -*- coding: utf-8 -*-

import HiggsAnalysis.KITHiggsToTauTau.plotting.higgsplot as higgsplot
import ROOT, json, os
import argparse
from copy import deepcopy

import logging
logger = logging.getLogger("")



def parse_arguments():
    parser = argparse.ArgumentParser(
        description=
        "Plot categories using HarryPlotter from shapes produced by shape-producer module."
    )
    parser.add_argument("--comparison", action="store_true", help="Plot Embedded - MC comparison. --emb has to be set.")
    parser.add_argument("--blind", action="store_true", help="Do not plot data")
    parser.add_argument("--emb", action="store_true", help="Embedded prefix")
    parser.add_argument("--ff", action="store_true", help="Use fake-factors")
    parser.add_argument(
        "-v",
        "--variables",
        nargs="+",
        type=str,
        required=True,
        help="Variable on x-axis")
    parser.add_argument(
        "--categories",
        nargs="+",
        type=str,
        required=False, default=None,
        help="Categories")
    parser.add_argument("--era", type=str, default="Run2018", help="Era")
    parser.add_argument(
        "--lumi", type=float, default=None, help="Integrated Luminosity")
    parser.add_argument("--mass", type=str, default="125", help="Mass")
    parser.add_argument(
        "--additional-arguments",
        type=str,
        default="",
        help="Additional higgsplot.py arguments")
    parser.add_argument(
        "--output-dir",
        type=str,
        default="plots",
        help="Output directory for plots")
    parser.add_argument(
        "--y-log",
        action="store_true",
        default=False,
        help="Use logarithmic y-axis")
    parser.add_argument(
        "--x-log",
        action="store_true",
        default=False,
        help="Use logarithmic x-axis")
    parser.add_argument(
        "-c",
        "--channels", nargs="+", type=str, required=True, help="Channel")
    parser.add_argument(
        "--analysis", type=str, default="smhtt", help="Analysis")
    parser.add_argument(
        "--shapes",
        type=str,
        default=None,
        help="ROOT files with shapes of processes")
    parser.add_argument(
        "--x-label", type=str, default=None, help="Label on x-axis")
    parser.add_argument("--chi2", action="store_true", help="Print chi2 value")
    parser.add_argument(
        "--num-processes",
        type=int,
        default=24,
        help="Number of processes used for plotting")

    parser.add_argument("--filename-prefix", type=str, default="", help="filename prefix")
    parser.add_argument("--www", action="store_true", help="webplotting")
    parser.add_argument("--www-dir", type=str, default=None,
        help='Directory structure where the plots will be uploaded. {date} expressions will be replaced by date.')
    parser.add_argument("--www-no-overwrite", action='store_true', default=False, help="Don't overwrite remote file. [Default: %(default)s]")
    parser.add_argument("--no-overwrite", "--keep-both", "--keep", "-k", action='store_true', default=False, help="Don't overwrite output file. [Default: %(default)s]")
    parser.add_argument("--log-level", default="debug", help="log level. [Default: %(default)s]")
    parser.add_argument("--redo-cache", action="store_true",
                        help="Do not use inputs from cached trees, but overwrite them. [Default: False for absolute paths, True for relative paths]")
    parser.add_argument("--prefit", action="store_true",
                        help="Switch to prefit plotting")

    return parser.parse_args()


def setup_logging(output_file, level=logging.DEBUG):
    logger.setLevel(level)
    formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    file_handler = logging.FileHandler(output_file, "w")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


config_template = {
    "colors": ["#B7B7B7", "#000000"],
    "filename": "",
    "files": [None],
    "labels": ["", ""],
    "legend": [0.38, 0.47, 0.88, 0.83],
    "legend_cols": 1,
    "legend_markers": ["ELP", "ELP"],
    "stacks": ["ratio_bkg", "ratio_data"],
    "markers": ["E2", "P"],
    "formats": ["pdf", "png"],
    "title": "",
    "cms": True,
    "extra_text": "Own Work",
    "energies": [13],
    "nicks_blacklist": ["noplot"],
    "analysis_modules": ["Ratio"],
    "ratio_result_nicks": ["ratio_Bkg", "ratio_Data"],
    "y_subplot_lims": [0.2, 2.2],
    "y_label": "N_{evts}",
    "y_subplot_label": "Bkg. unc.",
    "subplot_lines": [0.5, 1.0, 1.5]
}

logvars = ["nbtag","njets","jpt_1","jpt_2", "kinfit_chi2"]


def main(args,heavy_masses,light_masses):
    signal=[]
    signal_names=[]

    # signal_names=["ggh","qqh"]
    # signal=["ggH125","qqH125"]
    if "em" in args.channels:
        args.ff=False
    if not len(heavy_masses)==len(light_masses):
        print "both mass vectors must have same length"
        exit(1)
    for i in range(len(heavy_masses)):
        signal.append("NMSSM_{}_125_{}".format(heavy_masses[i],light_masses[i]))
        signal_names.append("nmssm_{}_125_{}".format(heavy_masses[i],light_masses[i]))
    if args.emb and args.ff:
        bkg_processes_names = [
         "emb", "zll", "ttl", "vvl",  "fakes" ,"htt"
        ]   
        bkg_processes = ["EMB", "ZL", "TTL", "VVL",  "jetFakes", "HTT"]
    elif args.emb:
        bkg_processes_names = ["emb", "zll","zj", "ttl", "ttj","vvl", "vvj", "w", "qcd"]
        bkg_processes = ["EMB", "ZL", "ZJ","TTL", "TTJ","VVL", "VVJ", "W", "QCD"]
    elif args.ff:
        bkg_processes_names = [
            "ztt", "zll", "ttt", "ttl", "vvt", "vvl", "fakes"
        ]  # enforced by HarryPlotter
        bkg_processes = ["ZTT", "ZL", "TTT", "TTL", "VVT", "VVL", "jetFakes"]
    else:
        bkg_processes_names = [
            "ztt", "zll","zj","ttl", "ttt","ttj","vvl","vvt","vvj","w","qcd"]
        bkg_processes = ["ZTT", "ZL", "ZJ","TTL","TTT", "TTJ", "VVL","VVT","VVJ","W","QCD"]
    channels = args.channels
    analysis = args.analysis
    era = args.era
    if args.lumi is None:
        if "2016" in era:
            lumi = 35.9
        elif "2017" in era:
            lumi = 41.5
        elif "2018" in era:
            lumi = 59.7
    else:
        lumi=args.lumi
    output_dir = args.output_dir+"/"+era
    y_log = args.y_log
    x_log = args.x_log

    mass = args.mass
    variables = args.variables
    categories = [c for c in args.categories] if args.categories is not None else None
    #if "em" in args.channels:
    #    categories = [c if c!="ff" else "ss" for c in categories]
    if "all" in variables:
        variables = ["mt_1","mt_2", "pt_1","pt_2", "eta_1", "eta_2", "m_vis", "ptvis", "npv", "njets", "nbtag", "jpt_1", "jpt_2", "jeta_1", "jeta_2", "met", "mjj", "dijetpt", "pZetaMissVis", "m_1", "m_2", "decayMode_1", "decayMode_2", "iso_1", "iso_2", "rho", "mt_tot", "d0_1", "d0_2", "dZ_1", "dZ_2"]

    if args.www:
        config_template['www'] = ''
    if args.www_dir:
        config_template['www_dir'] = args.www_dir
    if args.www_no_overwrite:
        config_template['www_no_overwrite'] = True
        config_template['no_overwrite'] = True
    if args.no_overwrite:
        config_template['no_overwrite'] = True
    if args.redo_cache:
        config_template['redo_cache'] = True

    if args.filename_prefix != '':
        args.filename_prefix = args.filename_prefix if args.filename_prefix[0] == '_' else '_' + args.filename_prefix
    # if args.log_level == 'debug':
        # config['log_level'] =

    configs = []
    for channel in channels:
        if args.categories is None:
            categories = [channel+"_"+v for v in variables]
        shapes = args.shapes if args.shapes is not None else "shapes_{}.root".format(channel)
        if "em" in channel:
            bkg_processes = [p for p in bkg_processes if p not in ["ZJ", "TTJ", "VVJ"]]
            bkg_processes_names = [p for p in bkg_processes_names if p not in ["zj", "ttj", "vvj"]]
        if len(variables)==1:
            variables=[variables[0]]*len(categories)
        for variable, category in zip(variables, categories):
            config = deepcopy(config_template)

            if args.chi2:
                config["analysis_modules"].append("AddHistograms")
                config["analysis_modules"].append("Chi2Test")
                config["add_nicks"] = [" ".join(bkg_processes_names)]
                config["add_result_nicks"] = ["tot_background_noplot"]
                config["chi2test_nicks"] = ["tot_background_noplot data"]
                config["chi2test_compare"] = ["UU CHI2/NDF"]

            config["files"] = [shapes]
            config["lumis"] = [lumi]
            config["year"] = era.strip("Run")
            config["output_dir"] = output_dir+"/"+channel+"/"+category
            config["y_log"] = True if ((variable in logvars) or y_log) else False
            config["x_log"] = True if x_log else False

            config["y_rel_lims"] = [5, 3500] if (variable in logvars) else [0., 1.9]
            if variable == "m_sv_puppi" and channel in ["mt","et"]:
                config["y_rel_lims"] = [0.,1.9]
            config["markers"] = ["HIST"] * len(bkg_processes_names) + ["E2"]  + ["LINE"]*len(signal_names) + ["P"] + ["E2"] + ["LINE"]*len(signal_names) + ["P"]
            config["legend_markers"] = ["F"] * (len(bkg_processes_names))   + ["F"] +  ["LX0"]*len(signal_names) + ["ELP"] + ["E2"] + ["L"]*len(signal_names) + ["P"]
            signal_label = []#['#scale[0.85]{H(%s)#rightarrowh(125)h"(%s) (1 pb)}'%(heavy_mass,light_mass)] if channel=="tt" else ['#scale[0.85]{H(%s)#rightarrowh(125)h"(%s) (10 pb)}'%(heavy_mass,light_mass)]
            for i in range(len(heavy_masses)):
                sig_string = '#scale[0.95]{H(%s)#rightarrowh(125)h"(%s) (1 pb)}'%(heavy_masses[i],light_masses[i]) if channel=="tt" else '#scale[0.95]{H(%s)#rightarrowh(125)h"(%s) (10 pb)}'%(heavy_masses[i],light_masses[i])
                signal_label.append(sig_string)
            sig_colors = ["#8B008B", "#8a8a00", "#008a8a", "#8a0022", "#22008a"]
            config["labels"] = bkg_processes_names + ["Bkg.unc."] + signal_label + ["data"
                                                      ] + [""]*len(signal_names) + config["labels"]
            config["colors"] = bkg_processes_names + ["transgrey"] + sig_colors[:len(signal_names)] + ["data"
                                                      ] + ["#B7B7B7"] + sig_colors[:len(signal_names)] + ["#000000"]
            config["nicks"] = bkg_processes_names + signal_names + ["data"]
            
            config["scale_factors"] = [1]*len(bkg_processes_names) + [10]*len(signal_label) + [1] if channel=="tt" else [1]*len(bkg_processes_names) + [100]*len(signal_label) + [1]

                
            config["x_expressions"] = [
                "#" + "#".join([
                    channel, category, process, analysis, era, variable, mass
                ]) + "#" for process in bkg_processes+signal
            ] + [
                "#" + "#".join([
                    channel, category, "data_obs", analysis, era, variable,
                    mass
                ]) + "#"
            ]
            if args.emb == False:
                config["filename"] = "_".join(
                    [channel, category, analysis, era, variable, mass, str(heavy_mass), str(light_mass)])
            else:
                config["filename"] = "_".join(
                    [channel, category, analysis, era, variable, mass, str(500), str(100), "emb"])
            if args.comparison:
                config["filename"] = "_".join(
                    [channel, category, analysis, era, variable, mass,"comparison"]) + args.filename_prefix
            if args.ff:
                config["filename"] = config["filename"]+"_ff"
            if not args.x_label == None:
                config["x_label"] = args.x_label
            else:
                config["x_label"] = "_".join([channel, variable])
            if "1btag" in category:
                if "bb" in variable:
                    config["x_label"] = config["x_label"]+"_1btag"
            title_dict = {}
            title_dict["mt"] = "#mu#tau_{h}"
            title_dict["tt"] = "#tau_{h}#tau_{h}"
            title_dict["et"] = "e#tau_{h}"
            title_dict["em"] = "e#mu"

            config["title"] = "#scale[0.8]{" + title_dict[channel] + " " + category[3:].replace("NMSSM_","") + "}" #"_".join(["channel", channel])
	    if "highCSVjet" in category:
	            config["title"] = "#scale[0.8]{" + title_dict[channel] + "} #scale[0.5]{" + category[3:].replace("NMSSM_","") + "}" #"_".join(["channel", channel])

            config["stacks"] = ["mc"] * len(bkg_processes_names) + signal_names + ["bkg_unc"] +[
                "data"
            ] + [x+"Ratio" for x in signal_names] + config["stacks"]
            config["ratio_denominator_nicks"] = [
                " ".join(bkg_processes_names)
            ] * (2+len(signal_names))
            config["ratio_numerator_nicks"] = [" ".join(bkg_processes_names)]
            for i in range(len(signal_names)):
                config["ratio_numerator_nicks"].append(" ".join(bkg_processes_names+[signal_names[i]]))
            config["ratio_numerator_nicks"].append("data")
            config["ratio_result_nicks"] = ["bkg_ratio"] + [x+"_ratio" for x in signal_names] + ["data_ratio"]

            config["analysis_modules"].append("AddHistograms")
            config["add_nicks"] = [" ".join(bkg_processes_names),]
            config["add_result_nicks"] = ["background_uncertainty"]

            if args.blind:
                for key in config.keys():
                    if isinstance(config[key], list):
                        if isinstance(config[key][0], str):
                            config[key] = [x for x in config[key] if (not "data" in x)]
                            if "marker" in key:
                                config[key] = [x for x in config[key] if (x!="P")]
                        if key in ["ratio_denominator_nicks","scale_factors","colors"]:
                            config[key] = config[key][:-1]
                config["legend_cols"] = 1
            configs.append(config)

    higgsplot.HiggsPlotter(
        list_of_config_dicts=configs,
        list_of_args_strings=[args.additional_arguments],
        n_processes=args.num_processes)


def prefit(args,heavy_mass,light_mass):
    signal=[]
    signal_names=[]

    prefit_categories = { 
        1 : "emb",
        2 : "tt",
        3 : "misc",
        4 : "ff",
        5 : "NMSSM_MH1001toinfty_boosted",
        6 : "NMSSM_MH240to240_unboosted",
        7 : "NMSSM_MH280to280_unboosted",
        8 : "NMSSM_MH320to320_unboosted",
        9 : "NMSSM_MH321to500_boosted",
        10 : "NMSSM_MH321to500_unboosted",
        11 : "NMSSM_MH501to700_boosted",
        12 : "NMSSM_MH501to700_unboosted",
        13 : "NMSSM_MH701to1000_boosted",
        14 : "NMSSM_MH701to1000_unboosted"
    }
    

    # folders = ["htt_{}_{}_2016_prefit".format(args.channels[0],x,era.strip("Run") for x in categories.keys())

    # signal_names=["ggh","qqh"]
    # signal=["ggH125","qqH125"]
    if "em" in args.channels:
        args.ff=False
        prefit_categories.update({4: "ss"})
    signal.append("NMSSM_{}_125_{}".format(heavy_mass,light_mass))
    signal_names.append("nmssm_{}_125_{}".format(heavy_mass,light_mass))

    if args.emb and args.ff:
        bkg_processes_names = [
         "emb", "zll", "ttl", "vvl", "fakes", "htt"
        ]
        bkg_processes = ["EMB", "ZL", "TTL", "VVL", "jetFakes", "HTT"]

    elif args.emb:
        bkg_processes_names = ["emb", "zll","zj", "ttl", "ttj","vvl", "vvj", "w", "qcd"]
        bkg_processes = ["EMB", "ZL", "ZJ","TTL", "TTJ","VVL", "VVJ", "W", "QCD"]
    elif args.ff:
        bkg_processes_names = [
            "ztt", "zll", "ttt", "ttl", "vvt", "vvl", "fakes"
        ]  # enforced by HarryPlotter
        bkg_processes = ["ZTT", "ZL", "TTT", "TTL", "VVT", "VVL", "jetFakes"]
    else:
        bkg_processes_names = [
            "ztt", "zll","zj","ttl", "ttt","ttj","vvl","vvt","vvj","w","qcd"]
        bkg_processes = ["ZTT", "ZL", "ZJ","TTL","TTT", "TTJ", "VVL","VVT","VVJ","W","QCD"]

    if "em" in args.channels:
        bkg_processes = [p for p in bkg_processes if p not in ["ZJ", "TTJ", "VVJ"]]
        bkg_processes_names = [p for p in bkg_processes_names if p not in ["zj", "ttj", "vvj"]]

    bkg_processes_save = [x for x in bkg_processes]
    bkg_processes_names_save = [x for x in bkg_processes_names]

    rfile = ROOT.TFile(args.shapes)


    channels = args.channels
    analysis = args.analysis
    era = args.era
    if args.lumi is None:
        if "2016" in era:
            lumi = 35.9
        elif "2017" in era:
            lumi = 41.5
        elif "2018" in era:
            lumi = 59.7
    else:
        lumi=args.lumi
    output_dir = args.output_dir+"/"+era
    y_log = args.y_log
    x_log = args.x_log

    mass = args.mass
    variables = args.variables

    if args.www:
        config_template['www'] = ''
    if args.www_dir:
        config_template['www_dir'] = args.www_dir
    if args.www_no_overwrite:
        config_template['www_no_overwrite'] = True
        config_template['no_overwrite'] = True
    if args.no_overwrite:
        config_template['no_overwrite'] = True
    if args.redo_cache:
        config_template['redo_cache'] = True

    if args.filename_prefix != '':
        args.filename_prefix = args.filename_prefix if args.filename_prefix[0] == '_' else '_' + args.filename_prefix
    # if args.log_level == 'debug':
        # config['log_level'] =
    
    configs = []
    for channel in channels:
        if args.categories is None:
            categories = [channel+"_"+v for v in variables]
        shapes = args.shapes if args.shapes is not None else "shapes_{}.root".format(channel)
        if len(variables)==1:
            variables=[variables[0]]*len(prefit_categories.keys())
        for variable, category in zip(variables, prefit_categories.keys()):
            config = deepcopy(config_template)
            bkg_processes = [p for p in bkg_processes_save]
            bkg_processes_names = [p for p in bkg_processes_names_save]
            empty_processes = []
            empty_names = []
            fit_mode = "postfit" if "postfit" in shapes else "prefit"
            for process,name in zip(bkg_processes,bkg_processes_names):
                if not rfile.Get("htt_{}_{}_{}_{}/{}".format(args.channels[0],category,era.strip("Run"),fit_mode,process)):
                    print "Process {} not found for category htt_{}_{}_{}_{}. Continuing.".format(process,args.channels[0],category,era.strip("Run"),fit_mode)
                    empty_processes.append(process)
                    empty_names.append(name)
            for process,name in zip(signal,signal_names):
                if not rfile.Get("htt_{}_{}_{}_{}/{}".format(args.channels[0],category,era.strip("Run"),fit_mode,process)):
                    print "Process {} not found for category htt_{}_{}_{}_{}. Continuing.".format(process,args.channels[0],category,era.strip("Run"),fit_mode)
                    empty_processes.append(process)
                    empty_names.append(name)
                    signal = ["TotalSig"]
	
            bkg_processes = [p for p in bkg_processes if not p in empty_processes]
            bkg_processes_names = [p for p in bkg_processes_names if not p in empty_names]
            config["files"] = [shapes]
            config["folders"] = "htt_{}_{}_{}_{}".format(args.channels[0],category,era.strip("Run"),fit_mode)
            config["lumis"] = [lumi]
            config["year"] = era.strip("Run")
            config["output_dir"] = output_dir+"/"+channel #+"/"+prefit_categories[category]
            config["y_log"] = True if ((variable in logvars) or y_log) else False
            config["x_log"] = True if x_log else False

            gof_file = "CMSSW_10_2_16_UL/src/output/gof/{era}_{channel}_{cat}/gof.json".format(era=era.strip("Run"),channel=channel,cat=category)
            p_value = -1
            if os.path.exists(gof_file):
                with open(gof_file,"r") as f:
                    gof_result = json.load(f)
                    p_value = gof_result["500.0"]["p"]


            config["subplot_legend"]  = [0.7, 0.73, 0.9, 0.98]
            config["subplot_legend_fontsize"] = 0.14
            config["y_rel_lims"] = [5, 500] if (variable in logvars) else [0., 1.8]
            config["markers"] = ["HIST"] * len(bkg_processes_names) + ["E2"]  + ["LINE"]*len(signal_names) + ["P"] + ["E2"] + ["LINE"]*len(signal_names) + ["P"]
            config["legend_markers"] = ["F"] * (len(bkg_processes_names))   + ["F"] +  ["LX0"]*len(signal_names) + ["ELP"] + ["E2"] + ["L"]*len(signal_names) + [""]
            signal_label = ['#scale[0.85]{H(%s)#rightarrowh(125)h"(%s) (0.1 pb)}'%(heavy_mass,light_mass)]
            config["labels"] = bkg_processes_names + ["Bkg.unc."] + signal_label + ["data"
                                                      ] + [""]*len(signal_names) + ["", "p={}".format(p_value)]
            if category>4:
                 config["labels"] = bkg_processes_names + ["Bkg.unc."] + signal_label + ["data"
                                                       ] + [""]*len(signal_names) + ["", ""]
            config["nicks"] = bkg_processes_names + signal_names + ["data"]
            
            config["colors"] = bkg_processes_names + ["transgrey"] + ["#8B008B"]*len(signal_names) + ["data"
                                                      ] + ["#B7B7B7"] + ["#8B008B"]*len(signal_names) + ["#000000"]
                
            config["x_expressions"] = bkg_processes+signal+["data_obs"]

            if args.emb == False:
                config["filename"] = "_".join(
                    [channel, str(category), analysis, era, variable, mass, str(heavy_mass), str(light_mass)])
            else:
                config["filename"] = "_".join(
                    [channel, str(category), analysis, era, variable, mass, str(heavy_mass), str(light_mass), "emb"])
            if args.comparison:
                config["filename"] = "_".join(
                    [channel, str(category), analysis, era, variable, mass,"comparison"]) + args.filename_prefix
            if args.ff:
                config["filename"] = config["filename"]+"_ff"
            if not args.x_label == None:
                config["x_label"] = args.x_label
            else:
                config["x_label"] = "_".join([channel, variable])
            config["filename"] = config["filename"]+"_"+fit_mode

            title_dict = {}
            title_dict["mt"] = "#mu#tau_{h}"
            title_dict["tt"] = "#tau_{h}#tau_{h}"
            title_dict["et"] = "e#tau_{h}"
            title_dict["em"] = "e#mu"

            config["title"] = "#scale[0.8]{" + title_dict[channel] + " " + prefit_categories[category].replace("NMSSM_","").replace("MH280to280_unboosted","MH280").replace("MH240to240_unboosted","MH240").replace("MH320to320_unboosted","MH320") + "}" #"_".join(["channel", channel])
            config["stacks"] = ["mc"] * len(bkg_processes_names) + signal_names + ["bkg_unc"] +[
                "data"
            ] + [x+"Ratio" for x in signal_names] + config["stacks"]
            config["ratio_denominator_nicks"] = [
                " ".join(bkg_processes_names)
            ] * (2+len(signal_names))
            config["ratio_numerator_nicks"] = [" ".join(bkg_processes_names)]
            for i in range(len(signal_names)):
                config["ratio_numerator_nicks"].append(" ".join(bkg_processes_names+[signal_names[i]]))
            config["ratio_numerator_nicks"].append("data")
            config["ratio_result_nicks"] = ["bkg_ratio"] + [x+"_ratio" for x in signal_names] + ["data_ratio"]
            config["analysis_modules"].append("AddHistograms")
            config["add_nicks"] = [" ".join(bkg_processes_names)]
            config["add_result_nicks"] = ["background_uncertainty"]
     
            if args.blind or category>4:
                for key in config.keys():
                    if isinstance(config[key], list):
                        if isinstance(config[key][0], str):
                            config[key] = [x for x in config[key] if (not "data" in x)]
                            if "marker" in key:
                                config[key] = [x for x in config[key] if (x!="P")]
                        if key in ["ratio_denominator_nicks","scale_factors","colors"]:
                            config[key] = config[key][:-1]
                #config["legend_cols"] = 1
            import pprint
            pp = pprint.PrettyPrinter(indent=2)
            pp.pprint(config)
            configs.append(config)

    higgsplot.HiggsPlotter(
        list_of_config_dicts=configs,
        list_of_args_strings=[args.additional_arguments],
        n_processes=args.num_processes)

    rfile.Close()

if __name__ == "__main__":
    args = parse_arguments()
    setup_logging("plot_nominal.log", logging.INFO)
    if not args.prefit:
        mass_dict = {
            "heavy_mass": [240, 280, 320, 360, 400, 450, 500, 550, 600, 700, 800, 900, 1000, 1200, 1400, 1600, 1800, 2000, 2500, 3000],
            "light_mass_coarse": [60, 70, 80, 90, 100, 120, 150, 170, 190, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1600, 1800, 2000, 2200, 2400, 2600, 2800],
            "light_mass_fine": [60, 70, 75, 80, 85, 90, 95, 100, 110, 120, 130, 150, 170, 190, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850],
        }
        for heavy_mass in [240,360,500,600,800,1000,1400,2000,3000]:# mass_dict["heavy_mass"]:
            light_masses = mass_dict["light_mass_coarse"] if heavy_mass > 1001 else mass_dict["light_mass_fine"]
            for light_mass in [100, max([x for x in light_masses if (x+125)<heavy_mass])]:
               if light_mass+125>heavy_mass:
                    continue
        main(args,[320,500,900],[60,100,750])
    else:
        prefit(args,500,100)
