#!/usr/bin/env python

import argparse
import yaml
import os
from multiprocessing import Pool
from subprocess import call

import logging
logger = logging.getLogger("run_application")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


def process_file(arguments):
    call(['./ml/job_application.sh {}'.format(arguments)], shell=True)


def parse_arguments():
    logger.debug("Parse arguments.")
    parser = argparse.ArgumentParser(
        description="Apply machine learning model on analysis ntuples.")
    parser.add_argument(
        "--dataset-config", required=True, help="Dataset config")
    parser.add_argument(
        "--training-config", required=True, help="Training config")
    parser.add_argument(
        "--application-config", required=True, help="Application config")
    parser.add_argument(
        "--filelist",
        required=True,
        help="Filelist with ROOT files and folders")
    parser.add_argument(
        "--num-processes",
        required=True,
        type=int,
        help="Number of processes to be spawned")
    return parser.parse_args()


def main(args):
    logger.debug("Read filelist and create bash arguments.")
    filelist = yaml.load(open(args.filelist, 'r'))
    arguments = []
    for entry in filelist:
        file_ = entry
        folders = ""
        for folder in filelist[entry]:
            folders += "{} ".format(folder)
        folders = folders.strip()
        arguments.append(
            "{DATASET_CONFIG} {TRAINING_CONFIG} {APPLICATION_CONFIG} {FILE} {FOLDERS}".
            format(
                DATASET_CONFIG=args.dataset_config,
                TRAINING_CONFIG=args.training_config,
                APPLICATION_CONFIG=args.application_config,
                FILE=file_,
                FOLDERS=folders))

    logger.debug("Run jobs with %s processes.", args.num_processes)
    pool = Pool(args.num_processes)
    pool.map(process_file, arguments)
    pool.close()
    pool.join()

    logger.info("Done.")


if __name__ == "__main__":
    args = parse_arguments()
    main(args)
