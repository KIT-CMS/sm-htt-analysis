#!/usr/bin/env python

import argparse
import os
import yaml


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--channels", nargs="+", type=str,
                        choices=["et", "mt", "tt", "em"],
                        help="Channels to be processed.")
    parser.add_argument("-v", "--variable", type=str,
                        help="Discriminating variable.")
    parser.add_argument("-e", "--era", type=int,
                        help="Era.")
    parser.add_argument("-n", "--cores", default=8, type=int,
                        help="Number of cores.")
    parser.add_argument("-s", "--shape-groups", nargs="+", type=str,
                        choices=["backgrounds", "sm_signals", "bbH",
                                 "ggH_t", "ggH_b", "ggH_i",
                                 "ggA_t", "ggA_b", "ggA_i",
                                 "ggh_t", "ggh_b", "ggh_i"],
                        help="Shape groups to be processed.")
    return parser.parse_args()


def main(args):
    tmp_str = "{} {} {} {} {} {}\n"
    with open("arguments.txt", "w") as f:
        for ch in args.channels:
            for shape_group in args.shape_groups:
                f.write(
                    tmp_str.format(
                        os.path.dirname(os.getcwd()),
                        args.cores,
                        args.era,
                        args.variable,
                        shape_group,
                        ch)
                    )
    return


if __name__ == "__main__":
    args = parse_args()
    main(args)
