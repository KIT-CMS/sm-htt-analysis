import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True  # disable ROOT internal argument parser

import argparse
import os
import multiprocessing

import logging
logger = logging.getLogger("")


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
        description="Convert shapes from the shape producer to the sync format."
    )
    parser.add_argument("--era", required=True, type=str, help="Analysis era")
    parser.add_argument("--input", required=True, type=str, help="Path to single input ROOT file.")
    parser.add_argument("--output", required=True, type=str, help="Path to output directory")
    parser.add_argument("--tag", required=False, type=str, help="Name to add to the output filename")
    parser.add_argument("-n", "--num-processes", default=6, type=int, help="Number of processes used.")
    return parser.parse_args()


def correct_nominal_shape(hist, name, integral):
    if integral >= 0:
         # if integral is larger than 0, everything is fine
        sf = 1.0
    elif integral == 0.0:
        logger.info("Nominal histogram is empty: {}".format(name))
        # if integral of nominal is 0, we make sure to scale the histogram with 0.0
        sf = 0
    else:
        logger.info("Nominal histogram is negative : {} --> fixing it now...".format(name))
        # if the histogram is negative, the make all negative bins positive,
        # and scale the histogram to a small positive value
        for i in range(hist.GetNbinsX()):
            if hist.GetBinContent(i+1)<0.0:
                logger.info("Negative Bin {} - {}".format(i, hist.GetBinContent(i+1)))
                hist.SetBinContent(i+1, 0.001)
                logger.info("After fixing: {} - {}".format(i, hist.GetBinContent(i+1)))
        sf = 0.001 / hist.Integral()
    hist.Scale(sf)
    return hist

def write_shapes_per_category(config: tuple):
    category, keys, channel, ofname, ifname = config
    infile = ROOT.TFile(ifname, "READ")
    dir_name = "{CHANNEL}_{CATEGORY}".format(
            CHANNEL=channel, CATEGORY=category)
    outfile = ROOT.TFile(ofname.replace(".root", "-" + category + ".root"), "RECREATE")
    logger.info("Starting {} with {}".format(dir_name, outfile))
    outfile.cd()
    outfile.mkdir(dir_name)
    outfile.cd(dir_name)
    for name in sorted(keys):
        hist = infile.Get(name)
        pos = 0.0
        neg = 0.0
        if "_xxh#bb" in name or ("_xxh#gg" in name and not "_i_" in name):
            integral = hist.Integral()
            if name.split("#")[-1]=="":
                nominal = correct_nominal_shape(hist, name, integral)
            # if the integral of the shape is negative, set it to the corrected nominal shape
            elif integral <= 0.0:
                    hist = nominal
            else:
                for i in range(hist.GetNbinsX()):
                    cont = hist.GetBinContent(i+1)
                    if cont<0.0:
                        neg += cont
                        hist.SetBinContent(i+1, 0.0)
                    else:
                        pos += cont
                if neg<0:
                    if (neg+pos)>0.0:
                        hist.Scale((neg+pos)/pos)
        elif "_xxh#gg" in name and "_i_" in name:
            print("Not doing andthing for interference ggH shapes ...: {}".format(name))
        else:
            for i in range(hist.GetNbinsX()):
                cont = hist.GetBinContent(i+1)
                if cont<0.0:
                    neg += cont
                    hist.SetBinContent(i+1, 0.0)
                else:
                    pos += cont
            if neg<0:
                if neg+pos>0.0:
                    hist.Scale((neg+pos)/pos)
                else:
                    hist.Scale(0.0)
                if name.split("#")[-1]=="":
                    logger.info("Found histogram with negative bin: " + name)
                    logger.info("Negative yield: %f"%neg)
                    logger.info("Total yield: %f"%(neg+pos))
                if neg<-100.0:
                    if (not "#QCD#" in name) or ("#em_" in name) or (not "#ggA_" in name): # in case of QCD in et, mt, tt be a bit more generous since this is only for cross checks
                        logger.info("LAAARGE: " + name)
                        logger.info("Negative yield: %f"%neg)
                        logger.info("Total yield: %f"%(neg+pos))
                        logger.fatal("Found histogram with a yield of negative bins larger than 1.0!")
                        #raise Exception

        if (not "ZTTpTTTauTau" in name) and ("CMS_htt_emb_ttbar" in name):
            continue
        name_output = keys[name]
        if "ZTTpTTTauTauUp" in name_output:
            name_output = name_output.replace("ZTTpTTTauTauUp","EMB")
        if "ZTTpTTTauTauDown" in name_output:
            name_output = name_output.replace("ZTTpTTTauTauDown","EMB")
        hist.SetTitle(name_output)
        hist.SetName(name_output)
        hist.Write()
        if "201" in name_output:
            if ("scale_t_" in name_output
                    or "prefiring" in name_output
                    or "scale_e_" in name_output
                    or "res_e_" in name_output
                    or "scale_t_" in name_output
                    or "scale_t_emb_" in name_output
                    or "boson_res_met_" in name_output
                    or "boson_scale_met_" in name_output
                    or "_1ProngPi0Eff_" in name_output
                    or "_3ProngEff_" in name_output
                    or ("_ff_" in name_output and "_syst_" in name_output)):
                hist.SetTitle(name_output.replace("_2016", "").replace("_2017", "").replace("_2018", ""))
                hist.SetName(name_output.replace("_2016", "").replace("_2017", "").replace("_2018", ""))
                hist.Write()
    outfile.Close()


