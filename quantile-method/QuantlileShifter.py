#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ROOT

import Dumbledraw.dumbledraw as dd
import argparse
import copy
import array
import random

import logging
logger = logging.getLogger("")

class QuantileShifter(object):
    def __init__(self, inputfile, source, target):
        quantilefile = ROOT.TFile(inputfile, "READ")
        self._source = copy.deepcopy(quantilefile.Get(source))
        self._target = copy.deepcopy(quantilefile.Get(target))
        quantilefile.Close()
    
    def shift(self, value):
        value = self._source.Eval(value)
        npoints = self._target.GetNp()
        xup = ROOT.Double()
        yup = ROOT.Double()
        xdown = ROOT.Double()
        ydown = ROOT.Double()
        self._target.GetKnot(0, xdown, ydown)
        i = 0
        for index in range(npoints):
            i = index
            self._target.GetKnot(index, xdown, ydown)
            self._target.GetKnot(index+1, xup, yup)
            if value <= yup and yup != 0.0:
                break            
        
        result = xdown + (value - ydown) / (yup - ydown) * (xup - xdown)
        result -= (self._target.Eval(result) - value) / self._target.Derivative(result)
        return result

def setup_logging(output_file, level=logging.DEBUG):
    logger.setLevel(level)
    formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    file_handler = logging.FileHandler(output_file, "w")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

def main():
    shifter = QuantileShifter("splines.root", "source", "target")
    backshifter = QuantileShifter("splines.root", "target", "source")
    hist1 = ROOT.TH1F("source", "source", 100, 0., 100.)
    hist2 = ROOT.TH1F("shifted", "shifted", 100, 0., 100.)
    hist3 = ROOT.TH1F("backshift", "backshift", 100, 0., 100.)
    hist4 = ROOT.TH1F("target", "target", 100, 0., 100.)
    for i in range(100000):
        number = random.gauss(40., 10.)
        hist1.Fill(number)
        hist2.Fill(shifter.shift(number))
        hist3.Fill(backshifter.shift(shifter.shift(number)))
        hist4.Fill(50.+(number-40.)*3./2.) #random.gauss(50., 15.))
    plot = dd.Plot([[0.54, 0.52], [0.27, 0.25]], "ModTDR", r=0.04, l=0.14)
    plot.add_hist(hist1, "source")
    plot.add_hist(hist1, "source_err")
    plot.add_hist(hist2, "shifted")
    plot.add_hist(hist3, "backshift")
    plot.add_hist(hist4, "target")
    plot.add_hist(hist4, "target_err")
    plot.setGraphStyle('source', 'hist', linecolor=2, linewidth=3)
    plot.setGraphStyle('shifted', 'hist', linecolor=4, linewidth=1)
    plot.setGraphStyle('backshift', 'hist', linecolor=8, linewidth=3)
    plot.setGraphStyle('target', 'hist', linecolor=6, linewidth=1)
    plot.setGraphStyle('source_err', 'e2', fillcolor=2, fillstyle=3001, linecolor=0)
    plot.setGraphStyle('target_err', 'e2', fillcolor=6, fillstyle=3001, linecolor=0)
    
    plot.subplot(0).setYlabel("N_{events}")
    plot.subplot(1).setYlabel("shifted/tar.")
    plot.subplot(2).setYlabel("bck.sh./orig.")
    plot.subplot(1).setYlims(0.55, 1.45)
    plot.subplot(2).setYlims(0.55, 1.45)
    plot.subplot(1).setNYdivisions(6, 10)
    plot.subplot(2).setNYdivisions(6, 10)
    plot.subplot(2).setXlabel("variable (arb.units)")
    plot.scaleYTitleOffset(2.0)
    
    plot.subplot(2).normalize(["source_err", "backshift"], "source")
    plot.subplot(1).normalize(["shifted", "target_err"], "target")
    plot.subplot(0).Draw(["source_err", "target_err", "source", "target", "shifted", "backshift"])
    plot.subplot(1).Draw(["target_err", "shifted"])
    plot.subplot(2).Draw(["source_err", "backshift"])
    plot.add_legend(width=0.25, height=0.2)
    plot.legend(0).add_entry(0, "source", "original", 'l')
    plot.legend(0).add_entry(0, "source_err", "original Poisson err.", 'f')
    plot.legend(0).add_entry(0, "target", "target", 'l')
    plot.legend(0).add_entry(0, "target_err", "target Poisson err.", 'f')
    plot.legend(0).add_entry(0, "shifted", "shifted", 'l')
    plot.legend(0).add_entry(0, "backshift", "shifted back", 'l')
    plot.legend(0).Draw()
    plot.save("applied_quantile_method.pdf")


if __name__ == "__main__":
    setup_logging("cumdistfunc.log", logging.DEBUG)
    main()