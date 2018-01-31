#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ROOT

import argparse
import numpy

import QuantileShifter

import logging
logger = logging.getLogger("")

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Produce shapes for 2016 Standard Model analysis.")

    parser.add_argument(
        "-i",
        "--input",
        required=True,
        type=str,
        help="Input file name. 'merged' in path is going to be replaced by 'calibrated' for output file")
    parser.add_argument(
        "--channels",
        default=[],
        nargs='+',
        type=str,
        help="Channels to be considered.")
    parser.add_argument(
        "--shifts",
        default=["nominal"],
        nargs='+',
        type=str,
        help="Systematc shifts to be considered.")
    parser.add_argument(
        "--num-threads",
        default=32,
        type=int,
        help="Number of threads to be used.")

    return parser.parse_args()

def setup_logging(output_file, level=logging.DEBUG):
    logger.setLevel(level)
    formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    file_handler = logging.FileHandler(output_file, "w")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

def main(args):
    # load shifters
    prompt_e_d0_shifter = QuantileShifter.QuantileShifter("cdf_splines.root", "e_prompt_MC_d0", "e_prompt_data_d0", True)
    prompt_e_dZ_shifter = QuantileShifter.QuantileShifter("cdf_splines.root", "e_prompt_MC_dZ", "e_prompt_data_dZ", True)
    prompt_m_d0_shifter = QuantileShifter.QuantileShifter("cdf_splines.root", "m_prompt_MC_d0", "m_prompt_data_d0", True)
    prompt_m_dZ_shifter = QuantileShifter.QuantileShifter("cdf_splines.root", "m_prompt_MC_dZ", "m_prompt_data_dZ", True)
    nonprompt_e_d0_shifter = QuantileShifter.QuantileShifter("cdf_splines.root", "e_nonprompt_MC_d0", "e_nonprompt_data_d0", True)
    nonprompt_e_dZ_shifter = QuantileShifter.QuantileShifter("cdf_splines.root", "e_nonprompt_MC_dZ", "e_nonprompt_data_dZ", True)
    nonprompt_m_d0_shifter = QuantileShifter.QuantileShifter("cdf_splines.root", "m_nonprompt_MC_d0", "m_nonprompt_data_d0", True)
    nonprompt_m_dZ_shifter = QuantileShifter.QuantileShifter("cdf_splines.root", "m_nonprompt_MC_dZ", "m_nonprompt_data_dZ", True)
    
    input_file = ROOT.TFile(args.input, "READ")
    output_file = ROOT.TFile(args.input.replace("merged", "calibrated_new"), "RECREATE")
    directories = {}
    for channel in args.channels:
        for shift in args.shifts:
            input_tree = input_file.Get("%s_%s/ntuple"%(channel, shift))
            if input_tree == None:
                continue
            directories[channel] = output_file.mkdir("%s_%s"%(channel, shift))
            directories[channel].cd()
            
            input_tree = input_file.Get("%s_%s/ntuple"%(channel, shift))
            output_tree = ROOT.TTree("ntuple","ntuple")
            
            # declare vars and branches
            d0_1 = numpy.zeros(1, dtype=float)
            dZ_1 = numpy.zeros(1, dtype=float)
            d0_2 = numpy.zeros(1, dtype=float)
            dZ_2 = numpy.zeros(1, dtype=float)
            d0_1_calib_all = numpy.zeros(1, dtype=float)
            dZ_1_calib_all = numpy.zeros(1, dtype=float)
            d0_2_calib_all = numpy.zeros(1, dtype=float)
            dZ_2_calib_all = numpy.zeros(1, dtype=float)
            output_tree.Branch("d0_1_calib", d0_1, "d0_1_calib/D")
            output_tree.Branch("dZ_1_calib", dZ_1, "dZ_1_calib/D")
            #output_tree.Branch("d0_1_calib_all", d0_1_calib_all, "d0_1_calib_all/D")
            #output_tree.Branch("dZ_1_calib_all", dZ_1_calib_all, "dZ_1_calib_all/D")
            output_tree.Branch("d0_2_calib", d0_2, "d0_2_calib/D")
            output_tree.Branch("dZ_2_calib", dZ_2, "dZ_2_calib/D")
            #output_tree.Branch("d0_2_calib_all", d0_2_calib_all, "d0_2_calib_all/D")
            #output_tree.Branch("dZ_2_calib_all", dZ_2_calib_all, "dZ_2_calib_all/D")
            for event in input_tree:
                d0_1[0] = event.d0_1
                dZ_1[0] = event.dZ_1
                d0_2[0] = event.d0_2
                dZ_2[0] = event.dZ_2
                #d0_1_calib_all[0] = event.d0_1
                #dZ_1_calib_all[0] = event.dZ_1
                #d0_2_calib_all[0] = event.d0_2
                #dZ_2_calib_all[0] = event.dZ_2
                '''
                # first tau candidate
                if event.gen_match_1 == 1:
                    d0_1[0] = prompt_e_d0_shifter.shift(d0_1[0])
                    dZ_1[0] = prompt_e_dZ_shifter.shift(dZ_1[0])
                    d0_1_calib_all[0] = d0_1[0]
                    dZ_1_calib_all[0] = dZ_1[0]
                elif event.gen_match_1 == 2:
                    d0_1[0] = prompt_m_d0_shifter.shift(d0_1[0])
                    dZ_1[0] = prompt_m_dZ_shifter.shift(dZ_1[0])
                    d0_1_calib_all[0] = d0_1[0]
                    dZ_1_calib_all[0] = dZ_1[0]
                elif event.gen_match_1 == 3:
                    d0_1_calib_all[0] = prompt_e_d0_shifter.shift(d0_1_calib_all[0])
                    dZ_1_calib_all[0] = prompt_e_dZ_shifter.shift(dZ_1_calib_all[0])
                elif event.gen_match_1 == 4:
                    d0_1_calib_all[0] = prompt_m_d0_shifter.shift(d0_1_calib_all[0])
                    dZ_1_calib_all[0] = prompt_m_dZ_shifter.shift(dZ_1_calib_all[0])
                # second tau candidate
                if event.gen_match_2 == 1:
                    d0_2[0] = prompt_e_d0_shifter.shift(d0_2[0])
                    dZ_2[0] = prompt_e_d0_shifter.shift(dZ_2[0])
                    d0_2_calib_all[0] = d0_2[0]
                    dZ_2_calib_all[0] = dZ_2[0]
                elif event.gen_match_2 == 2:
                    d0_2[0] = prompt_m_d0_shifter.shift(d0_2[0])
                    dZ_2[0] = prompt_m_d0_shifter.shift(dZ_2[0])
                    d0_2_calib_all[0] = d0_2[0]
                    dZ_2_calib_all[0] = dZ_2[0]
                elif event.gen_match_2 == 3:
                    d0_2_calib_all[0] = prompt_e_d0_shifter.shift(d0_2_calib_all[0])
                    dZ_2_calib_all[0] = prompt_e_dZ_shifter.shift(dZ_2_calib_all[0])
                elif event.gen_match_2 == 4:
                    d0_2_calib_all[0] = prompt_m_d0_shifter.shift(d0_2_calib_all[0])
                    dZ_2_calib_all[0] = prompt_m_dZ_shifter.shift(dZ_2_calib_all[0])
                '''
                # first tau candidate
                if event.gen_match_1 == 1:
                    d0_1[0] = prompt_e_d0_shifter.shift(d0_1[0])
                    dZ_1[0] = prompt_e_dZ_shifter.shift(dZ_1[0])
                elif event.gen_match_1 == 2:
                    d0_1[0] = prompt_m_d0_shifter.shift(d0_1[0])
                    dZ_1[0] = prompt_m_dZ_shifter.shift(dZ_1[0])
                elif event.gen_match_1 == 3:
                    d0_1[0] = nonprompt_e_d0_shifter.shift(d0_1[0])
                    dZ_1[0] = nonprompt_e_dZ_shifter.shift(dZ_1[0])
                elif event.gen_match_1 == 4:
                    d0_1[0] = nonprompt_m_d0_shifter.shift(d0_1[0])
                    dZ_1[0] = nonprompt_m_dZ_shifter.shift(dZ_1[0])
                # second tau candidate
                if event.gen_match_2 == 1:
                    d0_2[0] = prompt_e_d0_shifter.shift(d0_2[0])
                    dZ_2[0] = prompt_e_dZ_shifter.shift(dZ_2[0])
                elif event.gen_match_2 == 2:
                    d0_2[0] = prompt_m_d0_shifter.shift(d0_2[0])
                    dZ_2[0] = prompt_m_dZ_shifter.shift(dZ_2[0])
                elif event.gen_match_2 == 3:
                    d0_2[0] = nonprompt_e_d0_shifter.shift(d0_2[0])
                    dZ_2[0] = nonprompt_e_dZ_shifter.shift(dZ_2[0])
                elif event.gen_match_2 == 4:
                    d0_2[0] = nonprompt_m_d0_shifter.shift(d0_2[0])
                    dZ_2[0] = nonprompt_m_dZ_shifter.shift(dZ_2[0])
                output_tree.Fill()
            output_tree.Write()
    input_file.Close()
    output_file.Close()
    
    


if __name__ == "__main__":
    args = parse_arguments()
    setup_logging("CreateCalibratedFriendTrees.log", logging.DEBUG)
    main(args)