source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh

ERA=$1

v="m_vis,ptvis,m_sv_puppi,pt_sv_puppi,eta_sv_puppi,ME_q2v1,ME_q2v2,njets,jpt_1,jpt_2,jeta_1,jeta_2,pt_1,pt_2,eta_1,eta_2,mjj,jdeta,dijetpt,puppimet,mt_1_puppi,mt_2_puppi,pt_tt_puppi,pZetaPuppiMissVis,pt_ttjj_puppi,mTdileptonMET_puppi,nbtag,bpt_1,bpt_2,beta_1,beta_2"
ch="mt,et,tt,em"
plotting/plot_shapes_control.py -l  --era Run${ERA} --input default_shapes/shapes.root --variables ${v} --channels ${ch} --embedding --fake-factor
plotting/plot_shapes_control.py -l  --era Run${ERA} --input default_shapes/shapes.root --variables ${v} --channels ${ch} --fake-factor
# plotting/plot_shapes_control.py -l  --era Run2017 --input default_shapes/shapes.root --variables ${v} --channels ${ch} --embedding
# plotting/plot_shapes_control.py -l  --era Run2017 --input default_shapes/shapes.root --variables ${v} --channels ${ch}

#v="NNrecoil_pt,nnmet,mt_1_nn,mt_2_nn,mt_tot_nn,pt_tt_nn,pZetaNNMissVis,pt_ttjj_nn,mTdileptonMET_nn"
#ch="mt,et,tt,em"
#plotting/plot_shapes_control.py -l  --era Run2017 --input shapes.root --variables ${v} --channels ${ch} --embedding --fake-factor
#plotting/plot_shapes_control.py -l  --era Run2017 --input shapes.root --variables ${v} --channels ${ch} --fake-factor
#plotting/plot_shapes_control.py -l  --era Run2017 --input shapes.root --variables ${v} --channels ${ch} --embedding
#plotting/plot_shapes_control.py -l  --era Run2017 --input shapes.root --variables ${v} --channels ${ch}

# v="m_vis,m_vis_high,ptvis,met,puppimet,metParToZ,metPerpToZ,puppimetParToZ,puppimetPerpToZ,pt_1,pt_2,eta_1,eta_2,njets,jpt_1,jpt_2,jeta_1,jeta_2"
# ch="mm"
# plotting/plot_shapes_control.py -l  --era Run2017 --input shapes.root --variables ${v} --channels ${ch}
# plotting/plot_shapes_control.py -l  --era Run2017 --input shapes.root --variables ${v} --channels ${ch} --category-postfix "peak"
