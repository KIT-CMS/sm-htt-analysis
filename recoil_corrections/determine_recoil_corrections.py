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

era = sys.argv[1]
outfoldername = sys.argv[2]

f = r.TFile.Open("shapes_mm_recoil_%s.root"%era)

if not os.path.exists(outfoldername):
    os.mkdir(outfoldername)

fout      = r.TFile.Open("%s/Type1_PFMET_%s.root"%(outfoldername,era),"recreate")
foutpuppi = r.TFile.Open("%s/Type1_PuppiMET_%s.root"%(outfoldername,era),"recreate")

hist_names = sorted([k.GetName() for k in f.GetListOfKeys() if "_ss" not in k.GetName() and "output_tree" not in k.GetName() ])

categories = set(sorted([k.strip("#").split("#")[1] for k in hist_names]))
processes = set(sorted([k.strip("#").split("#")[2] for k in hist_names]))
variables = set(sorted([k.strip("#").split("#")[-2] for k in hist_names if "recoil" not in k]))

hists = {
    "ZL_from_data" : {},
    "ZL" : {},
}

variable_dict = {
     "metPerpToZ": "recoilZPerp" ,
     "metParToZ" : "recoilZParal",
     "puppimetPerpToZ": "recoilZPerp" ,
     "puppimetParToZ" : "recoilZParal",
}

variable_label_dict = {
     "metPerpToZ": "PF MET_{#perp Z}" ,
     "metParToZ" : "PF MET_{#parallel Z}",
     "puppimetPerpToZ": "PUPPI MET_{#perp Z}" ,
     "puppimetParToZ" : "PUPPI MET_{#parallel Z}",
}

category_dict = {
    "mm_njets_bin_0_vs_ptvis_bin_0" : "NJet0Pt0to10"   ,
    "mm_njets_bin_0_vs_ptvis_bin_1" : "NJet0Pt10to20"  ,
    "mm_njets_bin_0_vs_ptvis_bin_2" : "NJet0Pt20to30"  ,
    "mm_njets_bin_0_vs_ptvis_bin_3" : "NJet0Pt30to50"  ,
    "mm_njets_bin_0_vs_ptvis_bin_4" : "NJet0PtGt50"    ,
    "mm_njets_bin_1_vs_ptvis_bin_0" : "NJet1Pt0to10"   ,
    "mm_njets_bin_1_vs_ptvis_bin_1" : "NJet1Pt10to20"  ,
    "mm_njets_bin_1_vs_ptvis_bin_2" : "NJet1Pt20to30"  ,
    "mm_njets_bin_1_vs_ptvis_bin_3" : "NJet1Pt30to50"  ,
    "mm_njets_bin_1_vs_ptvis_bin_4" : "NJet1PtGt50"    ,
    "mm_njets_bin_2_vs_ptvis_bin_0" : "NJetGe2Pt0to10" ,
    "mm_njets_bin_2_vs_ptvis_bin_1" : "NJetGe2Pt10to20",
    "mm_njets_bin_2_vs_ptvis_bin_2" : "NJetGe2Pt20to30",
    "mm_njets_bin_2_vs_ptvis_bin_3" : "NJetGe2Pt30to50",
    "mm_njets_bin_2_vs_ptvis_bin_4" : "NJetGe2PtGt50"  ,
}

