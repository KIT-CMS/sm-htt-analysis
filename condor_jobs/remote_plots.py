import argparse
import os
import shutil
import stat

###
# this script gernerates condor jobs for the generation of prefit/postfit plots
###


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Produce plots for Standard Model analysis.")
    parser.add_argument("--workdir",
                        type=str,
                        help="path to the workdir",
                        default="condor_jobs/plotting/workdir")
    parser.add_argument(
        "--channels",
        default=[],
        type=lambda channellist:
        [channel for channel in channellist.split(",") if channel != ""],
        help="Channels to be considered, seperated by a comma without space",
        required=True)
    parser.add_argument(
        "--eras",
        default=[],
        type=lambda eralist: [era for era in eralist.split(",") if era != ""],
        help="Eras to be considered, seperated by a comma without space",
        required=True)
    parser.add_argument(
        "--mode",
        type=str,
        help=
        "Processing mode, default is postfit , options are: [prefit, postfit]",
        default="postfit")
    parser.add_argument("--fitfile",
                        type=str,
                        help="path to the fitfile",
                        required=True)
    parser.add_argument("--datacard",
                        type=str,
                        help="path to the datacard",
                        required=True)
    parser.add_argument("--workspace",
                        type=str,
                        help="path to the workspace",
                        required=True)
    parser.add_argument("--tag", help="Tag of output files.")
    parser.add_argument(
        "--command",
        choices=['submit', 'merge', 'plot'],
        help="Command of the tool. Options are submit, merge, plot ",
    )
    return parser.parse_args()


def readclasses(channel, tag):
    if "stage0" in tag:
        signallist = ["1"]
    elif "stage1p1" in tag:
        signallist = [
            "100", "101", "102", "103", "104", "105", "106", "107", "108",
            "109", "110", "200", "201", "202", "203"
        ]
    else:
        print("Unknown Tag {}".format(tag))
        raise Exception
    if channel == "em":
        catlist = ["13", "14", "16", "19", "20"]
    elif channel == "et":
        catlist = ["13", "15", "16", "20", "21"]
    elif channel == "mt":
        catlist = ["13", "15", "16", "20", "21"]
    elif channel == "tt":
        catlist = ["16", "20", "21"]
    else:
        print("Unknown channel {}".format(channel))
        raise Exception
    return catlist + signallist


def write_gc(eras, channel, categories, tag, workdir, mode):
    configfilepath = "{WORKDIR}/plots_{MODE}_{CHANNEL}_{TAG}.conf".format(
        WORKDIR=workdir, MODE=mode, CHANNEL=channel, TAG=tag)
    shutil.copy2("condor_jobs/grid_control_cmssw_c7.conf", configfilepath)
    if "stage1p1" in tag:
        stxs = "stxs_stage1p1"
    else:
        stxs = "stxs_stage0"
    configfile = open(configfilepath, "a+")
    configfile.write("ERA = {}\n".format((" ").join(eras)))
    configfile.write("CHANNEL = {}\n".format(channel))
    configfile.write("TAG = {}\n".format(tag))
    configfile.write("CATEGORY = {}\n".format((" ").join(categories)))
    configfile.write("MODE = {} \n".format(mode))
    configfile.write("FITFILE = {} \n".format(args.fitfile))
    configfile.write("STXS_FIT = {} \n".format(stxs))
    configfile.write("SUBMITDIR = {} \n".format((os.path.abspath("."))))
    configfile.write("DATACARD = {} \n".format(args.datacard))
    configfile.write("WORKSPACE = {} \n".format(args.workspace))
    configfile.write("\n")
    configfile.write("[global]\n")
    configfile.write("workdir = {}/plots_gc_workdir\n".format(
        os.path.abspath(workdir)))
    configfile.write("\n")
    configfile.write("[CMSSW]\n")
    configfile.write("epilog executable = {} \n".format(
        os.path.abspath("condor_jobs/run_remote_plots.sh")))
    configfile.write("project area = {}\n".format(
        os.path.abspath("CMSSW_10_2_16_UL")))
    configfile.close()
    return "$go {config} -G -m 0".format(config=configfilepath)


def write_while(tasks, path):
    filename = os.path.join(path, "while_{}.sh".format(",".join(tasks.keys()),
                                                       path))
    out_file = open(filename, "w")
    out_file.write("#!/bin/bash\n")
    out_file.write("\n")
    out_file.write("touch .lock\n")
    out_file.write("go={}\n".format(
        os.path.abspath("condor_jobs/grid-control/go.py")))
    out_file.write("\n")
    out_file.write('while [ -f ".lock" ]\n')
    out_file.write("do\n")
    for tag in tasks.keys():
        for channel in tasks[tag].keys():
            out_file.write("{}\n".format(tasks[tag][channel]["gc"]))
    out_file.write('echo "rm {}/.lock"\n'.format(path))
    out_file.write("sleep 4\n")
    out_file.write("done\n")
    out_file.close()
    os.chmod(filename, stat.S_IRWXU)
    return filename


def merge_outputs(tag, mode, path):
    workdir = "{}/{}/*/{}".format(path, tag, mode)
    os.system(
        "hadd -f {PATH}/{MODE}_{TAG}_shapes_merged.root {WORKDIR}/plots_gc_workdir/output/*/*.root"
        .format(TAG=tag, MODE=mode, WORKDIR=workdir, PATH=path))
    print("merged file: {PATH}/{MODE}_{TAG}_shapes_merged.root".format(
        TAG=tag, MODE=mode, PATH=path))


