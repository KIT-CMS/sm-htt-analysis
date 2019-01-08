#!/usr/bin/env python
# -*- coding: utf-8 -*-


import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True  # disable ROOT internal argument parser
import sys


if __name__ == "__main__":
    era = sys.argv[1]
    print("[INFO] Plot for era {}.".format(era))

    filename = sys.argv[2]
    print("[INFO] Plot POI correlations from file {}.".format(filename))
    f = ROOT.TFile(filename)
    if f == None:
        raise Exception("[ERROR] File {} not found.".format(filename))

    result = f.Get("fit_s")
    if result == None:
        raise Exception("[ERROR] Failed to load fit_s from file {}.".format(filename))

    params = result.floatParsInit()
    pois = []
    for i in range(params.getSize()):
        name = params[i].GetName()
        if name.startswith("r"):
            pois.append(name)
    print("[INFO] Identified POIs with names {}.".format(pois))

    num_pois = len(pois)
    m = ROOT.TH2D("h", "h", 2, 0, num_pois, 2, 0, num_pois)
    for i in range(num_pois):
        for j in range(num_pois):
            val = result.correlation(params.find(pois[i]), params.find(pois[j]))
            m.SetBinContent(i+1, j+1, val)

    print("[DEBUG] Print correlation matrix:")
    m.Print()

    m.SetTitle("")
    for i in range(num_pois):
        m.GetXaxis().SetBinLabel(i+1, pois[i])
        m.GetYaxis().SetBinLabel(i+1, pois[i])
    m.GetXaxis().LabelsOption("v")
    m.SetMinimum(-1)
    m.SetMaximum(1)

    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetPalette(1)
    c = ROOT.TCanvas("c", "c", 800, 800)
    m.Draw("COLZ")
    c.Update()

    t = ROOT.TText()
    t.SetTextAlign(22)
    t.SetTextFont(42)
    for i in range(num_pois):
        for j in range(num_pois):
            t.DrawText(i+0.5, j+0.5, "{:.2f}".format(
                m.GetBinContent(i+1, j+1)))

    c.SaveAs("{}_plot_poi_correlation.pdf".format(era))
