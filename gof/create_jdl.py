#!/usr/bin/env python

from classes.JDLCreator import JDLCreator
import yaml
import argparse
import os


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
    jobs.wall_time = 12 * 60 * 60
    jobs.memory = 4096
    jobs.accounting_group = "cms.higgs"
    jobs.image = "mschnepf/slc7-condocker"

    # Build list of arguments
    arguments = []
    binning = yaml.load(open(args.binning))
    variables = yaml.load(open(args.variables))

    # 1D fits
    for channel in binning["gof"]:
        for variable in variables["selected_variables"][int(args.era)][channel]:
            arguments.append("{} {} {} {}".format(args.era, channel, variable, os.getcwd()))

    # 2D fits
    for channel in binning["gof"]:
        selected_2d_fits = []
        for var1 in variables["selected_variables"][int(args.era)][channel]:
            for var2 in variables["selected_variables"][int(args.era)][channel]:
                selected_2d_fits.append("{}_{}".format(var1, var2))
        for variable in selected_2d_fits:
            if variable in binning["gof"][channel]:
                arguments.append("{} {} {} {}".format(args.era, channel, variable, os.getcwd()))

    jobs.arguments = arguments

    # The job requires lots of CPU resources
    jobs.requirements = '(Target.ProvidesCPU == True) && (Target.ProvidesIO == True ) && (Target.ProvidesEKPResources == True)'
    jobs.job_folder = args.output
    jobs.WriteJDL()


if __name__ == "__main__":
    args = parse_arguments()
    main(args)
