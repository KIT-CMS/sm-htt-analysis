import ROOT as r

channels = ["mt", "et", "em"]

files = {}
for ch in channels:
    files[ch] = r.TFile.Open("countshww_%s_2017.root"%ch,"read")

counts_dict = {}
for ch,f in files.items():
    tree = f.Get("output_tree")
    tree.GetEntry(0)
    counts = [(k.GetName(), getattr(tree,k.GetName())) for k in tree.GetListOfLeaves() ]
    for count in counts:
        name_list = count[0].strip("#").split("#")
        counts_dict.setdefault(name_list[1],{}) 
        counts_dict[name_list[1]][name_list[2]] = count[1]

for ch in channels:
    print "Channel:",ch
    print "\tLoss HWW old: ", (1.0 - counts_dict["%s_hww_old"%ch]["HWW"]/counts_dict["%s_inclusive"%ch]["HWW"])
    print "\tLoss HWW new: ", (1.0 - counts_dict["%s_hww_new"%ch]["HWW"]/counts_dict["%s_inclusive"%ch]["HWW"])
    print "\tLoss ggH old: ", (1.0 - counts_dict["%s_htautau_old"%ch]["ggH125"]/counts_dict["%s_inclusive"%ch]["ggH125"])
    print "\tLoss ggH new: ", (1.0 - counts_dict["%s_htautau_new"%ch]["ggH125"]/counts_dict["%s_inclusive"%ch]["ggH125"])
    print "\tLoss qqH old: ", (1.0 - counts_dict["%s_htautau_old"%ch]["qqH125"]/counts_dict["%s_inclusive"%ch]["qqH125"])
    print "\tLoss qqH new: ", (1.0 - counts_dict["%s_htautau_new"%ch]["qqH125"]/counts_dict["%s_inclusive"%ch]["qqH125"])
