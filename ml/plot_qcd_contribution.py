#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Dumbledraw.dumbledraw as dd
import Dumbledraw.rootfile_parser_inputshapes as rootfile_parser
import Dumbledraw.styles as styles
import ROOT as R

import logging
logger = logging.getLogger("")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)

# Open file
era = 2016
channel = "tt"

category = "{}_m_sv".format(channel)
rootfile = rootfile_parser.Rootfile_parser("2016_shapes.root", "smhtt", "Run2016", "m_sv", 125)

# Make plot
plot = dd.Plot([], "ModTDR", r=0.04, l=0.15)

# Add backgrounds
bkg_processes = ["ZTT", "W", "ZL", "ZJ", "TTT", "TTL", "TTJ", "VVT", "VVL", "VVJ"]
for process in bkg_processes:
    plot.add_hist(rootfile.get(channel, category, process), process, "bkg")
    plot.setGraphStyle(process, "hist", fillcolor=styles.color_dict[process])
plot.create_stack(bkg_processes, "stack")

# Add data
plot.add_hist(rootfile.get(channel, category, "data_obs"), "data_obs", "data_obs")
plot.setGraphStyle(
    "data_obs",
    "e0",
    markersize=1,
    fillcolor=styles.color_dict["unc"],
    linecolor=1)

# Set up legend
plot.add_legend(width=0.50, height=0.15)
for process in bkg_processes:
    plot.legend(0).add_entry(0, process, styles.legend_label_dict[process], 'f')
plot.legend(0).add_entry(0, "data_obs", "Data", 'PE')
plot.legend(0).setNColumns(3)

# Labels
plot.subplot(0).setXlabel("Di-#tau mass / GeV")
plot.subplot(0).setYlabel("N_{events}")
plot.scaleYTitleOffset(1.08)

# Draw
if channel == 'tt':
    plot.subplot(0).setYlims(0, 5000)
    plot.DrawChannelCategoryLabel("#tau_{h}#tau_{h}")
elif channel == 'mt':
    plot.DrawChannelCategoryLabel("#mu#tau_{h}")
    plot.subplot(0).setYlims(0, 14000)
elif channel == 'et':
    plot.subplot(0).setYlims(0, 7000)
    plot.DrawChannelCategoryLabel("e#tau_{h}")
plot.subplot(0).Draw(["data_obs", "stack"])
plot.legend(0).Draw()
plot.DrawCMS()
if era == 2016:
    plot.DrawLumi("35.9 fb^{-1} (13 TeV)")

# Save
plot.save("{}_plot_qcd.png".format(channel))
plot.save("{}_plot_qcd.pdf".format(channel))
