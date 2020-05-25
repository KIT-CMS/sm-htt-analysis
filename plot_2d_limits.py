import ROOT
from array import array
import json
import CombineHarvester.CombineTools.plotting as plot
import argparse

ROOT.gROOT.SetBatch(True)

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="plot 2d limits")
    parser.add_argument(
        "--channel", "-c" , help="channel")
    parser.add_argument(
        "--variable", "-v", help="variables")
    parser.add_argument(
        "--output", "-o", help="output dir")
    return parser.parse_args()


def main(args):
    channel = args.channel
    variable = args.variable
    mass_dict = {
        "heavy_mass": [240, 280, 320, 360, 400, 450, 500, 550, 600, 700, 800, 900, 1000, 1200, 1400, 1600, 1800, 2000, 2500, 3000],
        "light_mass_coarse": [60, 70, 80, 90, 100, 120, 150, 170, 190, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1600, 1800, 2000, 2200, 2400, 2600, 2800],
        "light_mass_fine": [60, 70, 75, 80, 85, 90, 95, 100, 110, 120, 130, 150, 170, 190, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850],
    }
    binedges_heavy = [0.]*(len(mass_dict["heavy_mass"])+1)

    for i in range(len(mass_dict["heavy_mass"])+1):
        if i==0:
            binedges_heavy[i] = 220.
        elif i==(len(mass_dict["heavy_mass"])):
            binedges_heavy[i] = 3250.
        else:
            binedges_heavy[i] = mass_dict["heavy_mass"][i-1] + 0.5*(mass_dict["heavy_mass"][i]-mass_dict["heavy_mass"][i-1])

    light_masses_all = mass_dict["light_mass_fine"]+mass_dict["light_mass_coarse"][mass_dict["light_mass_coarse"].index(900):]
    only_fine = []

    for mass in light_masses_all:
        if mass not in mass_dict["light_mass_coarse"]:
            only_fine.append(mass)
    binedges_light = [0.]*(len(light_masses_all)+1)

    for i in range(len(light_masses_all)+1):
        if i==0:
            binedges_light[i] = 55.
        elif i==(len(light_masses_all)):
            binedges_light[i] = 2900.
        else:
            binedges_light[i] = light_masses_all[i-1] + 0.5*(light_masses_all[i]-light_masses_all[i-1])

    hist = ROOT.TH2F("hist","", len(binedges_heavy)-1,  array("d",binedges_heavy), len(binedges_light)-1, array("d",binedges_light))
    xaxis = hist.GetXaxis()
    yaxis = hist.GetYaxis()
    theory_diff_hist = hist.Clone("theory_diff")
    theory_file=ROOT.TFile("HXSG_NMSSM_recommendations_00.root","READ")
    theory_graph = theory_file.Get("g_bbtautau")

    for mass in mass_dict["heavy_mass"]:
        theory_diff_value = theory_graph.Eval(mass)
        json_file = "nmssm_{}_{}_{}_cmb.json".format(channel,variable,mass)
        with open(json_file,"r") as read_file:
            limit_dict = json.load(read_file)
        x_bin = xaxis.FindBin(mass)
        for key in limit_dict.keys():
            if "exp0" not in limit_dict[key].keys():
                continue
            y_bin = yaxis.FindBin(float(key))
            hist.SetBinContent(x_bin,y_bin,limit_dict[key]["exp0"])
            if (mass>399 and mass<1001):
                theory_diff_hist.SetBinContent(x_bin,y_bin,limit_dict[key]["exp0"]/theory_diff_value)

        if mass>1001:
            for lm in only_fine:
                y_bin = yaxis.FindBin(float(lm))
                hist.SetBinContent(x_bin,y_bin,hist.GetBinContent(x_bin,y_bin-1))


    ## Boilerplate
    # ROOT.PyConfig.IgnoreCommandLineOptions = True
    # ROOT.gROOT.SetBatch(ROOT.kTRUE)
    # plot.ModTDRStyle()
    ROOT.gStyle.SetNdivisions(510, 'XYZ') # probably looks better
    ROOT.gStyle.SetCanvasDefW(900)
    ROOT.gStyle.SetCanvasDefH(600)

    channel_label = {"mt": "#mu#tau_{h}",
                "tt": "#tau_{h}#tau_{h}",
                "et":  "e#tau_{h}",
                "em": "e#mu_{}",
                "all": "e#tau_{h}+#mu#tau_{h}+#tau_{h}#tau_{h}"
                }
    variable_label = {"mbb": "m_{bb}",
                "m_sv_puppi": "m_{#tau#tau (SV-Fit)}",
                "m_ttvisbb":  "m_{#tau#tau(vis)bb}",
                "nmssm_discriminator": "3D discriminator",
                "mt_max_score": "NN Score",
                "et_max_score": "NN Score",
                "tt_max_score": "NN Score",
                "em_max_score": "NN Score",

                }
    c1 = ROOT.TCanvas()
    c1.cd()

    c1.SetRightMargin(0.15)
    hist.SetStats(0)

    ROOT.gStyle.SetOptStat(0)

    hist.GetZaxis().SetTitle("#scale[0.95]{95% CL limit on #sigma#font[42]{(gg#rightarrow H)}#upoint#font[52]{B}#font[42]{(H#rightarrow hh')}#upoint#font[52]{B}#font[42]{(h#rightarrow#tau#tau)}#upoint#font[52]{B}#font[42]{(h'#rightarrow bb)}(pb)}")
    hist.GetXaxis().SetTitle("Heavy Mass m_{H} (GeV)")
    hist.GetXaxis().SetNoExponent()
    hist.GetYaxis().SetNoExponent()
    hist.GetZaxis().SetNoExponent()
    hist.GetYaxis().SetTitle("Light Mass m_{h'} (GeV)")
    hist.GetZaxis().SetRangeUser(0.001,20.)

    c1.SetLogz()
    c1.SetLogx()
    c1.SetLogy()
    # hist.GetZaxis().SetRangeUser(0.002,1.2)
    # hist.GetXaxis().SetRangeUser(280.,3250.)
    # hist.GetYaxis().SetRangeUser(60.,2920.)

    hist.Draw("COLZ")

    c1.RedrawAxis()
    c1.RedrawAxis("g")
    plot.DrawCMSLogo(c1, 'CMS', "Own Work", 11, 0.045, 0.035, 1.2, '', 0.8)
    plot.DrawTitle(c1,"35.9 fb^{-1} (2016, 13 TeV)",3)
    plot.DrawTitle(c1,channel_label[channel]+": "+variable_label[variable],1)
    # ROOT.gPad.GetFrame().Draw("SAME")
    ROOT.gStyle.SetPalette(53)
    ROOT.gPad.RedrawAxis()
    # c1.GetFrame().Draw("same")
    c1.SaveAs("{}/{}_{}_2d.pdf".format(args.output,channel,variable))
    c1.SaveAs("{}/{}_{}_2d.png".format(args.output,channel,variable))

    c2 = ROOT.TCanvas()
    c2.cd()

    c2.SetRightMargin(0.15)

    theory_diff_hist.SetStats(0)

    ROOT.gStyle.SetOptStat(0)

    theory_diff_hist.GetZaxis().SetTitle("95% CL limit on #sigma #times BR expected / #sigma #times BR allowed by theory")
    theory_diff_hist.GetXaxis().SetTitle("Heavy Mass m_{H} (GeV)")
    theory_diff_hist.GetXaxis().SetNoExponent()
    theory_diff_hist.GetYaxis().SetNoExponent()
    theory_diff_hist.GetZaxis().SetNoExponent()
    theory_diff_hist.GetYaxis().SetTitle("Light Mass m_{h'} (GeV)")
    theory_diff_hist.GetZaxis().SetRangeUser(0.5,1000.)

    c2.SetLogz()
    c2.SetLogx()
    c2.SetLogy()

    theory_diff_hist.Draw("COLZ")

    c2.RedrawAxis()
    c2.RedrawAxis("g")
    plot.DrawCMSLogo(c2, 'CMS', "Own Work", 11, 0.045, 0.035, 1.2, '', 0.8)
    plot.DrawTitle(c2,"35.9 fb^{-1} (2016, 13 TeV)",3)
    plot.DrawTitle(c2,channel_label[channel]+": "+variable_label[variable],1)
    # ROOT.gPad.GetFrame().Draw("SAME")
    ROOT.gStyle.SetPalette(53)
    ROOT.gPad.RedrawAxis()
    # c2.GetFrame().Draw("same")
    c2.SaveAs("{}/{}_{}_2d_theory.pdf".format(args.output,channel,variable))
    c2.SaveAs("{}/{}_{}_2d_theory.png".format(args.output,channel,variable))



if __name__ == "__main__":
    args = parse_arguments()
    main(args)