category_label_dict = {
    "mm_njets_bin_0_vs_ptvis_bin_0" : "N_{jets}= 0, p_{T}#in [0,10] GeV",
    "mm_njets_bin_0_vs_ptvis_bin_1" : "N_{jets}= 0, p_{T}#in [10,20] GeV",
    "mm_njets_bin_0_vs_ptvis_bin_2" : "N_{jets}= 0, p_{T}#in [20,30] GeV",
    "mm_njets_bin_0_vs_ptvis_bin_3" : "N_{jets}= 0, p_{T}#in [30,50] GeV",
    "mm_njets_bin_0_vs_ptvis_bin_4" : "N_{jets}= 0, p_{T}#in [50,#infty] GeV",
    "mm_njets_bin_1_vs_ptvis_bin_0" : "N_{jets}= 1, p_{T}#in [0,10] GeV",
    "mm_njets_bin_1_vs_ptvis_bin_1" : "N_{jets}= 1, p_{T}#in [10,20] GeV",
    "mm_njets_bin_1_vs_ptvis_bin_2" : "N_{jets}= 1, p_{T}#in [20,30] GeV",
    "mm_njets_bin_1_vs_ptvis_bin_3" : "N_{jets}= 1, p_{T}#in [30,50] GeV",
    "mm_njets_bin_1_vs_ptvis_bin_4" : "N_{jets}= 1, p_{T}#in [50,#infty] GeV",
    "mm_njets_bin_2_vs_ptvis_bin_0" : "N_{jets}#geq 2, p_{T}#in [0,10] GeV",
    "mm_njets_bin_2_vs_ptvis_bin_1" : "N_{jets}#geq 2, p_{T}#in [10,20] GeV",
    "mm_njets_bin_2_vs_ptvis_bin_2" : "N_{jets}#geq 2, p_{T}#in [20,30] GeV",
    "mm_njets_bin_2_vs_ptvis_bin_3" : "N_{jets}#geq 2, p_{T}#in [30,50] GeV",
    "mm_njets_bin_2_vs_ptvis_bin_4" : "N_{jets}#geq 2, p_{T}#in [50,#infty] GeV",
}

for hist_name in hist_names:
    category = hist_name.strip("#").split("#")[1]
    process = hist_name.strip("#").split("#")[2]
    variable = hist_name.strip("#").split("#")[-2]
    if variable not in variables:
        continue
    hists["ZL_from_data"].setdefault(variable,{})
    hists["ZL"].setdefault(variable,{})
    if process == "ZL":
        hists["ZL"][variable][category] = copy.deepcopy(getattr(f,hist_name))
    elif process == "data_obs":
        data_hist = copy.deepcopy(getattr(f,hist_name))
        hists["ZL_from_data"][variable].setdefault(category,None)
        if not hists["ZL_from_data"][variable][category]:
            hists["ZL_from_data"][variable][category] = data_hist
        else:
            hists["ZL_from_data"][variable][category].Add(data_hist, 1.0)

    else:
        mc_hist = copy.deepcopy(getattr(f,hist_name))
        hists["ZL_from_data"][variable].setdefault(category,None)
        if not hists["ZL_from_data"][variable][category]:
            mc_hist.Scale(-1.0)
            hists["ZL_from_data"][variable][category] = mc_hist
        else:
            hists["ZL_from_data"][variable][category].Add(mc_hist, -1.0)

c = r.TCanvas("c","c",1000,1000)

mean_reso_dict = {}

