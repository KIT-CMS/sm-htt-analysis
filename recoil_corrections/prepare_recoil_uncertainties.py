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
mode = sys.argv[3] # choices: prefit -> asuming for all categories a 10% uncertainty (both scale & reso); provided uncertainty file == postfit() -> accessing measured values from combine fit in fitted_recoil_uncs.root

f = r.TFile.Open("shapes_mm_recoilunc_%s.root"%era)

if not os.path.exists(outfoldername):
    os.mkdir(outfoldername)

fout      = r.TFile.Open("%s/PFMETSys_%s.root"%(outfoldername,era),"recreate")
foutpuppi = r.TFile.Open("%s/PuppiMETSys_%s.root"%(outfoldername,era),"recreate")

r.gROOT.SetBatch()

hist_names = sorted([k.GetName() for k in f.GetListOfKeys() if "_ss" not in k.GetName() and "output_tree" not in k.GetName() ])

categories = set(sorted([k.strip("#").split("#")[1] for k in hist_names]))
variables = set(sorted([k.strip("#").split("#")[-2] for k in hist_names]))

category_dict = {
    "mm_njets_bin_0_vs_ptvis_bin_0" : {"njets_bin" : "NJet0"  , "pt_bin" :  5.0},
    "mm_njets_bin_0_vs_ptvis_bin_1" : {"njets_bin" : "NJet0"  , "pt_bin" : 15.0},
    "mm_njets_bin_0_vs_ptvis_bin_2" : {"njets_bin" : "NJet0"  , "pt_bin" : 25.0},
    "mm_njets_bin_0_vs_ptvis_bin_3" : {"njets_bin" : "NJet0"  , "pt_bin" : 40.0},
    "mm_njets_bin_0_vs_ptvis_bin_4" : {"njets_bin" : "NJet0"  , "pt_bin" : 55.0},
    "mm_njets_bin_1_vs_ptvis_bin_0" : {"njets_bin" : "NJet1"  , "pt_bin" :  5.0},
    "mm_njets_bin_1_vs_ptvis_bin_1" : {"njets_bin" : "NJet1"  , "pt_bin" : 15.0},
    "mm_njets_bin_1_vs_ptvis_bin_2" : {"njets_bin" : "NJet1"  , "pt_bin" : 25.0},
    "mm_njets_bin_1_vs_ptvis_bin_3" : {"njets_bin" : "NJet1"  , "pt_bin" : 40.0},
    "mm_njets_bin_1_vs_ptvis_bin_4" : {"njets_bin" : "NJet1"  , "pt_bin" : 55.0},
    "mm_njets_bin_2_vs_ptvis_bin_0" : {"njets_bin" : "NJetGe2", "pt_bin" :  5.0},
    "mm_njets_bin_2_vs_ptvis_bin_1" : {"njets_bin" : "NJetGe2", "pt_bin" : 15.0},
    "mm_njets_bin_2_vs_ptvis_bin_2" : {"njets_bin" : "NJetGe2", "pt_bin" : 25.0},
    "mm_njets_bin_2_vs_ptvis_bin_3" : {"njets_bin" : "NJetGe2", "pt_bin" : 40.0},
    "mm_njets_bin_2_vs_ptvis_bin_4" : {"njets_bin" : "NJetGe2", "pt_bin" : 55.0},
}

ptbins = np.array([0.0, 10.0, 20.0, 30.0, 50.0, 100.0])

means = {}

for hist_name in hist_names:
    category = hist_name.strip("#").split("#")[1]
    variable = hist_name.strip("#").split("#")[-2]
    if variable not in variables:
        continue
    means.setdefault(variable,{})
    hist = copy.deepcopy(getattr(f,hist_name))
    means[variable][category] = hist.GetMean()
    
hists = {}
for v in variables:
    if "puppi" in v:
        foutpuppi.cd()
    else:
        fout.cd()
    hists[v] = {}
    for jetbin in set([c["njets_bin"] for c in category_dict.values()]):
        hists[v][jetbin] = r.TH1D(jetbin,jetbin,len(ptbins)-1,ptbins)
        hists[v][jetbin].SetMinimum(0.0)
        hists[v][jetbin].SetMaximum(2.0)
    
    for cat in categories:
        hists[v][category_dict[cat]["njets_bin"]].SetBinContent(hists[v][category_dict[cat]["njets_bin"]].FindBin(category_dict[cat]["pt_bin"]), means[v][cat])

    for jetbin in set([c["njets_bin"] for c in category_dict.values()]):
        hists[v][jetbin].Write()

for f in [foutpuppi, fout]:
    f.cd()
    nJetBinsH = r.TH1D("nJetBinsH","nJetBinsH",3,0.0,3.0)
    for index, name in  enumerate(["NJet0", "NJet1", "NJetGe2"]):
        nJetBinsH.GetXaxis().SetBinLabel(index+1, name)
    nJetBinsH.Write()
    if mode == "prefit":
        syst = r.TH2D("syst","syst",2,0.0,2.0,3,0.0,3.0)
        for i in range(syst.GetNbinsX()):
            for j in range(syst.GetNbinsY()):
                syst.SetBinContent(i+1,j+1,0.1)
        syst.Write()
    else:
        if "Puppi" in f.GetName():
            modecopy = mode.replace("puppi","").replace("metParToZ","puppimetParToZ")
        else:
            modecopy = mode.replace("puppi","")
        print modecopy
        if not os.path.exists(modecopy):
            print "ERROR: cannot access specified uncertainty file:",modecopy,".Please provide a corresponding .json file"
            exit(1)
        uncertainties = json.loads(open(modecopy,"r").read())
        syst = r.TH2D("syst","syst",2,0.0,2.0,3,0.0,3.0)
        types = ["CMS_htt_boson_scale_met_Run%s"%era, "CMS_htt_boson_reso_met_Run%s"%era] # need exact the same order as in the histogram
        categories = ["mm_0jet", "mm_1jet", "mm_ge2jet"] # need exact the same order as in the histogram
        for i in range(syst.GetNbinsX()):
            for j in range(syst.GetNbinsY()):
                syst.SetBinContent(i+1,j+1,float(uncertainties[categories[j]][types[i]]))
        syst.Write()
