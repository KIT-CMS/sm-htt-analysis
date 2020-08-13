#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ROOT
import numpy as np
from array import array
import matplotlib.pyplot as plt
ROOT.PyConfig.IgnoreCommandLineOptions = True  # disable ROOT internal argument parser
ROOT.gStyle.SetPaintTextFormat(".2f")
import sys

ROOT.gROOT.SetBatch()



def SetTDRStyle():
    """Sets the PubComm recommended style

    Just a copy of <http://ghm.web.cern.ch/ghm/plots/MacroExample/tdrstyle.C>
    @sa ModTDRStyle() to use this style with some additional customisation.
    """
    # For the canvas:
    ROOT.gStyle.SetCanvasBorderMode(0)
    ROOT.gStyle.SetCanvasColor(ROOT.kWhite)
    ROOT.gStyle.SetCanvasDefH(600)  # Height of canvas
    ROOT.gStyle.SetCanvasDefW(600)  # Width of canvas
    ROOT.gStyle.SetCanvasDefX(0)    # POsition on screen
    ROOT.gStyle.SetCanvasDefY(0)

    # For the Pad:
    ROOT.gStyle.SetPadBorderMode(0)
    # ROOT.gStyle.SetPadBorderSize(Width_t size = 1)
    ROOT.gStyle.SetPadColor(ROOT.kWhite)
    ROOT.gStyle.SetPadGridX(False)
    ROOT.gStyle.SetPadGridY(False)
    ROOT.gStyle.SetGridColor(0)
    ROOT.gStyle.SetGridStyle(3)
    ROOT.gStyle.SetGridWidth(1)

    # For the frame:
    ROOT.gStyle.SetFrameBorderMode(0)
    ROOT.gStyle.SetFrameBorderSize(1)
    ROOT.gStyle.SetFrameFillColor(0)
    ROOT.gStyle.SetFrameFillStyle(0)
    ROOT.gStyle.SetFrameLineColor(1)
    ROOT.gStyle.SetFrameLineStyle(1)
    ROOT.gStyle.SetFrameLineWidth(1)

    # For the histo:
    # ROOT.gStyle.SetHistFillColor(1)
    # ROOT.gStyle.SetHistFillStyle(0)
    ROOT.gStyle.SetHistLineColor(1)
    ROOT.gStyle.SetHistLineStyle(0)
    ROOT.gStyle.SetHistLineWidth(1)
    # ROOT.gStyle.SetLegoInnerR(Float_t rad = 0.5)
    # ROOT.gStyle.SetNumberContours(Int_t number = 20)

    ROOT.gStyle.SetEndErrorSize(2)
    # ROOT.gStyle.SetErrorMarker(20)
    # ROOT.gStyle.SetErrorX(0.)

    ROOT.gStyle.SetMarkerStyle(20)

    # For the fit/function:
    ROOT.gStyle.SetOptFit(1)
    ROOT.gStyle.SetFitFormat('5.4g')
    ROOT.gStyle.SetFuncColor(2)
    ROOT.gStyle.SetFuncStyle(1)
    ROOT.gStyle.SetFuncWidth(1)

    # For the date:
    ROOT.gStyle.SetOptDate(0)
    # ROOT.gStyle.SetDateX(Float_t x = 0.01)
    # ROOT.gStyle.SetDateY(Float_t y = 0.01)

    # For the statistics box:
    ROOT.gStyle.SetOptFile(0)
    ROOT.gStyle.SetOptStat(0)
    # To display the mean and RMS:   SetOptStat('mr')
    ROOT.gStyle.SetStatColor(ROOT.kWhite)
    ROOT.gStyle.SetStatFont(42)
    ROOT.gStyle.SetStatFontSize(0.025)
    ROOT.gStyle.SetStatTextColor(1)
    ROOT.gStyle.SetStatFormat('6.4g')
    ROOT.gStyle.SetStatBorderSize(1)
    ROOT.gStyle.SetStatH(0.1)
    ROOT.gStyle.SetStatW(0.15)
    # ROOT.gStyle.SetStatStyle(Style_t style = 1001)
    # ROOT.gStyle.SetStatX(Float_t x = 0)
    # ROOT.gStyle.SetStatY(Float_t y = 0)

    # Margins:
    ROOT.gStyle.SetPadTopMargin(0.06)
    ROOT.gStyle.SetPadBottomMargin(0.20)
    ROOT.gStyle.SetPadLeftMargin(0.30)
    ROOT.gStyle.SetPadRightMargin(0.11)

    # For the Global title:
    ROOT.gStyle.SetOptTitle(0)
    ROOT.gStyle.SetTitleFont(42)
    ROOT.gStyle.SetTitleColor(1)
    ROOT.gStyle.SetTitleTextColor(1)
    ROOT.gStyle.SetTitleFillColor(10)
    ROOT.gStyle.SetTitleFontSize(0.05)
    # ROOT.gStyle.SetTitleH(0); # Set the height of the title box
    # ROOT.gStyle.SetTitleW(0); # Set the width of the title box
    # ROOT.gStyle.SetTitleX(0); # Set the position of the title box
    # ROOT.gStyle.SetTitleY(0.985); # Set the position of the title box
    # ROOT.gStyle.SetTitleStyle(Style_t style = 1001)
    # ROOT.gStyle.SetTitleBorderSize(2)

    # For the axis titles:
    ROOT.gStyle.SetTitleColor(1, 'XYZ')
    ROOT.gStyle.SetTitleFont(42, 'XYZ')
    ROOT.gStyle.SetTitleSize(0.06, 'XYZ')
    # Another way to set the size?
    # ROOT.gStyle.SetTitleXSize(Float_t size = 0.02)
    # ROOT.gStyle.SetTitleYSize(Float_t size = 0.02)
    ROOT.gStyle.SetTitleXOffset(0.9)
    ROOT.gStyle.SetTitleYOffset(1.25)
    # ROOT.gStyle.SetTitleOffset(1.1, 'Y'); # Another way to set the Offset

    # For the axis labels:

    ROOT.gStyle.SetLabelColor(1, 'XYZ')
    ROOT.gStyle.SetLabelFont(42, 'XYZ')
    ROOT.gStyle.SetLabelOffset(0.007, 'XYZ')
    ROOT.gStyle.SetLabelSize(0.02, 'XYZ') ###############################################

    # For the axis:

    ROOT.gStyle.SetAxisColor(1, 'XYZ')
    ROOT.gStyle.SetStripDecimals(True)
    ROOT.gStyle.SetTickLength(0.03, 'XYZ')
    ROOT.gStyle.SetNdivisions(510, 'XYZ')
    ROOT.gStyle.SetPadTickX(1)
    ROOT.gStyle.SetPadTickY(1)

    # Change for log plots:
    ROOT.gStyle.SetOptLogx(0)
    ROOT.gStyle.SetOptLogy(0)
    ROOT.gStyle.SetOptLogz(0)

    # Postscript options:
    ROOT.gStyle.SetPaperSize(20., 20.)
    # ROOT.gStyle.SetLineScalePS(Float_t scale = 3)
    # ROOT.gStyle.SetLineStyleString(Int_t i, const char* text)
    # ROOT.gStyle.SetHeaderPS(const char* header)
    # ROOT.gStyle.SetTitlePS(const char* pstitle)

    # ROOT.gStyle.SetBarOffset(Float_t baroff = 0.5)
    # ROOT.gStyle.SetBarWidth(Float_t barwidth = 0.5)
    # ROOT.gStyle.SetPaintTextFormat(const char* format = 'g')
    # ROOT.gStyle.SetPalette(Int_t ncolors = 0, Int_t* colors = 0)
    # ROOT.gStyle.SetTimeOffset(Double_t toffset)
    # ROOT.gStyle.SetHistMinimumZero(kTRUE)

    ROOT.gStyle.SetHatchesLineWidth(5)
    ROOT.gStyle.SetHatchesSpacing(0.05)

