#!/usr/bin/env python

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch(True)

import argparse
import os
import array

import logging
logger = logging.getLogger("reweight_stxs_stage1")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Reweight STXS stage1 signals.")
    parser.add_argument(
        "output", type=str, help="Output path.")
    parser.add_argument(
        "files", type=str, nargs="+", help="Dataset files.")
    parser.add_argument(
        "--weight-branch",
        default="training_weight",
        type=str,
        help="Branch with weights.")
    parser.add_argument(
        "--stxs-branch",
        default="htxs_stage1p1cat",
        type=str,
        help="Branch with STXS flags.")
    return parser.parse_args()


def get_sums(file_, name, range_, args, i_file):
    tree = file_.Get(name)
    if tree == None:
        logger.critical("Failed to load tree %s.", name)
        raise Exception
    histname = name+"_h"
    c = ROOT.TCanvas(name+"_c", name+"_c")
    h = ROOT.TH1F(histname, histname, len(range_), range_[0]-0.5, range_[-1]+0.5)
    tree.Draw(args.stxs_branch+">>"+histname, args.weight_branch, "goff")
    h = ROOT.gDirectory.Get(histname)
    if h == None:
        logger.critical("Failed to get histogram %s.", histname)
        raise Exception
    h.Draw("HIST")
    c.Update()
    c.SaveAs("{}.pdf".format(os.path.join(args.output, "fold{}_reweight_stxs_stage1_{}".format(i_file, name))))

    sums = []
    for i in range(len(range_)):
        sums.append(h.GetBinContent(i+1))
    return sums


def reweight(file_, name, integral, bins, args):
    tree = file_.Get(name)
    if tree == None:
        logger.critical("Failed to load tree %s.", name)
        raise Exception

    weights = []
    for event in tree:
        weights.append(getattr(event, args.weight_branch))

    tree.SetBranchStatus(args.weight_branch, 0)
    copy = tree.CopyTree("")
    value = array.array("f", [-999])
    b = copy.Branch(args.weight_branch, value, args.weight_branch+"/F")
    num_bins = len(bins.keys())
    min_cat = min(bins.keys())
    for i, event in enumerate(copy):
        stxs_cat = int(getattr(copy, args.stxs_branch))
        if stxs_cat < min_cat:
            logger.warning("Encountered event with STXS flag %u and weight %f.", stxs_cat, weights[i])
            value[0] = weights[i]
        else:
            value[0] = weights[i]*integral/float(num_bins)/bins[stxs_cat]
        b.Fill()
    copy.Write()
    return copy


def main(args):
    # Compute integral of STXS sub-signals
    ggh_integral = 0.0
    qqh_integral = 0.0
    ggh_range = range(101, 112)
    qqh_range = range(201, 206)
    ggh_bins = {x: 0.0 for x in ggh_range}
    qqh_bins = {x: 0.0 for x in qqh_range}
    for i_file, filename in enumerate(args.files):
        logger.info("Process file %s.", filename)
        f = ROOT.TFile(filename)
        if f == None:
            logger.critical("Failed to load file %s.", filename)
            raise Exception

        sums = get_sums(f, "qqh", qqh_range, args, i_file)
        for i, r in enumerate(qqh_range):
            qqh_bins[r] += sums[i]
        qqh_integral += sum(sums)

        sums = get_sums(f, "ggh", ggh_range, args, i_file)
        for i, r in enumerate(ggh_range):
            ggh_bins[r] += sums[i]
        ggh_integral += sum(sums)

        f.Close()

    # Create new trees with reweighted signal
    for i_file, filename in enumerate(args.files):
        logger.info("Overwrite signal trees in file %s with reweighted training weights.", filename)
        f = ROOT.TFile(filename, "UPDATE")
        if f == None:
            logger.critical("Failed to load file %s.", filename)
            raise Exception

        reweight(f, "qqh", qqh_integral, qqh_bins, args)
        reweight(f, "ggh", ggh_integral, ggh_bins, args)

        f.Write()
        f.Close()

    # Make control plots
    for i_file, filename in enumerate(args.files):
        f = ROOT.TFile(filename)
        for name in ["ggh", "qqh"]:
            tree = f.Get(name)
            histname = name+"_h"
            c = ROOT.TCanvas(name+"_c", name+"_c")
            tree.Draw(args.stxs_branch+">>"+histname, args.weight_branch, "goff")
            h = ROOT.gDirectory.Get(histname)
            h.Draw("HIST")
            c.Update()
            c.SaveAs("{}.pdf".format(os.path.join(args.output, "fold{}_reweight_stxs_stage1_{}_control".format(i_file, name))))
        f.Close()


if __name__ == "__main__":
    args = parse_arguments()
    main(args)