def plot_shapes(tag, mode, shapefile, channels, eras):
    if "stage0" in tag:
        categories = "stxs_stage0"
        additionals = ""
    elif "stage1p1" in tag:
        categories = "stxs_stage1p1_15node"
        additionals = "--exact-signals"
    else:
        categories = "stxs_stage1p1"
        additionals = ""
    # if len(channels) == 4:
    #     channels = ["cmb"]
    returncode = 0
    for channel in channels:
        for era in eras:
            if "postfit" in args.mode:
                plotdir = "output/plots/{ERA}-{TAG}-{CHANNEL}_shape-plots_postfit".format(
                    ERA=era, TAG=tag, CHANNEL=channel)
            else:
                plotdir = "output/plots/{ERA}-{TAG}-{CHANNEL}_shape-plots_prefit".format(
                    ERA=era, TAG=tag, CHANNEL=channel)
            if not os.path.exists(plotdir):
                os.makedirs(plotdir)
            print(
                "Running ./plotting/plot_shapes_combined.py -i {FILE} -o {PLOTDIR} -c {CHANNEL} -e {ERA} --categories {CATEGORIES} --fake-factor --embedding --normalize-by-bin-width -l --train-ff True --train-emb True {ADDITIONALS}"
                .format(FILE=shapefile,
                        ERA=era,
                        CATEGORIES=categories,
                        PLOTDIR=plotdir,
                        CHANNEL=channel,
                        ADDITIONALS=additionals))
            returncode = os.system(
                "./plotting/plot_shapes_combined.py -i {FILE} -o {PLOTDIR} \
                -c {CHANNEL} -e {ERA} --categories {CATEGORIES} \
                --fake-factor --embedding --normalize-by-bin-width \
                -l --train-ff True --train-emb True {ADDITIONALS}".format(
                    FILE=shapefile,
                    ERA=era,
                    CATEGORIES=categories,
                    PLOTDIR=plotdir,
                    CHANNEL=channel,
                    ADDITIONALS=additionals))
            if (returncode != 0):
                print("Error in processing")
                print("Did you source the needed enviorement ? ")
                print(
                    ">>> source utils/setup_python.sh && source utils/setup_cvmfs_sft.sh"
                )
                break
        if (returncode != 0):
            break
        if "postfit" in args.mode:
                plotdir = "output/plots/{ERA}-{TAG}-{CHANNEL}_shape-plots_postfit".format(
                    ERA="all", TAG=tag, CHANNEL=channel)
        else:
            plotdir = "output/plots/{ERA}-{TAG}-{CHANNEL}_shape-plots_prefit".format(
                    ERA="all", TAG=tag, CHANNEL=channel)
        if not os.path.exists(plotdir):
            os.makedirs(plotdir)
        returncode = os.system(
            "./plotting/plot_shapes_combined.py -i {FILE} -o {PLOTDIR} \
            -c {CHANNEL} -e all --categories {CATEGORIES} \
            --fake-factor --embedding \
            -l --train-ff True --train-emb True {ADDITIONALS}".format(
                FILE=shapefile,
                CATEGORIES=categories,
                CHANNEL=channel,
                PLOTDIR=plotdir,
                ADDITIONALS=additionals + " --combine-backgrounds"))
    if "postfit" in args.mode:
                plotdir = "output/plots/{ERA}-{TAG}-{CHANNEL}_shape-plots_postfit".format(
                    ERA="all", TAG=tag, CHANNEL="cmb")
    else:
        plotdir = "output/plots/{ERA}-{TAG}-{CHANNEL}_shape-plots_prefit".format(
                ERA="all", TAG=tag, CHANNEL="cmb")
    if not os.path.exists(plotdir):
        os.makedirs(plotdir)
    returncode = os.system(
                "./plotting/plot_shapes_combined.py -i {FILE} -o {PLOTDIR} \
                -c cmb -e all --categories {CATEGORIES} \
                --fake-factor --embedding \
                -l --train-ff True --train-emb True {ADDITIONALS}".format(
                    FILE=shapefile,
                    CATEGORIES=categories,
                    PLOTDIR=plotdir,
                    ADDITIONALS=additionals + " --combine-backgrounds"))


def main(args):
    tag = args.tag
    eras = args.eras
    channels = args.channels
    mode = args.mode
    if args.command == "submit":
        tasks = {}
        tasks[tag] = {}
        for channel in channels:
            tasks[tag][channel] = {}
            workdir = "{}/{}/{}/{}".format(args.workdir, tag, channel, mode)
            print("Selected Workdir: {}".format(workdir))
            if not os.path.exists(workdir):
                os.makedirs(workdir)
            tasks[tag][channel]["gc"] = write_gc(eras, channel,
                                                 readclasses(channel, tag),
                                                 tag, workdir, mode)
        filename = write_while(tasks, args.workdir)
        print("Start plot production by running ./" + filename)
        print("Sit back, get a coffee and enjoy :)")

    if args.command == "merge":
        print("Merging condor output shapes")
        merge_outputs(tag, mode, args.workdir)

    if args.command == "plot":
        shapefile = "{PATH}/{MODE}_{TAG}_shapes_merged.root".format(
            TAG=tag, MODE=mode, PATH=args.workdir)
        print("plot the condor output shapes")
        print("Using")
        print("Tag: {}".format(tag))
        print("Mode: {}".format(mode))
        print("File: {}".format(shapefile))
        print("Eras: {}".format(eras))
        plot_shapes(tag, mode, shapefile, channels, eras)


if __name__ == "__main__":
    args = parse_arguments()
    main(args)