def SetCorrMatrixPalette():
    ROOT.TColor.CreateGradientColorTable(3,
                                      array("d",[0.00, 0.50, 1.00]),
                                      array("d",[0.00, 1.00, 1.00]),
                                      array("d",[0.00, 1.00, 0.00]),
                                      array("d",[1.00, 1.00, 0.00]),
                                      10000,  1.0)

if __name__ == "__main__":
    SetTDRStyle()
    SetCorrMatrixPalette()
    #print cp
    #ROOT.gStyle.SetPalette(cp) #kBlueGreenYellow kCoffee
    #ROOT.TColor.InvertPalette()
    label_dict = {
        "r_ggH_GG2H_0J_PTH_0_10" : "0 Jet p_{T}^{H} [0,10]",
        "r_ggH_GG2H_0J_PTH_GT10" : "0 Jet p_{T}^{H} [10,200]",
        "r_ggH_GG2H_PTH_200_300" : "p_{T}^{H} [200,300]",
        "r_ggH_GG2H_PTH_GT300" : "p_{T}^{H} [300,#infty]",
        "r_ggH_GG2H_1J_PTH_0_60" : "1 Jet p_{T}^{H} [0,60]",
        "r_ggH_GG2H_1J_PTH_60_120" : "1 Jet p_{T}^{H} [60,120]",
        "r_ggH_GG2H_1J_PTH_120_200" : "1 Jet p_{T}^{H} [120,200]",
        "r_ggH_GG2H_GE2J" : "#geq 2 Jet p_{T}^{H} [0,200]",

        "r_qqH_QQ2HQQ_noVBFtopo" : "no VBF topo",
        "r_qqH_QQ2HQQ_GE2J_MJJ_GT350_PTH_GT200" : "#geq 2 Jet m_{jj} [350,#infty] p_{T}^{H} [200,#infty]",
        "r_qqH_QQ2HQQ_GE2J_MJJ_350_700_PTH_0_200" : "#geq 2 Jet m_{jj} [350,700] p_{T}^{H} [0,200]",
        "r_qqH_QQ2HQQ_GE2J_MJJ_GT700_PTH_0_200" : "#geq 2 Jet m_{jj} [700,#infty] p_{T}^{H} [0,200]",
    }
    label_list = [
        "r_ggH_GG2H_0J_PTH_0_10",
        "r_ggH_GG2H_0J_PTH_GT10",
        "r_ggH_GG2H_PTH_200_300",
        "r_ggH_GG2H_PTH_GT300",
        "r_ggH_GG2H_1J_PTH_0_60",
        "r_ggH_GG2H_1J_PTH_60_120",
        "r_ggH_GG2H_1J_PTH_120_200",
        "r_ggH_GG2H_GE2J",

        "r_qqH_QQ2HQQ_noVBFtopo",
        "r_qqH_QQ2HQQ_GE2J_MJJ_GT350_PTH_GT200",
        "r_qqH_QQ2HQQ_GE2J_MJJ_350_700_PTH_0_200",
        "r_qqH_QQ2HQQ_GE2J_MJJ_GT700_PTH_0_200",
    ]

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

    #Check, whether pois correspond to final selection:
    contained = True
    for p in pois:
       if p not in label_list:
            contained = False
            break
    pois = label_list

    num_pois = len(pois)
    m = ROOT.TH2D("h", "h", num_pois-1, 0, num_pois-1, num_pois-1, 0, num_pois-1)
    for i in range(num_pois-1):
        for j in range(i,num_pois-1):
            val = result.correlation(params.find(pois[i]), params.find(pois[j+1]))
            m.SetBinContent(i+1, j+1, val)

    m.SetTitle("")
    for i in range(num_pois-1):
        m.GetXaxis().SetBinLabel(i+1, "")
        m.GetYaxis().SetBinLabel(i+1, label_dict[pois[i+1]])
    m.GetXaxis().LabelsOption("v")
    m.GetYaxis().SetLabelFont(43)
    m.GetYaxis().SetLabelSize(10) ########################################################
    m.SetMinimum(-1)
    m.SetMaximum(1)

    c = ROOT.TCanvas("c", "c", 600, 600)
    c.SetGrid(1)
    m.SetContour(10000)
    m.Draw("colz text")

    tex = ROOT.TLatex()
    tex.SetNDC()
    tex.SetLineWidth(2)
    tex.SetTextAlign(11)
    tex.SetTextFont(43)
    tex.SetTextSize(25)
    tex.SetTextFont(43)
    tex.DrawLatex(0.30, 0.955, "CMS")
    #tex.DrawLatex(0.65, 0.955, "77.4 fb^{-1} (13 TeV)")
    tex.DrawLatex(0.65, 0.955, "137.1 fb^{-1} (13 TeV)")
    tex.SetTextFont(53)
    tex.DrawLatex(0.40, 0.955, "Preliminary")
    for i in range(num_pois-1):
        texlabel = ROOT.TLatex()
        texlabel.SetTextAngle(30)
        texlabel.SetTextFont(43)
        texlabel.SetTextAlign(32)
        texlabel.SetTextSize(10)   ###########################################
        texlabel.DrawLatex(i+0.6,-0.19,label_dict[pois[i]])

    texgrouplabel = ROOT.TLatex()
    texgrouplabel.SetTextFont(42)
    texgrouplabel.SetTextAlign(23)
    texgrouplabel.SetTextSize(0.04)
    texgrouplabel.DrawLatex(3.5,-2.0,"gg#rightarrowH,bbH")
    texgrouplabel.DrawLatex(9.0,-2.0,"VBF+V(qq)H")
    texgrouplabel.SetTextAngle(90)
    texgrouplabel.DrawLatex(-5.0,3.5,"gg#rightarrowH,bbH")
    texgrouplabel.DrawLatex(-5.0,9.0,"VBF+V(qq)H")

    lineh = ROOT.TLine(0.0,7.0,11.0,7.0)
    lineh.SetLineWidth(2)
    lineh.Draw()
    linev = ROOT.TLine(8.0,0.0,8.0,11.0)
    linev.SetLineWidth(2)
    linev.Draw()

    c.Update()

    c.SaveAs("{}_plot_poi_correlation_stage-1p1.pdf".format(era))
    c.SaveAs("{}_plot_poi_correlation_stage-1p1.png".format(era))
