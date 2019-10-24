import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import numpy as np
import argparse
import json
import matplotlib.colors as colors

parser = argparse.ArgumentParser()
parser.add_argument(
    'input', nargs='+', help="""Input json files""")
args = parser.parse_args()
nmssm_heavy_masses = [320,450,700,800,900,1000]
input_files = []
for mH in nmssm_heavy_masses:
    input_files.append("nmssm_all_{}_cmb.json".format(mH))
nmssm_low_masses = [60, 70, 75, 80, 85, 90, 95, 100, 110, 120, 130, 150, 170, 190, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850]
x = np.linspace(200,1100,30)
y = np.linspace(20,900,180)
yticks = []
dx=x[1]-x[0]
dy=y[1]-y[0]
high_masses = []
min_ = 1e10
limits = np.full((len(x),len(y)),0.0)
for src in input_files:
    for i in range(len(x)-1):
        with open(src) as json_file:
            data = json.load(json_file)
        if float(src.split("_")[2]) > x[i] and float(src.split("_")[2]) < x[i+1]:
            yticks.append((x[i+1]+x[i])/2.0)
            for j in range(len(y)-1):
                for mass in data.keys():
                    if float(mass) > y[j] and float(mass) > y[j+1]:
                        limits[i,j] = data[mass]["exp0"]
                        if data[mass]["exp0"]<min_:
                            min_ = data[mass]["exp0"]

cmap = colors.LinearSegmentedColormap.from_list("n", ["forestgreen","gold"])
cmap.set_under('w')
fig, ax = plt.subplots()
c = ax.pcolormesh(y, x, limits, vmin = min_, cmap="Blues", norm=colors.LogNorm(vmin=min_, vmax=limits.max()))

ax.axis([ y.min(), y.max(), x.min(), x.max()])
cbar = fig.colorbar(c, ax=ax, ticks = [np.round(min_,decimals=3),0.1,0.2,0.5,1.0,np.round(limits.max(),decimals=2)])
cbar.set_label("95% CL limit")
cbar.ax.set_yticklabels([np.round(min_,decimals=3),0.1,0.2,0.5,1.0,np.round(limits.max(),decimals=2)])
plt.yticks(yticks,nmssm_heavy_masses)
plt.xticks(nmssm_low_masses)

plt.xscale("log")
xlin = np.linspace(20,900,10000)
ylin = xlin+125.0
# plt.plot(xlin,ylin)
plt.fill_between(xlin,ylin,alpha=0.5,color='gray')
plt.xlabel(r"$\rm{m}_{h^{l}}$ (GeV)")
plt.ylabel(r"$\rm{m}_{\rm{H}}$ (GeV)")

plt.savefig("2D_limit.png")
plt.savefig("2D_limit.pdf")


# fig, ax = plt.subplots()

# cf = ax.contourf(y + dy/2.,
#                   x + dx/2., limits,
#                   cmap='Blues')
# fig.colorbar(cf, ax=ax)

# plt.savefig("2D_limit_contour.png")
# plt.savefig("2D_limit_contour.pdf")
