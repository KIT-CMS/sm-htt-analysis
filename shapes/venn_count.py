#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True  # disable ROOT internal argument parser

import argparse
import os

from shape_producer.estimation_methods_2016 import DataEstimation
from shape_producer.era import Run2016
from shape_producer.channel import ETSM2016, MTSM2016, TTSM2016


def main(args):
    # Use 2016 dataset
    era = Run2016(args.datasets)

    # Channel
    if args.channel == "et":
        channel = ETSM2016()
        friend_directory = args.et_friend_directory
    elif args.channel == "mt":
        channel = MTSM2016()
        friend_directory = args.mt_friend_directory
    elif args.channel == "tt":
        channel = TTSM2016()
        friend_directory = args.tt_friend_directory
    else:
        raise Exception

    # Data estimation
    data = DataEstimation(era, args.directory, channel, friend_directory=friend_directory)
    files = data.get_files()
    cuts = (data.get_cuts() + channel.cuts).expand()

    # Combine all files
    tree = ROOT.TChain()
    for f in files:
        tree.Add(f + "/{}_nominal/ntuple".format(args.channel))
        #print("Add file to tree: {}".format(f))

    friend = ROOT.TChain()
    for f in files:
        friendname = os.path.basename(f).replace(".root", "")
        friendpath = os.path.join(friend_directory, friendname, friendname+".root")
        friend.Add(friendpath + "/{}_nominal/ntuple".format(args.channel))
        #print("Add file to friend: {}".format(friendpath))

    tree.AddFriend(friend)

    # All events after baseline selection
    tree.Draw("m_sv>>all_events", cuts, "goff")
    all_events = ROOT.gDirectory.Get("all_events").GetEntries()

    # Only 16043
    tree.Draw("m_sv>>only_16043", cuts + "*(({})==0)*(({})==1)".format(args.cut18032, args.cut16043), "goff")
    only_16043 = ROOT.gDirectory.Get("only_16043").GetEntries()

    # All 16043
    tree.Draw("m_sv>>all_16043", cuts + "*(({})==1)".format(args.cut16043), "goff")
    all_16043 = ROOT.gDirectory.Get("all_16043").GetEntries()

    # Only 18032
    tree.Draw("m_sv>>only_18032", cuts + "*(({})==1)*(({})==0)".format(args.cut18032, args.cut16043), "goff")
    only_18032 = ROOT.gDirectory.Get("only_18032").GetEntries()

    # All 18032
    tree.Draw("m_sv>>all_18032", cuts + "*(({})==1)".format(args.cut18032), "goff")
    all_18032 = ROOT.gDirectory.Get("all_18032").GetEntries()

    # Both
    tree.Draw("m_sv>>both", cuts + "*(({})==1)*(({})==1)".format(args.cut18032, args.cut16043), "goff")
    both = ROOT.gDirectory.Get("both").GetEntries()

    # None
    tree.Draw("m_sv>>none", cuts + "*(({})==0)*(({})==0)".format(args.cut18032, args.cut16043), "goff")
    none = ROOT.gDirectory.Get("none").GetEntries()

    # Print
    print("Cross-check: {}".format(both + only_18032 + only_16043 + none == all_events))
    print("All events: {}".format(all_events))
    print("In none of both selection: {}".format(none))
    print("In both selections together: {}".format(both))
    print("In at least one selection: {}".format(both + only_18032 + only_16043))
    print("Only 16043: {}".format(only_16043))
    print("All 16043: {}".format(all_16043))
    print("Only 18032: {}".format(only_18032))
    print("All 18032: {}".format(all_18032))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Count Venn diagramm numbers for event overlap.")
    parser.add_argument(
        "--channel",
        required=True,
        type=str,
        help="Channel.")
    parser.add_argument(
        "--cut16043",
        required=True,
        type=str,
        help="Cut for 16043 selection.")
    parser.add_argument(
        "--cut18032",
        required=True,
        type=str,
        help="Cut for 18032 selection.")
    parser.add_argument(
        "--directory",
        required=True,
        type=str,
        help="Directory with Artus outputs.")
    parser.add_argument(
        "--et-friend-directory",
        default=None,
        type=str,
        help=
        "Directory arranged as Artus output and containing a friend tree for et."
    )
    parser.add_argument(
        "--mt-friend-directory",
        default=None,
        type=str,
        help=
        "Directory arranged as Artus output and containing a friend tree for mt."
    )
    parser.add_argument(
        "--tt-friend-directory",
        default=None,
        type=str,
        help=
        "Directory arranged as Artus output and containing a friend tree for tt."
    )
    parser.add_argument(
        "--datasets", required=True, type=str, help="Kappa datsets database.")
    args = parser.parse_args()
    main(args)
