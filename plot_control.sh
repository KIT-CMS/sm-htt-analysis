for ch in mt et tt em;
do
    for v in m_vis ptvis ME_D ME_vbf ME_z2j_1 ME_z2j_2 ME_q2v1 ME_q2v2 ME_phi1 ME_phi ME_costheta1 ME_costheta2 ME_costhetastar njets jpt_1 jpt_2 jeta_1 jeta_2 met pt_1 pt_2 eta_1 eta_2 mjj jdeta dijetpt mt_1 mt_2 pt_tt pt_ttjj nbtag bpt_1 bpt_2 beta_1 beta_2;
    do
        plotting/plot_shapes_control.py -l -c ${ch} --era Run2017 --input shapes_${ch}.root --control-variable ${v} --categories ${ch}_${v}
    done
done
#for ch in mt et tt em;
#do
#    for v in m_vis ptvis ME_D ME_vbf ME_z2j_1 ME_z2j_2 ME_q2v1 ME_q2v2 ME_phi1 ME_phi ME_costheta1 ME_costheta2 ME_costhetastar njets jpt_1 jpt_2 jeta_1 jeta_2 met pt_1 pt_2 eta_1 eta_2 mjj jdeta dijetpt mt_1 mt_2 pt_tt pt_ttjj nbtag bpt_1 bpt_2 beta_1 beta_2;
##   for v in m_vis;
#    do
#        plotting/plot_shapes_control.py -l -c ${ch} --era Run2017 --input shapes_${ch}.root --control-variable ${v} --categories ${ch}_${v} --embedding --fake-factor
#    done
#done