def main(args):
    # Open input ROOT file and output ROOT file
    file_input = ROOT.TFile(args.input)

    # Loop over shapes of input ROOT file and create map of input/output names
    hist_map = {}
    for key in file_input.GetListOfKeys():
        if key.GetName() == "output_tree":
            continue
        # Read name and extract shape properties
        name = key.GetName()
        properties = [x for x in name.split("#") if not x == ""]

        # Get category name (and remove CHANNEL_ from category name)
        category = properties[1].replace(properties[0] + "_", "", 1)
        # we dont need these categories in the synced shapes
        if (category.endswith("_ss")
            or category.endswith("_B")
            or category.endswith("_FF")
            or category.endswith("qqh")
            or category.endswith("ggh")):
            continue
        # Get other properties
        channel = properties[0]
        process = properties[2]

        # Check that in the mapping of the names the channel and category is existent
        if not channel in hist_map:
            hist_map[channel] = {}
        if not category in hist_map[channel]:
            hist_map[channel][category] = {}

        # Push name of histogram to dict
        if not len(properties) in [7, 8]:
            logger.critical(
                "Shape {} has an unexpected number of properties.".format(
                    name))
            raise Exception
        name_output = "{PROCESS}".format(PROCESS=process)
        # convert jetFakes to jetFakesSM naming to destinguish between SM and MSSM FFs
        if ("jetFakes" in name_output):
            name_output = name_output.replace("jetFakes", "jetFakesSM")
        if len(properties) == 8:
            systematic = properties[7]
            # convert jetFakes to jetFakesSM naming to destinguish between SM and MSSM FFs
            if ("jetFakes" in name_output):
                systematic = systematic.replace("CMS_ff_", "CMS_ffSM_")
            # temp rename trigger uncertainties to xtrigger_t in tautau channel
            if ("eff_trigger" in systematic and channel == "tt"):
                systematic = systematic.replace("CMS_eff_trigger", "CMS_eff_xtrigger_t")
            # convert REWEIGHT Systematics to correct naming
            if ("REWEIGHT" in systematic and "Hdamp" in systematic):
                sys_old = systematic
                if("RREWEIGHT" in systematic):
                    systematic = systematic.replace("RREWEIGHT","REWEIGHT")
                systematic = systematic.replace("ggh","ggH")
                print("Changed {} to {}".format(sys_old, systematic))

            name_output += "_" + systematic
        hist_map[channel][category][name] = name_output
    # Clean-up
    file_input.Close()

    # Loop over map once and create respective output files
    for channel in hist_map:
        if args.tag in [None, ""]:
            filename_output = os.path.join(
                args.output,
                "{ERA}-{CHANNELS}-synced-ML.root").format(CHANNELS=channel, ERA=args.era)
        else:
            filename_output = os.path.join(
                args.output,
                "{ERA}-{TAG}-{CHANNELS}-synced-ML.root").format(CHANNELS=channel, TAG=args.tag, ERA=args.era)
        if not os.path.exists(args.output):
            os.mkdir(args.output)
        logger.info("Running shape sync for {} categories in channel {} - {}".format(len(hist_map[channel].items()), channel, args.era))
        with multiprocessing.Pool(min(args.num_processes, len(hist_map[channel].items()))) as pool:
            pool.map(write_shapes_per_category,
                     [(*item, channel, filename_output, args.input) for item in sorted(hist_map[channel].items())])





if __name__ == "__main__":
    args = parse_arguments()
    setup_logging("convert_synced_shapes.log", logging.DEBUG)
    main(args)
