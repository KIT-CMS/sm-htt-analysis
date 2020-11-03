import yaml
import argparse
import os
import shutil
import stat
from shape_producer.estimation_methods_2016 import ggHEstimation, qqHEstimation

###
# this script is used to create split the submit of the shape
# producting into smaller chunks that can be handled by one core jobs
###


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Produce shapes for Standard Model analysis."
    )
    parser.add_argument(
        "--workdir", type=str, help="path to the workdir", default="condor_jobs/workdir"
    )
    parser.add_argument(
        "--channels",
        default=[],
        type=lambda channellist: [
            channel for channel in channellist.split(",") if channel != ""
        ],
        help="Channels to be considered, seperated by a comma without space",
    )
    parser.add_argument(
        "--eras",
        default=[],
        type=lambda eralist: [era for era in eralist.split(",") if era != ""],
        help="Eras to be considered, seperated by a comma without space",
    )
    parser.add_argument(
        "--mode",
        type=str,
        help="Processing mode, default is submit , options are: [submit, merge]",
        default="submit",
    )
    parser.add_argument(
        "--gcmode",
        type=str,
        help="Processing mode for grid-control, default is normal, options are: [normal, optimal]",
        default="normal",
    )
    parser.add_argument(
        "--tags",
        default=["default"],
        type=lambda taglist: [tag for tag in taglist.split(",") if tag != ""],
        help="Tag of output files.",
    )
    return parser.parse_args()


def readclasses(channelname, era, tag):
    if not os.path.isfile(
        "output/ml/{}_{}_{}/dataset_config.yaml".format(era, channelname, tag)
    ):
        confFileName = "ml/templates/shape-producer_{}.yaml".format(channelname)
    else:
        confFileName = "output/ml/{}_{}_{}/dataset_config.yaml".format(
            era, channelname, tag
        )
    confdict = yaml.load(open(confFileName, "r"))
    # for stage0, combine ggh and qqh in one job for 2D binning
    if "ggh" in confdict["classes"] and "qqh" in confdict["classes"]:
        confdict["classes"].remove("ggh")
        confdict["classes"].remove("qqh")
        confdict["classes"].append("ggh,qqh")
    return confdict["classes"]


def buildprocesses(era, channelname):
    trueTauBkgS = {"ZTT", "TTT", "VVT"}
    leptonTauBkgS = {"ZL", "TTL", "VVL"}
    jetFakeBkgS = {"ZJ", "W", "TTJ", "VVJ"}
    jetFakeBkgD = {
        "et": jetFakeBkgS,
        "mt": jetFakeBkgS,
        "tt": jetFakeBkgS,
        "em": {"W"},
    }

    ww_nicks = {"ggHWW125", "qqHWW125", "WHWW125", "ZHWW125"}

    signal_nicks = (
        {"WH125", "ZH125", "VH125", "ttH125"}
        | {ggH_htxs for ggH_htxs in ggHEstimation.htxs_dict}
        | {qqH_htxs for qqH_htxs in qqHEstimation.htxs_dict}
        | ww_nicks
    )
        # add SUSY signals:
    mass_dict = {
        "2016": {
            "ggH": [80, 90, 100, 110, 120, 130, 140, 160, 180, 200, 250, 300, 350, 400, 450, 500, 600, 700, 800, 900, 1000, 1200, 1400, 1500, 1600, 1800, 2000, 2300, 2600, 2900, 3200],
            "bbH_nlo": [80, 90, 110, 120, 130, 140, 160, 180, 200, 250, 350, 400, 450, 500, 600, 700, 800, 900, 1000, 1200, 1400, 1600, 1800, 2000, 2300, 2600, 2900, 3200],
        },
        "2017": {
            "ggH": [80, 90, 100, 110, 120, 130, 140, 180, 200, 250, 300, 350, 400, 450, 600, 700, 800, 900, 1200, 1400, 1500, 1600, 1800, 2000, 2300, 2600, 2900, 3200],
            "bbH_nlo": [80, 90, 110, 120, 125, 130, 140, 160, 180, 200, 250, 300, 350, 400, 450, 500, 600, 700, 800, 900, 1000, 1200, 1400, 1600, 1800, 2000, 2300, 2600, 2900, 3200, 3500],
        },
        "2018": {
            "ggH": [80, 90, 100, 110, 120, 130, 140, 160, 180, 200, 250, 300, 350, 400, 450, 600, 700, 800, 900, 1200, 1400, 1500, 1600, 1800, 2000, 2300, 2600, 2900, 3200],
            "bbH_nlo": [80, 90, 100, 110, 120, 125, 130, 140, 160, 180, 200, 250, 300, 350, 400, 450, 500, 600, 700, 800, 900, 1000, 1200, 1400, 1600, 1800, 2000, 2300, 2600, 2900, 3200, 3500],
        }
    }

    susyggH_masses = mass_dict[era]["ggH"]
    susybbH_masses = mass_dict[era]["bbH_nlo"]
    # mssm ggH and bbH signals
    for ggH_contribution in ["ggh_t", "ggh_b", "ggh_i", "ggH_t", "ggH_b", "ggH_i", "ggA_t", "ggA_b", "ggA_i"]:
        for mass in susyggH_masses:
            name = ggH_contribution + "_" + str(mass)
            signal_nicks.add(name)
    for m in susybbH_masses:
        name = "bbH_" + str(m)
        signal_nicks.add(name)
    print len(signal_nicks)
    background_nicks = set(
        trueTauBkgS
        | leptonTauBkgS
        | jetFakeBkgD[channelname]
        | {"EMB"}
        | {"FAKES"}
        | {"QCD"}
    ) | {"data_obs"}
    processes = [[signal_nick] for signal_nick in signal_nicks]
    processes.append(list(background_nicks))
    # this way, background shapes are processed first
    return processes[::-1]


