import yaml
import argparse
import os
import shutil
<<<<<<< HEAD
import stat
=======
>>>>>>> started working on remote shape production
from shape_producer.estimation_methods_2016 import ggHEstimation, qqHEstimation
###
# this script is used to create split the submit of the shape
# producting into smaller chunks that can be handled by one core jobs
###


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Produce shapes for Standard Model analysis.")
<<<<<<< HEAD
    parser.add_argument("--workdir",
                        type=str,
                        help="path to the workdir",
                        default="condor_jobs/workdir")
=======
    parser.add_argument("--workdir", type=str, help="path to the workdir", default="condor_jobs/workdir")    
>>>>>>> started working on remote shape production
    parser.add_argument(
        "--channels",
        default=[],
        type=lambda channellist:
        [channel for channel in channellist.split(',')],
        help="Channels to be considered, seperated by a comma without space")
<<<<<<< HEAD
    parser.add_argument(
        "--eras",
        default=[],
        type=lambda eralist: [era for era in eralist.split(',')],
        help="Eras to be considered, seperated by a comma without space")
    parser.add_argument(
        "--mode",
        type=str,
        help="Processing mode, default is gc, options are gc, condor",
        default="gc")
=======
    parser.add_argument("--era", type=str, help="Experiment era.")
    parser.add_argument("--mode", type=str, help="Processing mode, default is gc, options are gc, condor", default="gc")
>>>>>>> started working on remote shape production
    parser.add_argument("--tag",
                        default="ERA_CHANNEL",
                        type=str,
                        help="Tag of output files.")
    return parser.parse_args()


<<<<<<< HEAD
def readclasses(channelname, era, tag):
    if args.tag == "" or args.tag is None or not os.path.isfile(
            "output/ml/{}_{}_{}/dataset_config.yaml".format(
                era, channelname, tag)):
=======
def readclasses(channelname):
    if args.tag == "" or args.tag is None or not os.path.isfile(
            "output/ml/{}_{}_{}/dataset_config.yaml".format(
                args.era, channelname, args.tag)):
>>>>>>> started working on remote shape production
        confFileName = "ml/templates/shape-producer_{}.yaml".format(
            channelname)
    else:
        confFileName = "output/ml/{}_{}_{}/dataset_config.yaml".format(
<<<<<<< HEAD
            era, channelname, tag)
=======
            args.era, channelname, args.tag)
>>>>>>> started working on remote shape production
    confdict = yaml.load(open(confFileName, "r"))
    return confdict["classes"]


def buildprocesses(channelname):
    trueTauBkgS = {"ZTT", "TTT", "VVT"}
    leptonTauBkgS = {"ZL", "TTL", "VVL"}
    jetFakeBkgS = {"ZJ", "W", "TTJ", "VVJ"}
    jetFakeBkgD = {
        "et": jetFakeBkgS,
        "mt": jetFakeBkgS,
        "tt": jetFakeBkgS,
        "em": {"W"},
    }

    ww_nicks = set()  # {"ggHWW125", "qqHWW125"}
    signal_nicks = {"WH125", "ZH125", "VH125", "ttH125"} | {
        ggH_htxs
        for ggH_htxs in ggHEstimation.htxs_dict
    } | {qqH_htxs
         for qqH_htxs in qqHEstimation.htxs_dict} | ww_nicks
    background_nicks = set(trueTauBkgS | leptonTauBkgS
                           | jetFakeBkgD[channelname] | {"EMB"} | {"FAKES"}
                           | {"QCD"}) | {"DATA"}
    processes = [[signal_nick] for signal_nick in signal_nicks]
    processes.append(list(background_nicks))
    return processes


<<<<<<< HEAD
def write_gc(era, channel, nnclasses, processes, tag, workdir):
    configfilepath = '{WORKDIR}/shapes_{ERA}_{CHANNEL}.conf'.format(
        WORKDIR=workdir, ERA=era, CHANNEL=channel)
