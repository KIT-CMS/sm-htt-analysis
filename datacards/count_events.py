#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import numpy as np

import logging
logger = logging.getLogger("")


def setup_logging(output_file, level=logging.DEBUG):
    logger.setLevel(level)
    formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    file_handler = logging.FileHandler(output_file, "w")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Count events of processes in datacard.")

    parser.add_argument("datacard", type=str, help="Datacard text file.")

    return parser.parse_args()


def main(args):
    logger.debug("Load datacard %s.", args.datacard)

    # Load datacard as text file
    lines = open(args.datacard).readlines()

    # Find out all categories and processes
    index_obs = None
    index_procs = None
    for i_line in range(len(lines) - 4):
        if "bin" in lines[i_line] and "observation" in lines[i_line + 1]:
            index_obs = i_line
        if "bin" in lines[i_line] and "process" in lines[i_line +
                                                         1] and "process" in lines[i_line
                                                                                   +
                                                                                   2] and "rate" in lines[i_line
                                                                                                          +
                                                                                                          3]:
            index_procs = i_line

    categories_obs = [
        c for c in lines[index_obs].split(" ") if not c in ["", "bin", "\n"]
    ]
    obs = [
        float(c) for c in lines[index_obs + 1].split(" ")
        if not c in ["", "observation", "\n"]
    ]
    dict_obs = {c: e for c, e in zip(categories_obs, obs)}

    categories_procs = [
        c for c in lines[index_procs].split(" ") if not c in ["", "bin", "\n"]
    ]
    procs = [
        c for c in lines[index_procs + 1].split(" ")
        if not c in ["", "process", "\n"]
    ]
    events_procs = [
        float(c) for c in lines[index_procs + 3].split(" ")
        if not c in ["", "rate", "\n"]
    ]

    categories_unique = list(set(categories_procs))
    procs_unique = list(set(procs))
    events_matrix = np.zeros((len(categories_unique), len(procs_unique)))
    for c, p, e in zip(categories_procs, procs, events_procs):
        index_c = categories_unique.index(c)
        index_p = procs_unique.index(p)
        events_matrix[index_c, index_p] += e

    # Print number of events in categories for data and simulation
    logger.info("Print number of events in categories.")
    for c in dict_obs:
        logger.info("Events in category %s (data, simulation): %s, %s", c,
                    dict_obs[c],
                    np.sum(events_matrix[categories_unique.index(c), :]))

    # Print number of events for processes in simulation
    logger.info("Print number of events for processes.")
    for p in procs_unique:
        logger.info("Process %s (simulation): %s", p,
                    np.sum(events_matrix[:, procs_unique.index(p)]))


if __name__ == "__main__":
    args = parse_arguments()
    setup_logging("count_events.log", logging.DEBUG)
    main(args)
