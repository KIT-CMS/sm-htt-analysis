import ROOT as r
import re
import math
import os
import numpy as np
import Dumbledraw.dumbledraw as dd
import Dumbledraw.rootfile_parser_inputshapes as rootfile_parser
import Dumbledraw.styles as styles
import sys

def sorted_nicely(l):
    """ Sort the given iterable in the way that humans expect: alphanumeric sort (in bash, that's 'sort -V')"""
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    return sorted(l, key = alphanum_key)


def sorted_cats(l):
    return sorted(l,key = lambda k : [float(k.replace(k.split("-")[0],"").replace("-less-","").replace("-greater-","").replace("p","."))]  )

fname = sys.argv[1]

f = r.TFile(fname,"read")
t = f.Get("output_tree")
t.GetEntry(0)

counts =  [k.GetName() for k in t.GetListOfLeaves() if "_FF" not in k.GetName() and "_ss" not in k.GetName() and "data_obs" not in k.GetName()]

variables = sorted_nicely(set([k.strip("#").split("#")[1].split("-")[0] for k in counts]))

processes = sorted_nicely(set([k.strip("#").split("#")[2] for k in counts]))

categories_less = {}
categories_greater = {}
cutvalues = {}
for var in variables:
    categories_less[var] = sorted_cats(set([k.strip("#").split("#")[1] for k in counts if "less" in k and var  == k.strip("#").split("#")[1].split("-")[0]] ))
    categories_greater[var] = sorted_cats(set([k.strip("#").split("#")[1] for k in counts if "greater" in k and var == k.strip("#").split("#")[1].split("-")[0]]))
    cutvalues[var] = [float(k.replace(k.split("-")[0],"").replace("-less-","").replace("p",".")) for k in categories_less[var]]
    print var
    for cl,cg,val in zip(categories_less[var],categories_greater[var],cutvalues[var]):
        print "\t",cl,cg,val
    print "-------------------"

backgrounds = [p for p in processes if "H125" not in p]
signals = [p for p in processes if "H125" in p]

yields_dict = {}

for c in counts:
    cat = c.strip("#").split("#")[1]
    process = c.strip("#").split("#")[2]
    yields_dict.setdefault(cat,{})
    yields_dict[cat][process] = getattr(t,c)
    if process in backgrounds:
        yields_dict[cat].setdefault("BG",0.0)
        yields_dict[cat]["BG"] += getattr(t,c)
    elif process in signals:
        yields_dict[cat].setdefault("H125",0.0)
        yields_dict[cat]["H125"] += getattr(t,c)


soverb_dict = {}
signals = signals + ["H125"]
for sig in signals:
    soverb_dict[sig] = {}
    for var in variables:
        for cg, cl in zip(categories_greater[var],categories_less[var]):
            soverb_dict[sig].setdefault(var,{"greater" : [], "less" : []})
            denominator = math.sqrt(max(0,yields_dict[cg][sig]) + max(0,yields_dict[cg]["BG"]))
            if denominator > 0:
                soverb_greater = yields_dict[cg][sig]/denominator
            else:
                soverb_greater = 0
            denominator = math.sqrt(max(0,yields_dict[cl][sig]) + max(0,yields_dict[cl]["BG"]))
            if denominator > 0:
                soverb_less = yields_dict[cl][sig]/denominator
            else:
                soverb_less = 0
            soverb_dict[sig][var]["greater"].append(soverb_greater)
            soverb_dict[sig][var]["less"].append(soverb_less)


if not os.path.exists("cutscans"):
    os.mkdir("cutscans")

channel_dict = {
    "ee": "ee",
    "em": "e#mu",
    "et": "e#tau_{h}",
    "mm": "#mu#mu",
    "mt": "#mu#tau_{h}",
    "tt": "#tau_{h}#tau_{h}"
}

for ch in channel_dict:
    if not os.path.exists("cutscans/%s"%ch):
        os.mkdir("cutscans/%s"%ch)
    for sig in signals:
        if not os.path.exists("cutscans/%s/%s"%(ch,sig)):
            os.mkdir("cutscans/%s/%s"%(ch,sig))

for sig in signals:
    for var in soverb_dict[sig]:
        channel = var.split("_")[0]
        variable_name = var.replace(channel+"_","",1)
        print channel, variable_name
        width = 600
        plot = dd.Plot(
            [], "ModTDR", r=0.04, l=0.14, width=width)
        cuts_less = r.TGraph(len(cutvalues[var]), np.array(cutvalues[var]), np.array(soverb_dict[sig][var]["less"]))
        cuts_greater = r.TGraph(len(cutvalues[var]), np.array(cutvalues[var]), np.array(soverb_dict[sig][var]["greater"]))
        plot.add_graph(cuts_less, "cuts_less")
        plot.add_graph(cuts_greater, "cuts_greater")
        plot.setGraphStyle("cuts_less", "L", linecolor=r.kBlue, linewidth=3, markersize=0)
        plot.setGraphStyle("cuts_greater", "L", linecolor=r.kRed, linewidth=3, markersize=0)
        plot.subplot(0).setXlims(cutvalues[var][0], cutvalues[var][-1])
        plot.subplot(0).setYlims(0.0,1.4*max(soverb_dict[sig][var]["less"]+soverb_dict[sig][var]["greater"]))
        var_label = styles.x_label_dict[channel].get(variable_name, variable_name)
        plot.subplot(0).setXlabel("Cut on "+var_label)
        plot.subplot(0).setYlabel("S/#sqrt{S + B}")
        plot.scaleYLabelSize(0.8)
        plot.scaleYTitleOffset(1.0)
        plot.subplot(0).Draw(["cuts_less", "cuts_greater"])
        # create legends
        plot.add_legend(width=0.35, height=0.15, pos=2)
        var_label = variable_name
        plot.legend(0).add_entry(0, "cuts_less", "%s < cut"%var_label, 'l')
        plot.legend(0).add_entry(0, "cuts_greater", "%s > cut"%var_label, 'l')
        plot.legend(0).Draw()

        # draw additional labels
        plot.DrawCMS()
        era = "2017"
        if "2016" in era:
            plot.DrawLumi("35.9 fb^{-1} (2016, 13 TeV)")
        elif "2017" in era:
            plot.DrawLumi("41.5 fb^{-1} (2017, 13 TeV)")
        plot.DrawText(0.72,0.82,"#splitline{S = %s}{B = total BG}"%sig)

        posChannelCategoryLabelLeft = None
        plot.DrawChannelCategoryLabel(
            "%s, %s" % (channel_dict[channel], "inclusive"),
            begin_left=posChannelCategoryLabelLeft)

        # save plot
        plot.save("cutscans/%s/%s/%s_soverb_cutscan.%s" % (channel, sig, var, "pdf"))
        plot.save("cutscans/%s/%s/%s_soverb_cutscan.%s" % (channel, sig, var, "png"))
