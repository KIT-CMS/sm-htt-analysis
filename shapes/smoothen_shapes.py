import ROOT
import sys
import argparse

ROOT.gROOT.SetBatch()

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Convert shapes from the shape producer to the sync format."
    )

    parser.add_argument("--era", type=str, help="Experiment era.")
    parser.add_argument(
        "--channels",
        default=[],
        nargs='+',
        type=str,
        choices=['em', 'et', 'mt', 'tt'],
        help="Channels to be considered.")
    return parser.parse_args()

window = [0.0, 1.0]
def fline(x, par):
    if (x[0] < window[0] or x[0] > window[1]):
        ROOT.TF1.RejectPoint()
        return 0
    return par[0] + par[1]*x[0]

def main(args):
    categories = {
        "em" : ["ggh", "ggh_unrolled", "qqh", "qqh_unrolled", "misc", "ss", "st", "tt", "vv", "ztt"],
        "et" : ["ggh", "ggh_unrolled", "qqh", "qqh_unrolled", "ztt", "zll", "tt", "w", "ss", "misc"],
        "mt" : ["ggh", "ggh_unrolled", "qqh", "qqh_unrolled", "ztt", "zll", "tt", "w", "ss", "misc"],
        "tt" : ["ggh", "ggh_unrolled", "qqh", "qqh_unrolled", "ztt", "noniso", "misc"]
        }

    for channel in args.channels:
        print channel
        rootfile = ROOT.TFile("htt_{ch}.inputs-sm-Run{era}-ML.root".format(ch=channel, era=args.era), "UPDATE")
        for category in categories[channel]:
            print "- "+category
            directory = "{ch}_{cat}".format(ch=channel, cat=category)
            key_list = rootfile.Get(directory).GetListOfKeys()
            rootfile.cd(directory)
            for entry in key_list:
                key = entry.GetName()
                if "scale_j_" in key or "scale_met" in key:
                    if key.startswith("em_"):
                        continue
                    hist_unc = rootfile.Get(directory+"/"+key)
                    if channel == "em":
                        hist_unc.SetName(key)
                    hist_nom = rootfile.Get(directory+"/"+key.split("_CMS")[0])
                    hist_ratio = hist_unc.Clone("ratio")
                    nbins = hist_nom.GetNbinsX()
                    for i in range(nbins):
                        nom_content = hist_nom.GetBinContent(i+1)
                        if nom_content==0.0:
                            hist_ratio.SetBinContent(i+1, 1.0)
                            hist_ratio.SetBinError(i+1, 10.0)
                        else:
                            hist_ratio.SetBinContent(i+1, hist_unc.GetBinContent(i+1)/nom_content)
                            hist_ratio.SetBinError(i+1, max(hist_unc.GetBinError(i+1), hist_nom.GetBinError(i+1))/nom_content)
                            '''if hist_unc.GetBinContent(i+1)<1.0:
                                hist_ratio.SetBinError(i+1, 1.0)
                            else:
                                hist_ratio.SetBinError(i+1, hist_unc.GetBinError(i+1)/nom_content)'''
                    hist_range = [hist_nom.GetBinLowEdge(1), hist_nom.GetBinLowEdge(nbins)+hist_nom.GetBinWidth(nbins)]
                    ranges = []
                    if "unrolled" in category:
                        if "ggh" in category:
                            unit_length = (hist_range[1]-hist_range[0])/11.0 if channel=="em" else (hist_range[1]-hist_range[0])/9.0
                            for i in range(9):
                                ranges.append([hist_range[0]+i*unit_length, hist_range[0]+(i+1)*unit_length])
                        if "qqh" in category:
                            unit_length = (hist_range[1]-hist_range[0])/5.0
                            for i in range(5):
                                ranges.append([hist_range[0]+i*unit_length, hist_range[0]+(i+1)*unit_length])
                    else:
                        ranges.append(hist_range)
                        
                    
                    #c1=ROOT.TCanvas()
                    #hist_ratio.Draw()
                    #hist_nom.Draw("same")
                    #c1.SaveAs("hist1.png")
                    for subrange in ranges:
                        window[0] = subrange[0]
                        window[1] = subrange[1]
                        func = ROOT.TF1("fline",fline,0,9,2)
                        func.SetParameters(1.0,0.0)      
                        hist_ratio.Fit("fline", "q0") #q0
                        for i in range(nbins):
                            if hist_ratio.GetBinCenter(i+1) > subrange[0] and hist_ratio.GetBinCenter(i+1) < subrange[1]:
                                hist_unc.SetBinContent(i+1, func.Eval(hist_ratio.GetBinCenter(i+1))*hist_nom.GetBinContent(i+1))
                                hist_ratio.SetBinContent(i+1, func.Eval(hist_ratio.GetBinCenter(i+1)))
                    #hist_ratio.Draw()
                    #hist_nom.Draw("same")
                    #c1.SaveAs("hist2.png")
                    hist_unc.Write()
                    #break
            #break
        
        rootfile.Close()


if __name__ == "__main__":
    args = parse_arguments()
    main(args)
                          
                          
                     
