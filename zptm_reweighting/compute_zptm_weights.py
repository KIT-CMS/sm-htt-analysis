import ROOT as r
import json
import numpy as np
import sys
import Dumbledraw.styles as styles

r.gROOT.SetBatch()
r.gStyle.SetPaintTextFormat(".2f")
styles.ModTDRStyle()

fname = sys.argv[1]
year = fname.split("_")[-1].replace(".root","")
f = r.TFile.Open(fname)

t = f.Get("output_tree")
t.GetEntry(0)

count_names = sorted([k.GetName() for k in t.GetListOfLeaves() if "_ss" not in k.GetName()])

categories = set(sorted([k.strip("#").split("#")[1] for k in count_names]))
processes = set(sorted([k.strip("#").split("#")[2] for k in count_names]))

yields = {
    "ZL_from_data" : {},
    "ZL" : {},
    "ratio" : {}
}

for count_name in count_names:
    category = count_name.strip("#").split("#")[1]
    process = count_name.strip("#").split("#")[2]
    if process == "ZL":
        yields["ZL"][category] = getattr(t,count_name)
    elif process == "data_obs":
        data_yield = getattr(t,count_name)
        yields["ZL_from_data"].setdefault(category,0.0)
        yields["ZL_from_data"][category] += data_yield
    else:
        mc_yield = getattr(t,count_name)
        yields["ZL_from_data"].setdefault(category,0.0)
        yields["ZL_from_data"][category] -= mc_yield

f.Close()

for c in categories:
    yields["ratio"][c] = yields["ZL_from_data"][c]/yields["ZL"][c]

total_mc_yield = sum([yields["ZL"][c] for c in categories])
total_weighted_mc_yield = sum([yields["ZL"][c]*yields["ratio"][c] for c in categories])
print "total ZL yield: ",total_mc_yield
print "total weighted ZL yield: ",total_weighted_mc_yield

for c in categories:
    yields["ratio"][c] *= total_mc_yield/total_weighted_mc_yield


corrected_total_weighted_mc_yield = sum([yields["ZL"][c]*yields["ratio"][c] for c in categories])
print "corrected total weighted ZL yield: ",corrected_total_weighted_mc_yield

with open("zptm_%s.json"%year,"w") as out:
    out.write(json.dumps(yields,sort_keys=True,indent=2)) 

variable_bins = {
    "m_vis" : np.array([50.0, 100.0, 200.0, 500.0, 1000.0]),
    "ptvis" : np.array([0.0, 10.0, 20.0, 30.0, 40.0, 50.0, 100.0, 150.0, 200.0, 300.0, 400.0, 1000.0]),
}
zptmass_histo = r.TH2D("zptmass_histo","zptmass_histo",len(variable_bins["m_vis"])-1,variable_bins["m_vis"],len(variable_bins["ptvis"])-1,variable_bins["ptvis"] )

for c in yields["ratio"]:
    mass_bin = int(c.split("_vs_")[0].split("_")[-1])
    pt_bin = int(c.split("_vs_")[1].split("_")[-1])
    zptmass_histo.SetBinContent(mass_bin+1,pt_bin+1, yields["ratio"][c])

fout = r.TFile.Open("zptm_weights_%s_kit.root"%year,"recreate")
zptmass_histo.Write()
fout.Close()

variable_bins["ptvis"][0] = 4.0
c = r.TCanvas("c","c",1200,800)
c.cd()
zptmass_histo_plot = r.TH2D("zptmass_histo","zptmass_histo",len(variable_bins["m_vis"])-1,variable_bins["m_vis"],len(variable_bins["ptvis"])-1,variable_bins["ptvis"] )
for i in range(zptmass_histo.GetNcells()):
    zptmass_histo_plot.SetBinContent(i, zptmass_histo.GetBinContent(i)) 
zptmass_histo_plot.SetTitle("")
zptmass_histo_plot.GetXaxis().SetTitle("Di-muon mass / GeV")
zptmass_histo_plot.GetYaxis().SetTitle("Di-muon p_{T} / GeV")
zptmass_histo_plot.GetYaxis().SetLimits(3.0, zptmass_histo.GetXaxis().GetXmax())
zptmass_histo_plot.GetYaxis().SetMoreLogLabels()
zptmass_histo_plot.Draw("col text")
c.SetLogy()
c.Update()
c.SaveAs(str(fout.GetName()).replace(".root",".png"))
c.SaveAs(str(fout.GetName()).replace(".root",".pdf"))