def write_gc(era, channel, nnclasses, processes, tag, workdir,tarballpath, mode):
    if mode == "normal":
        configfilepath = "{WORKDIR}/shapes_{ERA}_{CHANNEL}_{TAG}.conf".format(
            WORKDIR=workdir, ERA=era, CHANNEL=channel, TAG=tag
        )
        shutil.copy2("condor_jobs/grid_control_c7.conf", configfilepath)
        processstring = ""
        for process in processes:
            processstring += " {}".format(((",").join(process)))

    elif mode == "bkg":
        configfilepath = "{WORKDIR}/shapes_{ERA}_{CHANNEL}_{TAG}_bkg.conf".format(
            WORKDIR=workdir, ERA=era, CHANNEL=channel, TAG=tag
        )
        shutil.copy2("condor_jobs/grid_control_c7.conf", configfilepath)
        processstring = ",".join(processes)
    configfile = open(configfilepath, "a+")
    configfile.write("ERA = {}\n".format(era))
    configfile.write("CHANNELS = {}\n".format(channel))
    configfile.write("TAG = {}\n".format(tag))
    configfile.write("PROCESSES = {}\n".format(processstring))
    if os.path.isdir("output/friend_trees"):
        friend_input_mount = os.popen("cd output; pwd -P").read().strip("\n")
        configfile.write("FRIEND_INPUT_MOUNT = {}\n".format(friend_input_mount))
    configfile.write("CATEGORIES = {}\n".format((" ").join(nnclasses)))
    if mode == "normal":
        configfile.write("NCPUS = 1\n")
    elif mode == "bkg":
        configfile.write("NCPUS = 8\n")
    configfile.write("\n")
    configfile.write("[global]\n")
    if mode == "normal":
        configfile.write("workdir = {}/gc_workdir\n".format(os.path.abspath(workdir)))
    elif mode == "bkg":
        configfile.write(
            "workdir = {}/bkg_gc_workdir\n".format(os.path.abspath(workdir))
        )
    configfile.write("\n")
    configfile.write("[UserTask]\n")
    configfile.write(
        "executable = {}\n".format(os.path.abspath("condor_jobs/run_remote_job.sh"))
    )
    configfile.write(
        "input files = {}\n".format(os.path.abspath(tarballpath))
    )
    if mode == "normal":
        # configfile.write("constant = CPUS \n CPUS = 1\n")
        configfile.write("\n[jobs]\n")
        configfile.write("cpus = 1\n")
    elif mode == "bkg":
        # configfile.write("constant = CPUS \nCPUS = 8\n")
        configfile.write("\n[jobs]\n")
        configfile.write("cpus = 8\n")
    configfile.close()
    return "$go {config} -G -m 0".format(config=configfilepath)