for v in variables:

    mean_reso_dict[v] = {}
    for cat in categories:
        datahistname = "_".join([variable_dict[v],category_dict[cat],"hist_data"])
        datafuncname = "_".join([variable_dict[v],category_dict[cat],"data"])
        mchistname = "_".join([variable_dict[v],category_dict[cat],"hist_mc"])
        mcfuncname = "_".join([variable_dict[v],category_dict[cat],"mc"])

        mean_reso_dict[v][cat] = {}
        c.Clear()
        c.cd()
        hists["ZL_from_data"][v][cat].SetLineColor(r.kOrange+2)
        hists["ZL_from_data"][v][cat].SetLineWidth(3)
        hists["ZL_from_data"][v][cat].SetMaximum(1.2*max(hists["ZL_from_data"][v][cat].GetMaximum(), hists["ZL"][v][cat].GetMaximum()))
        hists["ZL_from_data"][v][cat].SetMinimum(0.0)
        hists["ZL_from_data"][v][cat].GetXaxis().SetTitle(variable_label_dict[v])
        hists["ZL_from_data"][v][cat].GetYaxis().SetTitle("N_{events}")
        hists["ZL_from_data"][v][cat].SetStats(0)
        hists["ZL_from_data"][v][cat].Draw("hist")
        hists["ZL_from_data"][v][cat].SetTitle(datahistname)
        hists["ZL_from_data"][v][cat].SetName(datahistname)

        hists["ZL"][v][cat].SetLineColor(r.kCyan+2)
        hists["ZL"][v][cat].SetLineWidth(3)
        hists["ZL"][v][cat].SetStats(0)
        hists["ZL"][v][cat].Draw("hist same")
        hists["ZL"][v][cat].SetTitle(mchistname)
        hists["ZL"][v][cat].SetName(mchistname)

        hists["ZL_from_data"][v][cat].Fit("gaus")
        fdata = hists["ZL_from_data"][v][cat].GetFunction("gaus")
        fdata.SetLineColor(r.kRed+2)
        fdata.SetLineWidth(3)
        fdata.Draw("c same")
        fdata.SetTitle(datafuncname)
        fdata.SetName(datafuncname)
        fdata_pars = fdata.GetParameters()
        mean_reso_dict[v][cat]["data"] = {
            "mean" : fdata_pars[1],
            "resolution": fdata_pars[2]
        }

        hists["ZL"][v][cat].Fit("gaus")
        fmc = hists["ZL"][v][cat].GetFunction("gaus")
        fmc.SetLineColor(r.kBlue)
        fmc.SetLineWidth(3)
        fmc.Draw("c same")
        fmc.SetTitle(mcfuncname)
        fmc.SetName(mcfuncname)
        fmc_pars = fmc.GetParameters()
        mean_reso_dict[v][cat]["mc"] = {
            "mean" : fmc_pars[1],
            "resolution": fmc_pars[2]
        }
        legend = r.TLegend(0.2,0.82,0.95,0.92)
        legend.SetNColumns(2)
        legend.AddEntry(hists["ZL_from_data"][v][cat], "Data","l")
        legend.AddEntry(fdata, "Gauss fit data: #mu = %.2f, #sigma = %.2f"%(fdata_pars[1], fdata_pars[2]),"l")
        legend.AddEntry(hists["ZL"][v][cat], "MC","l")
        legend.AddEntry(fmc, "Gauss fit MC: #mu = %.2f, #sigma = %.2f"%(fmc_pars[1], fmc_pars[2]),"l")
        legend.Draw()

        text = r.TLatex()
        text.SetNDC()
        text.SetTextFont(42)
        text.SetTextSize(0.04)
        text.DrawLatex(0.18, 0.96, category_label_dict[cat])

        plotname = outfoldername+"/"+"_".join([v,cat])+".png" 
        c.SaveAs(plotname)
        c.SaveAs(plotname.replace(".png",".pdf"))
        if "puppi" in v:
            foutpuppi.cd()
        else:
            fout.cd()

        hists["ZL_from_data"][v][cat].Write()
        hists["ZL"][v][cat].Write()
        fdata.Write()
        fmc.Write()

for f in [foutpuppi, fout]:
    f.cd()
    projH = r.TH1D("projH","projH",2,0.0,2.0)
    for index, name in  enumerate(["recoilZPerp", "recoilZParal"]):
        projH.GetXaxis().SetBinLabel(index+1, name)
    projH.Write()

    nJetBinsH = r.TH1D("nJetBinsH","nJetBinsH",3,0.0,3.0)
    for index, name in  enumerate(["NJet0", "NJet1", "NJetGe2"]):
        nJetBinsH.GetXaxis().SetBinLabel(index+1, name)
    nJetBinsH.Write()

    ZPtBinsH = r.TH1D("ZPtBinsH","ZPtBinsH",5,0.0,5.0)
    for index, name in  enumerate(["Pt0to10","Pt10to20", "Pt20to30", "Pt30to50",  "PtGt50"]):
        ZPtBinsH.GetXaxis().SetBinLabel(index+1, name)
    ZPtBinsH.Write()


with open("%s/recoil.json"%outfoldername,"w") as jsonout:
    jsonout.write(json.dumps(mean_reso_dict, sort_keys=True, indent=2))
    jsonout.close()
