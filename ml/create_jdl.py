#!/usr/bin/env python

from classes.JDLCreator import JDLCreator
import yaml
import argparse


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=str, help="Output path")
    parser.add_argument("--channel", required=True, type=str, help="Channel")
    parser.add_argument(
        "--modifiers", required=True, type=str, nargs="+", help="Modifier values")
    return parser.parse_args()


def main(args):
    jobs = JDLCreator("ekpsupermachines")

    jobs.executable = "ml/job.sh"
    jobs.wall_time = 10 * 60 * 60
    jobs.memory = 2048
    jobs.accounting_group = "cms.higgs"
    jobs.image = "stwunsch/slc6-condocker:smhtt"

    # Build list of arguments
    arguments = []
    for modifier in args.modifiers:
        arguments.append("{} {}".format(args.channel, modifier))
    jobs.arguments = arguments

    # The job requires lots of CPU resources
    # NOTE: This selects the sg machines.
    jobs.requirements = "(Target.ProvidesCPU == True) && (Target.ProvidesEKPResources == True)"
    jobs.job_folder = args.output
    jobs.WriteJDL()


if __name__ == "__main__":
    args = parse_arguments()
    main(args)
