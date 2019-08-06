#!/usr/bin/env python

from classes.JDLCreator import JDLCreator
import yaml
import argparse


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "era", type=str, help="Experiment era.")
    parser.add_argument(
        "output", type=str, help="Output path")
    parser.add_argument(
        "binning", type=str, help="Binning config.")
    parser.add_argument(
        "variables", type=str, help="Variables config.")
    return parser.parse_args()


def main(args):
    jobs = JDLCreator("docker")

    jobs.executable = "gof/job.sh"
    jobs.wall_time = 1 * 60 * 60
    jobs.memory = 2048
    jobs.accounting_group = "cms.higgs"
    jobs.image = "stwunsch/slc6-condocker:smhtt"

    # Build list of arguments
    arguments = []
    binning = yaml.load(open(args.binning), Loader=yaml.FullLoader)
    variables = yaml.load(open(args.variables))

    # 1D fits
    for channel in binning["gof"]:
        for variable in variables["variables"]:
            arguments.append("{} {} {}".format(args.era, channel, variable))

    # 2D fits
    for channel in binning["gof"]:
        selected_2d_fits = []
        for var1 in variables["selected_variables"][int(args.era)][channel]:
            for var2 in variables["selected_variables"][int(args.era)][channel]:
                selected_2d_fits.append("{}_{}".format(var1, var2))
        for variable in selected_2d_fits:
            if variable in binning["gof"][channel]:
                arguments.append("{} {} {}".format(args.era, channel, variable))

    jobs.arguments = arguments

    # The job requires lots of CPU resources
    jobs.requirements = '(Target.ProvidesCPU == True) && (Target.ProvidesEKPResources == True)'
    jobs.job_folder = args.output
    jobs.WriteJDL()


if __name__ == "__main__":
    args = parse_arguments()
    main(args)