def build_tarball(workdir):
    print("building tarball...")
    cmd = "tar --dereference -czf {}/gc_tarball.tar.gz shape-producer/* shapes/* utils/* datasets/* ml/* fake-factor-application/* utils/* output/ml/*/dataset_config.yaml".format(
        workdir
    )
    print(cmd)
    os.system(cmd)
    print("finished tarball...")
    return("{}/gc_tarball.tar.gz ".format(workdir))


def write_while(tasks, path):
    filename = os.path.join(path, "while_{}.sh".format(",".join(tasks.keys()), path))
    out_file = open(filename, "w")
    out_file.write("#!/bin/bash\n")
    out_file.write("\n")
    out_file.write("touch .lock\n")
    out_file.write("go={}\n".format(os.path.abspath("condor_jobs/grid-control/go.py")))
    out_file.write("\n")
    out_file.write('while [ -f ".lock" ]\n')
    out_file.write("do\n")
    for tag in tasks.keys():
        for era in tasks[tag].keys():
            for channel in tasks[tag][era].keys():
                out_file.write("{}\n".format(tasks[tag][era][channel]["gc"]))
    out_file.write('echo "rm {}/.lock"\n'.format(path))
    out_file.write("sleep 4\n")
    out_file.write("done\n")
    out_file.close()
    os.chmod(filename, stat.S_IRWXU)
    return filename


def main(args):
    tags = args.tags
    eras = args.eras
    channels = args.channels
    gcmode = args.gcmode

    if args.mode == "submit":
        tasks = {}
        tarballpath=build_tarball(args.workdir)
        for tag in tags:
            tasks[tag] = {}
            for era in eras:
                tasks[tag][era] = {}
                for channel in channels:
                    tasks[tag][era][channel] = {}
                    workdir = "{}/{}/{}/{}".format(args.workdir, tag, era, channel)
                    print("Selected Workdir: {}".format(workdir))
                    if not os.path.exists(workdir):
                        os.makedirs(workdir)
                    if gcmode == "normal":
                        tasks[tag][era][channel]["gc"] = write_gc(
                            era,
                            channel,
                            readclasses(channel, era, tag),
                            buildprocesses(era, channel),
                            tag,
                            workdir,
                            tarballpath,
                            "normal",
                        )
                    if gcmode == "optimal":
                        # In this case, we submit backgorunds seperately using 8 cores instead of one
                        del tasks[tag][era][channel]
                        tasks[tag][era][channel + "_bkg"] = {}
                        tasks[tag][era][channel + "_signal"] = {}
                        tasks[tag][era][channel + "_bkg"]["gc"] = write_gc(
                            era,
                            channel,
                            readclasses(channel, era, tag),
                            buildprocesses(era, channel)[0],
                            tag,
                            workdir,
                            tarballpath,
                            "bkg",
                        )
                        tasks[tag][era][channel + "_signal"]["gc"] = write_gc(
                            era,
                            channel,
                            readclasses(channel, era, tag),
                            buildprocesses(era, channel)[1:],
                            tag,
                            workdir,
                            tarballpath,
                            "normal",
                        )
        filename = write_while(tasks, args.workdir)
        print("Start shape production by running ./" + filename)
        print("Sit back, get a coffee and enjoy :)")
        print("After all tasks are finished, run the merging using")
        print(" --> mergeBatchShapes")
    if args.mode == "merge":
        for tag in tags:
            for era in eras:
                for channel in channels:
                    workdir = "{}/{}/{}/{}".format(args.workdir, tag, era, channel)
                    print("Merging {} {} ...".format(era, channel))
                    if not os.path.isdir("output/shapes/" + tag):
                        os.system("mkdir output/shapes/" + tag)
                    if gcmode == "normal":
                        os.system(
                            "hadd -f output/shapes/{tag}/{era}-{tag}-{channel}-shapes.root {workdir}/gc_workdir/output/*/*.root".format(
                                era=era, tag=tag, channel=channel, workdir=workdir
                            )
                        )
                    elif gcmode == "optimal":
                        os.system(
                            "hadd -f output/shapes/{tag}/{era}-{tag}-{channel}-shapes.root {workdir}/gc_workdir/output/*/*.root {workdir}/bkg_gc_workdir/output/*/*.root".format(
                                era=era, tag=tag, channel=channel, workdir=workdir
                            )
                        )


if __name__ == "__main__":
    args = parse_arguments()
    main(args)
