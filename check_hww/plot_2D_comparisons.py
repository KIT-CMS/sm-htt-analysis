import ROOT as r
import json
import numpy as np
import sys
import Dumbledraw.styles as styles
import yaml
import os

r.gROOT.SetBatch()
r.gStyle.SetPaintTextFormat(".2f")
styles.ModTDRStyle()
binning = yaml.load(open("shapes/binning.yaml"))

fname = sys.argv[1]
f = r.TFile.Open(fname)
channel = fname.split("/")[1].split("_")[1]

channel_dict = {
    "mt" : "#mu^{}#tau_{h}",
    "et" : "e^{}#tau_{h}",
    "tt" : "^{}#tau_{h}^{}#tau_{h}",
    "em" : "e#mu",
}


signals = [
    "HWW",
    "ggH125",
    "qqH125",
]
outfolder = "plots_hww_vs_htt"
if not os.path.exists(outfolder):
    os.makedirs(outfolder)

trees = {}
for s in signals:
    trees[s] = f.Get(s)

c = r.TCanvas("c","c",1200,800)
c.SetMargin(0.13,0.11,0.13,0.1)
c.cd()
variables = ["m_vis", "ptvis", "DiTauDeltaR", "pZetaMissVis", "mTdileptonMET"]
for i,var_i in enumerate(variables):
    for j,var_j in enumerate(variables):
        if i < j:
            print var_i,var_j
            varpair = ":".join([var_j,var_i])
            i_binning = np.array(binning["control"][channel][var_i]["bins"], dtype=float)
            j_binning = np.array(binning["control"][channel][var_j]["bins"], dtype=float)
            for s in signals:
                c.Clear()
                histname = "_".join([channel,s,varpair.replace(":","_vs_")])
                comp_hist = r.TH2D(histname,histname,len(i_binning)-1,i_binning,len(j_binning)-1,j_binning)
                trees[s].Draw("%s>>%s"%(varpair,histname),"training_weight","goff")
                comp_hist.Draw("colz")
                comp_hist.SetTitle("")
                i_label = styles.x_label_dict[channel][var_i]
                j_label = styles.x_label_dict[channel][var_j]
                comp_hist.GetXaxis().SetTitle(i_label)
                comp_hist.GetYaxis().SetTitle(j_label)
                comp_hist.GetYaxis().SetTitleOffset(comp_hist.GetXaxis().GetTitleOffset()+0.1)
                ChannelYearText = r.TLatex()
                ChannelYearText.SetNDC()
                ChannelYearText.SetTextAngle(0)
                ChannelYearText.SetTextColor(r.kBlack)
                ChannelYearText.SetTextFont(42)
                ChannelYearText.SetTextSize(0.05)
                ChannelYearText.DrawLatex(0.13,0.93,channel_dict[channel])
                ChannelYearText.DrawLatex(0.58,0.93,"41.5 fb^{-1} (2017, 13 TeV)")
                c.Update()
                c.SaveAs("%s/%s.png"%(outfolder,histname))
                c.SaveAs("%s/%s.pdf"%(outfolder,histname))
