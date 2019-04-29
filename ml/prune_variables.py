#!/usr/bin/env python

import logging
logger = logging.getLogger("prune_variables")

import argparse
import yaml
import os
from collections import OrderedDict

def parse_arguments():
    logger.debug("Parse arguments.")
    parser = argparse.ArgumentParser(
        description="Add variables after each training run in order of taylor coefficients.")
    parser.add_argument("config_train", help="Path to training config file")
    #parser.add_argument("taylor_coefficients", help="Path to file with ordered 1D taylor coefficients.")
    return parser.parse_args()


def parse_config(filename):
    logger.debug("Parse config.")
    return yaml.load(open(filename, "r"))

def parse_txt(filename):
    logger.debug("Parse text-file")
    taylor_coefficients = OrderedDict()
    with open(filename, "r") as f:
        for line in f:
            line = line.split(":")
            key = line[1].strip()
            value = line[2].strip()
            taylor_coefficients[key] = float(value)
    return taylor_coefficients


def setup_logging(level, output_file=None):
    logger.setLevel(level)
    formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    if not output_file == None:
        file_handler = logging.FileHandler(output_file, "w")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)


def main(args, config_train, taylor_coefficients):
    variables = config_train["variables"]
    training_path = config_train['output_path']
    training_path = training_path.split('/')[:-1]
    new_element = '{}_variables'.format(len(variables) + 1)
    training_path.append(new_element)
    config_train['output_path'] = '/' + os.path.join(*training_path)

    # Add the next variable to the training config that was not in there already.
    for key, variable in taylor_coefficients.items():
        if key not in variables:
            config_train["variables"].append(key)
            logger.info("Added variable {} to training config".format(key))
            break
    output_path = args.config_train
    yaml.dump(config_train, open(output_path, "w"), default_flow_style=False)
    logger.info("Save results to {}.".format(output_path))


if __name__ == "__main__":
    setup_logging(logging.DEBUG)
    args = parse_arguments()
    config = parse_config(args.config_train)
    taylor_path = config['taylor_coefficient_path']
    taylor_coefficients = parse_txt(taylor_path)
    main(args, config, taylor_coefficients)
