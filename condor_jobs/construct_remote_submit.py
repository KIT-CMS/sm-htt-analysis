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
        description="Produce shapes for Standard Model analysis.")
    parser.add_argument("--workdir",
                        type=str,
                        help="path to the workdir",
                        default="condor_jobs/workdir")
    parser.add_argument(
        "--channels",
        default=[],
        type=lambda channellist:
        [channel for channel in channellist.split(',')],
        help="Channels to be considered, seperated by a comma without space")
    parser.add_argument(
        "--eras",
        default=[],
        type=lambda eralist: [era for era in eralist.split(',')],
        help="Eras to be considered, seperated by a comma without space")
    parser.add_argument(
        "--mode",
        type=str,
        help=
        "Processing mode, default is submit , options are: [submit, merge]",
        default="submit")
    parser.add_argument(
        "--gcmode",
        type=str,
        help=
        "Processing mode for grid-control, default is normal, options are: [normal, optimal]",
        default="normal")
    parser.add_argument("--tag",
                        default="ERA_CHANNEL",
                        type=str,
                        help="Tag of output files.")
    return parser.parse_args()


def readclasses(channelname, era, tag):
    if args.tag == "" or args.tag is None or not os.path.isfile(
            "output/ml/{}_{}_{}/dataset_config.yaml".format(
                era, channelname, tag)):
        confFileName = "ml/templates/shape-producer_{}.yaml".format(
            channelname)
    else:
        confFileName = "output/ml/{}_{}_{}/dataset_config.yaml".format(
            era, channelname, tag)
    confdict = yaml.load(open(confFileName, "r"))
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

    ww_nicks = {"ggHWW125", "qqHWW125"}
    # tmp fix, remove for eoy ntuples
    if era not in ["2016", "2017"]: ww_nicks = set()

    signal_nicks = {"WH125", "ZH125", "VH125", "ttH125"} | {
        ggH_htxs
        for ggH_htxs in ggHEstimation.htxs_dict
    } | {qqH_htxs
         for qqH_htxs in qqHEstimation.htxs_dict} | ww_nicks
    background_nicks = set(trueTauBkgS | leptonTauBkgS
                           | jetFakeBkgD[channelname] | {"EMB"} | {"FAKES"}
                           | {"QCD"}) | {"data_obs"}
    processes = [[signal_nick] for signal_nick in signal_nicks]
    processes.append(list(background_nicks))
    # this way, background shapes are processed first
    return processes[::-1]


def write_gc(era, channel, nnclasses, processes, tag, workdir, mode):
    if mode == "normal":
        configfilepath = '{WORKDIR}/shapes_{ERA}_{CHANNEL}.conf'.format(
            WORKDIR=workdir, ERA=era, CHANNEL=channel)
        shutil.copy2('condor_jobs/grid_control_c7.conf', configfilepath)
        processstring = ""
        for process in processes:
            processstring += " {}".format(((",").join(process)))

    elif mode == "bkg":
        configfilepath = '{WORKDIR}/shapes_{ERA}_{CHANNEL}_bkg.conf'.format(
            WORKDIR=workdir, ERA=era, CHANNEL=channel)
        shutil.copy2('condor_jobs/grid_control_c7.conf', configfilepath)
        processstring = ",".join(processes)
    configfile = open(configfilepath, "a+")
    configfile.write("ERA = {}\n".format(era))
    configfile.write("CHANNELS = {}\n".format(channel))
    configfile.write("TAG = {}\n".format(tag))
    configfile.write("PROCESSES = {}\n".format(processstring))
    configfile.write("CATEGORIES = {}\n".format((" ").join(nnclasses)))
    if mode == "normal":
        configfile.write("NCPUS = 1\n")
    elif mode == "bkg":
        configfile.write("NCPUS = 8\n")
    configfile.write("\n")
    configfile.write("[global]\n")
    if mode == "normal":
        configfile.write("workdir = {}/gc_workdir\n".format(
            os.path.abspath(workdir)))
    elif mode == "bkg":
        configfile.write("workdir = {}/bkg_gc_workdir\n".format(
            os.path.abspath(workdir)))
    configfile.write("\n")
    configfile.write("[UserTask]\n")
    configfile.write("executable = {}\n".format(
        os.path.abspath("condor_jobs/run_remote_job.sh")))
    configfile.write("input files = {}\n".format(
        os.path.abspath("condor_jobs/gc_tarball.tar.gz")))
    if mode == "normal":
        # configfile.write("constant = CPUS \n CPUS = 1\n")
        configfile.write("\n[jobs]\n")
        configfile.write("cpus = 1\n")
    elif mode == "bkg":
        # configfile.write("constant = CPUS \nCPUS = 8\n")
        configfile.write("\n[jobs]\n")
        configfile.write("cpus = 8\n")
    configfile.close()
    return "{go} {config} -G -m 5".format(
        go=os.path.abspath("condor_jobs/grid-control/go.py"),
        config=configfilepath)


