import ROOT as r
import json
import numpy as np
import copy
import os
import sys
import Dumbledraw.styles as styles

r.gROOT.SetBatch()
r.gStyle.SetOptStat(0)
styles.ModTDRStyle()
r.gStyle.SetTitleSize(0.045, 'XYZ')
r.gStyle.SetPaintTextFormat(".4f")

era = sys.argv[1]
infoldername = sys.argv[2]

finpuppi = r.TFile.Open("%s/PuppiMETSys_%s.root"%(infoldername,era),"read")

canv = r.TCanvas("c","c",1000,1000)

finpuppi.cd()
finpuppi.Print()
canv.cd()
syst_for_plot = finpuppi.Get("syst")
syst_for_plot.GetXaxis().SetBinLabel(1,"response")
syst_for_plot.GetXaxis().SetBinLabel(2,"resolution")
syst_for_plot.GetYaxis().SetBinLabel(1,"0-jet")
syst_for_plot.GetYaxis().SetBinLabel(2,"1-jet")
syst_for_plot.GetYaxis().SetBinLabel(3,"#geq 2-jet")
syst_for_plot.GetXaxis().SetLabelSize(0.09)
syst_for_plot.GetYaxis().SetLabelSize(0.09)
syst_for_plot.SetMarkerSize(3.0)
syst_for_plot.Draw("col text")
canv.SaveAs("%s_syst_%s.png"%("METRecoilPuppi",era))
canv.SaveAs("%s_syst_%s.pdf"%("METRecoilPuppi",era))
