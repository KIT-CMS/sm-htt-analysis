#!/bin/bash

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh

#python quantile-method/CumDistFunc.py -i impact_parameter_shapes.root -o cdf_splines.root -c \
#-s "#ee#ee_d0_e#MC#smhtt#Run2016#d0_1#125#" "#ee#ee_d0_e#data_obs#smhtt#Run2016#d0_1#125#" "#ee#ee_dZ_e#MC#smhtt#Run2016#dZ_1#125#" "#ee#ee_dZ_e#data_obs#smhtt#Run2016#dZ_1#125#" \
#   "#mm#mm_d0_m#MC#smhtt#Run2016#d0_1#125#" "#mm#mm_d0_m#data_obs#smhtt#Run2016#d0_1#125#" "#mm#mm_dZ_m#MC#smhtt#Run2016#dZ_1#125#" "#mm#mm_dZ_m#data_obs#smhtt#Run2016#dZ_1#125#" \
#-n "e_prompt_MC_d0" "e_prompt_data_d0" "e_prompt_MC_dZ" "e_prompt_data_dZ" \
#   "m_prompt_MC_d0" "m_prompt_data_d0" "m_prompt_MC_dZ" "m_prompt_data_dZ"

python quantile-method/CumDistFunc.py -i impact_parameter_shapes.root -o cdf_splines.root -c \
-s "#ee#ee_d0_e#MC#smhtt#Run2016#d0_1#125#" "#ee#ee_d0_e#data_obs#smhtt#Run2016#d0_1#125#" "#ee#ee_dZ_e#MC#smhtt#Run2016#dZ_1#125#" "#ee#ee_dZ_e#data_obs#smhtt#Run2016#dZ_1#125#" \
   "#mm#mm_d0_m#MC#smhtt#Run2016#d0_1#125#" "#mm#mm_d0_m#data_obs#smhtt#Run2016#d0_1#125#" "#mm#mm_dZ_m#MC#smhtt#Run2016#dZ_1#125#" "#mm#mm_dZ_m#data_obs#smhtt#Run2016#dZ_1#125#" \
   "#em#em_d0_em_te#MC#smhtt#Run2016#d0_1#125#" "#em#em_d0_em_te#data_obs#smhtt#Run2016#d0_1#125#" "#em#em_dZ_em_te#MC#smhtt#Run2016#dZ_1#125#" "#em#em_dZ_em_te#data_obs#smhtt#Run2016#dZ_1#125#" \
   "#em#em_d0_em_tm#MC#smhtt#Run2016#d0_2#125#" "#em#em_d0_em_tm#data_obs#smhtt#Run2016#d0_2#125#" "#em#em_dZ_em_tm#MC#smhtt#Run2016#dZ_2#125#" "#em#em_dZ_em_tm#data_obs#smhtt#Run2016#dZ_2#125#" \
-n "e_prompt_MC_d0" "e_prompt_data_d0" "e_prompt_MC_dZ" "e_prompt_data_dZ" \
   "m_prompt_MC_d0" "m_prompt_data_d0" "m_prompt_MC_dZ" "m_prompt_data_dZ" \
   "e_nonprompt_MC_d0" "e_nonprompt_data_d0" "e_nonprompt_MC_dZ" "e_nonprompt_data_dZ" \
   "m_nonprompt_MC_d0" "m_nonprompt_data_d0" "m_nonprompt_MC_dZ" "m_nonprompt_data_dZ"