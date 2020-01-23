import yaml
import argparse
import os
import shutil
from shape_producer.estimation_methods_2016 import ggHEstimation, qqHEstimation
###
# this script is used to create split the submit of the shape
# producting into smaller chunks that can be handled by one core jobs
###


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Produce shapes for Standard Model analysis.")
    parser.add_argument("--workdir", type=str, help="path to the workdir", default="condor_jobs/workdir")    
    parser.add_argument(
        "--channels",
        default=[],
        type=lambda channellist:
        [channel for channel in channellist.split(',')],
        help="Channels to be considered, seperated by a comma without space")
    parser.add_argument("--era", type=str, help="Experiment era.")
    parser.add_argument("--mode", type=str, help="Processing mode, default is gc, options are gc, condor", default="gc")
    parser.add_argument("--tag",
                        default="ERA_CHANNEL",
                        type=str,
                        help="Tag of output files.")
    return parser.parse_args()


def readclasses(channelname):
    if args.tag == "" or args.tag is None or not os.path.isfile(
            "output/ml/{}_{}_{}/dataset_config.yaml".format(
                args.era, channelname, args.tag)):
        confFileName = "ml/templates/shape-producer_{}.yaml".format(
            channelname)
    else:
        confFileName = "output/ml/{}_{}_{}/dataset_config.yaml".format(
            args.era, channelname, args.tag)
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
    configfile.write("workdir = {}".format(workdir))
    configfile.write("\n")
    configfile.write("[UserTask]\n")
    configfile.write("executable = {}\n".format(os.path.abspath("condor_jobs/run_remote_job.sh")))
    configfile.write("input files = {}\n".format(os.path.abspath("condor_jobs/gc_tarball.tar.gz")))
    configfile.close()
    return "go.py {}".format(configfilepath)

def build_tarball():
    print("building tarball...")
    os.system("tar -czf condor_jobs/gc_tarball.tar.gz shape-producer shapes utils datasets ml fake-factor-application utils")
    print("finished tarball...")
# def collect_outputs(joblist, tag):
#     path = "output/shapes/{TAG}/{ERA}/{CHANNEL}/{ERA}-{TAG}-{CHANNEL}-{PROCESS}-{CATEGORIES}-shapes.root".format(
#         era=job["era"],
#         channel=job["channel"],
#         tag=tag,
#         processes=(",").join(job["processes"]),
#         nnclass=job["nnclass"])
#     )


def main(args):
    era = args.era
    tag = args.tag
    channels = args.channels

    if args.mode == "gc":
        tasks = {}
        build_tarball()
        for channel in channels:
            tasks[channel] = {}
            workdir = "{}/{}/{}".format(args.workdir, era, channel)
            print("Selected Workdir: {}".format(workdir))
            if not os.path.exists(workdir):
                os.makedirs(workdir)
            tasks[channel]["gc"] = write_gc(era, channel, readclasses(channel), buildprocesses(channel), tag, workdir)
            tasks[channel]["workdir"] = workdir
            

    elif args.mode == "condor":
        jobs = []
        for channel in channels:
            for nnclass in readclasses(channel):
                for processes in buildprocesses(channel):
                    jobs.append({
                        "era": era,
                        "channel": channel,
                        "processes": processes,
                        "nnclass": nnclass
                    })
        writearguments(jobs, tag)
        os.system("source utils/bashFunctionCollection.sh && ensureoutdirs")
        os.system("./condor_jobs/submit_remote.sh")
    else:
        raise NameError('Type of submit is not known')

if __name__ == "__main__":
    args = parse_arguments()
    main(args)
