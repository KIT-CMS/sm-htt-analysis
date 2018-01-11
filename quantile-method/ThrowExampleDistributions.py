#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ROOT
import random

def main():
    outputfile = ROOT.TFile("test_distributions.root", "RECREATE")
    hist1 = ROOT.TH1F("source", "source", 8, 0., 100.)
    hist2 = ROOT.TH1F("target", "target", 8, 0., 100.)
    for i in range(100000):
        hist1.Fill(random.gauss(40., 10.))
        hist2.Fill(random.gauss(50., 15.))
    hist1.Write()
    hist2.Write()
    outputfile.Close()

if __name__ == "__main__":
    main()