def build_tarball():
    print("building tarball...")
    os.system(
        "tar -czf condor_jobs/gc_tarball.tar.gz shape-producer shapes utils datasets ml fake-factor-application utils"
    )
    print("finished tarball...")


def write_while(tasks, tag):
    out_file = open('while_{}.sh'.format(tag), 'w')
    out_file.write('#!/bin/bash\n')
    out_file.write('\n')
    out_file.write('touch .lock\n')
    out_file.write('\n')
    out_file.write('while [ -f ".lock" ]\n')
    out_file.write('do\n')
    for era in tasks.keys():
        for channel in tasks[era].keys():
            out_file.write('{}\n'.format(tasks[era][channel]["gc"]))
    out_file.write('echo "rm .lock"\n')
    out_file.write('sleep 2\n')
    out_file.write('done\n')
    out_file.close()
    os.chmod('while_{}.sh'.format(tag), stat.S_IRWXU)


def main(args):
    eras = args.eras
    tag = args.tag
    channels = args.channels
    gcmode = args.gcmode

    if args.mode == "submit":
        tasks = {}
        build_tarball()
        for era in eras:
            tasks[era] = {}
            for channel in channels:
                tasks[era][channel] = {}
                workdir = "{}/{}/{}/{}".format(args.workdir, tag, era, channel)
                print("Selected Workdir: {}".format(workdir))
                if not os.path.exists(workdir):
                    os.makedirs(workdir)
                if gcmode == 'normal':
                    tasks[era][channel]["gc"] = write_gc(
                        era, channel, readclasses(channel, era, tag),
                        buildprocesses(era, channel), tag, workdir, 'normal')
                if gcmode == 'optimal':
                    # In this case, we submit backgorunds seperately using 8 cores instead of one
                    del tasks[era][channel]
                    tasks[era][channel + "_bkg"] = {}
                    tasks[era][channel + "_signal"] = {}
                    tasks[era][channel + "_bkg"]["gc"] = write_gc(
                        era, channel, readclasses(channel, era, tag),
                        buildprocesses(era, channel)[0], tag, workdir, 'bkg')
                    tasks[era][channel + "_signal"]["gc"] = write_gc(
                        era, channel, readclasses(channel, era, tag),
                        buildprocesses(era, channel)[1:], tag, workdir,
                        'normal')
        write_while(tasks, tag)
        print("Start shape production by running ./while_{}.sh".format(tag))
        print("Sit back, get a coffee and enjoy :)")
        print("After all tasks are finished, run the merging using")
        print(" --> mergeBatchShapes")
    if args.mode == "merge":
        for era in eras:
            for channel in channels:

                workdir = "{}/{}/{}/{}".format(args.workdir, tag, era, channel)
                print("Merging {} {} ...".format(era, channel))
                if gcmode == "normal":
                    os.system(
                        "hadd -f output/shapes/{era}-{tag}-{channel}-shapes.root {workdir}/gc_workdir/output/*/*.root"
                        .format(era=era,
                                tag=tag,
                                channel=channel,
                                workdir=workdir))
                elif gcmode == "optimal":
                    os.system(
                        "hadd -f output/shapes/{era}-{tag}-{channel}-shapes.root {workdir}/gc_workdir/output/*/*.root {workdir}/bkg_gc_workdir/output/*/*.root"
                        .format(era=era,
                                tag=tag,
                                channel=channel,
                                workdir=workdir))


if __name__ == "__main__":
    args = parse_arguments()
    main(args)
