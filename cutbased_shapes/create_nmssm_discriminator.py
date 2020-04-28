#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True  # disable ROOT internal argument parser

import argparse
import os
from multiprocessing import Pool
import glob
from array import array
import logging
from tqdm import tqdm
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
        description="Convert shapes from the shape producer to the sync format."
    )

    parser.add_argument("--cores", type=int, help="Cores for multiprocessing.")
    parser.add_argument("--variable", type=str, help="Variable for final discriminator.")
    parser.add_argument("--inputs", type=str, nargs="+", help="Path to input ROOT files.")
    return parser.parse_args()

def main(args):
    # create Pool for multiprocessing
    # pool = Pool(args.cores)
    print "Creating nmssm discriminator..."
    inputfiles = ["","",""]
    if not len(args.inputs)==3:
        print "Give exactly three input files: m_sv_puppi, mbb, m_ttvisbb"
        exit()
    for i in args.inputs:
        if "m_sv_puppi" in i:
            inputfiles[0] = i
        elif "mbb" in i:
            inputfiles[1] = i
        elif "m_ttvisbb" in i:
            inputfiles[2] = i
        else:
            print "m_sv_puppi, mbb, m_ttvisbb must be in the files!"
            exit()
    bin_list = []
    histname_list = []
    for i,inputfile in enumerate(inputfiles):
        print inputfile
        file_input = ROOT.TFile(inputfile)
        histname_list.append(sorted([k.GetName() for k in file_input.GetListOfKeys() if k.GetName() != "output_tree" and not
            (k.GetName().strip("#").split("#")[1].endswith("_ss") or
            k.GetName().strip("#").split("#")[1].endswith("_B") or
            k.GetName().strip("#").split("#")[1].endswith("_FF"))]))
        bin_list.append([])
        hist = file_input.Get(histname_list[i][0])
        for i_bin in range(1,hist.GetNbinsX()+2):
            bin_list[i].append(hist.GetBinLowEdge(i_bin))
        del hist
        del file_input

    binedges = []

    for i,bins in enumerate(bin_list):
        if i>0:
            start_value = binedges[-1]
        else:
            start_value=0.0
        for bin_ in bins:
            binedges.append(start_value+bin_)
    binedges = array("f",binedges)
    file_1 = ROOT.TFile(inputfiles[0])
    file_2 = ROOT.TFile(inputfiles[1])
    file_3 = ROOT.TFile(inputfiles[2])
    new_file = ROOT.TFile(inputfiles[0].replace("m_sv_puppi",args.variable),"RECREATE")
    new_file.cd()
    for histnames in histname_list:
        for histname in tqdm(histnames):
            new_histname = histname.replace("m_sv_puppi",args.variable)
            new_hist = ROOT.TH1D(new_histname,new_histname,len(binedges)-1,binedges)
            old_hist = file_1.Get(histname)
            n_bins_m_sv_puppi = old_hist.GetNbinsX()
            for i_bin in range(1,n_bins_m_sv_puppi+1):
                new_hist.SetBinContent(i_bin,old_hist.GetBinContent(i_bin))
            del old_hist
            old_hist = file_2.Get(histname.replace("m_sv_puppi","mbb"))
            n_bins_mbb = old_hist.GetNbinsX()
            for i_bin in range(1,n_bins_mbb+1):
                new_hist.SetBinContent(1+n_bins_m_sv_puppi+i_bin,old_hist.GetBinContent(i_bin))            
            del old_hist
            old_hist = file_3.Get(histname.replace("m_sv_puppi","m_ttvisbb"))
            n_bins_m_ttvisbb = old_hist.GetNbinsX()
            for i_bin in range(1,n_bins_m_ttvisbb+1):
                new_hist.SetBinContent(2+n_bins_m_sv_puppi+n_bins_mbb+i_bin,old_hist.GetBinContent(i_bin))          
            new_hist.Write()  
        break
    file_1.Close()
    file_2.Close()
    file_3.Close()
    new_file.Close()
    exit(0)
if __name__ == "__main__":
    args = parse_arguments()
    setup_logging("create_nmssm_discriminator.log", logging.DEBUG)
    main(args)