=======
def writearguments(joblist, tag):
    filename = "condor_jobs/arguments_remote.txt"
    argfile = open(filename, 'w')
    for job in joblist:
        argfile.write("{era} {channel} {tag} {nnclass} {processes} \n".format(
            era=job["era"],
            channel=job["channel"],
            tag=tag,
            processes=(",").join(job["processes"]),
            nnclass=job["nnclass"]))
    argfile.close()

def write_gc(era, channel, nnclasses, processes, tag, workdir):
    configfilepath = os.path.abspath('{WORKDIR}/shapes_{ERA}_{CHANNEL}.conf'.format(WORKDIR=workdir, ERA=era, CHANNEL=channel))
>>>>>>> started working on remote shape production
    shutil.copy2('condor_jobs/grid_control_c7.conf', configfilepath)
    processstring = ""
    for process in processes:
        processstring += " {}".format(((",").join(process)))
    configfile = open(configfilepath, "a+")
    configfile.write("ERA = {}\n".format(era))
    configfile.write("CHANNELS = {}\n".format(channel))
    configfile.write("TAG = {}\n".format(tag))
    configfile.write("PROCESSES = {}\n".format(processstring))
    configfile.write("CATEGORIES = {}\n".format((" ").join(nnclasses)))
    configfile.write("\n")
    configfile.write("[global]\n")
    configfile.write("workdir = {}\n".format(os.path.abspath(workdir)))
    configfile.write("\n")
    configfile.write("[UserTask]\n")
    configfile.write("executable = {}\n".format(
        os.path.abspath("condor_jobs/run_remote_job.sh")))
    configfile.write("input files = {}\n".format(
        os.path.abspath("condor_jobs/gc_tarball.tar.gz")))
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


def write_while(tasks):
    out_file = open('while.sh', 'w')
    out_file.write('#!/bin/bash\n')
    out_file.write('\n')
    out_file.write('touch .lock\n')
    out_file.write('\n')
    out_file.write('while [ -f ".lock" ]\n')
    out_file.write('do\n')
    for era in tasks.keys():
        for channel in tasks[era].keys():
            out_file.write('    {}\n'.format(tasks[era][channel]["gc"]))
    out_file.write('echo "rm .lock"\n')
    out_file.write('sleep 2\n')
    out_file.write('done\n')
    out_file.close()
    os.chmod('while.sh', stat.S_IRWXU)


def main(args):
    eras = args.eras
    tag = args.tag
    channels = args.channels

    if args.mode == "submit":
        tasks = {}
        build_tarball()
        for era in eras:
            tasks[era] = {}
            for channel in channels:
                tasks[era][channel] = {}
                workdir = "{}/{}/{}".format(args.workdir, era, channel)
                print("Selected Workdir: {}".format(workdir))
                if not os.path.exists(workdir):
                    os.makedirs(workdir)
                tasks[era][channel]["gc"] = write_gc(
                    era, channel, readclasses(channel, era, tag),
                    buildprocesses(channel), tag, workdir)
        write_while(tasks)
        print("Start shape production by running ./while.sh")
        print("Sit back, get a coffee and enjoy :)")
        print("After all tasks are finished, run the merging using")
        print(
            " --> python condor_jobs/construct_remote_submit.py --workdir {workdir} --channels {channels} --eras {eras} --tag {tag} --mode merge"
            .format(workdir=args.workdir,
                    channels=",".join(args.channels),
                    eras=",".join(args.eras),
                    tag=tag))
    if args.mode == "merge":
        for era in eras:
            for channel in channels:
                workdir = "{}/{}/{}".format(args.workdir, era, channel)
                print("Merging {} {} ...".format(era, channel))
                os.system(
                    "hadd -f output/shapes/{era}-{tag}-{channel}-shapes.root {workdir}/output/*/*.root"
                    .format(era=era, tag=tag, channel=channel,
                            workdir=workdir))


if __name__ == "__main__":
    args = parse_arguments()
    main(args)
