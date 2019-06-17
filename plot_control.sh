source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh

v="m_vis,ptvis,m_sv,pt_sv,eta_sv,m_fastmtt,pt_fastmtt,eta_fastmtt,ME_D,ME_vbf,ME_z2j_1,ME_z2j_2,ME_q2v1,ME_q2v2,ME_costheta1,ME_costheta2,ME_costhetastar,ME_phi,ME_phi1,njets,jpt_1,jpt_2,jeta_1,jeta_2,pt_1,pt_2,eta_1,eta_2,mjj,jdeta,dijetpt,met,mt_1,mt_2,pt_tt,pZetaMissVis,pt_ttjj,mt_tot,mTdileptonMET,puppimet,mt_1_puppi,mt_2_puppi,pt_tt_puppi,pZetaPuppiMissVis,pt_ttjj_puppi,mt_tot_puppi,mTdileptonMET_puppi,nbtag,bpt_1,bpt_2,beta_1,beta_2,DiTauDeltaR,m_sv_puppi,pt_sv_puppi,eta_sv_puppi,m_fastmtt_puppi,pt_fastmtt_puppi,eta_fastmtt_puppi"
ch="mt,et,tt,em"
plotting/plot_shapes_control.py -l  --era Run2017 --input default_shapes/shapes.root --variables ${v} --channels ${ch} --embedding --fake-factor
plotting/plot_shapes_control.py -l  --era Run2017 --input default_shapes/shapes.root --variables ${v} --channels ${ch} --fake-factor
plotting/plot_shapes_control.py -l  --era Run2017 --input default_shapes/shapes.root --variables ${v} --channels ${ch} --embedding
plotting/plot_shapes_control.py -l  --era Run2017 --input default_shapes/shapes.root --variables ${v} --channels ${ch}

#v="NNrecoil_pt,nnmet,mt_1_nn,mt_2_nn,mt_tot_nn,pt_tt_nn,pZetaNNMissVis,pt_ttjj_nn,mTdileptonMET_nn"
#ch="mt,et,tt,em"
#plotting/plot_shapes_control.py -l  --era Run2017 --input shapes.root --variables ${v} --channels ${ch} --embedding --fake-factor
#plotting/plot_shapes_control.py -l  --era Run2017 --input shapes.root --variables ${v} --channels ${ch} --fake-factor
#plotting/plot_shapes_control.py -l  --era Run2017 --input shapes.root --variables ${v} --channels ${ch} --embedding
#plotting/plot_shapes_control.py -l  --era Run2017 --input shapes.root --variables ${v} --channels ${ch}

v="m_vis,m_vis_high,ptvis,met,puppimet,metParToZ,metPerpToZ,puppimetParToZ,puppimetPerpToZ,pt_1,pt_2,eta_1,eta_2,njets,jpt_1,jpt_2,jeta_1,jeta_2"
ch="mm"
plotting/plot_shapes_control.py -l  --era Run2017 --input shapes.root --variables ${v} --channels ${ch}
plotting/plot_shapes_control.py -l  --era Run2017 --input shapes.root --variables ${v} --channels ${ch} --category-postfix "peak"
