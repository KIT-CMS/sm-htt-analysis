#!/bin/bash

# How to use: ./shapes/venn_count.sh CHANNEL CUT16043 CUT18032

# See HIG16043: https://arxiv.org/pdf/1708.00373.pdf

ET_0JET="(njets==0)"
ET_VBF="(njets>=2)*(mjj>300)*(pt_tt>50)"
ET_BOOSTED="(${ET_0JET}==0)*(${ET_VBF}==0)"

MT_0JET="(njets==0)"
MT_VBF="(njets>=2)*(mjj>300)*(pt_tt>50)*(pt_2>40)"
MT_BOOSTED="(${MT_0JET}==0)*(${MT_VBF}==0)"

TT_0JET="(njets==0)"
TT_VBF="(njets>=2)*(pt_tt>100)*(jdeta>2.5)"
TT_BOOSTED="(${TT_0JET}==0)*(${TT_VBF}==0)"

echo ">>> ET, qqH:"
./shapes/venn_count.sh et "((m_sv>115)*(m_sv<135)*(mjj>700)*(mjj<1100)+(m_sv>95)*(m_sv<135)*(mjj>1100)*(mjj<1500)+(m_sv>115)*(m_sv<155)*(mjj>1500))*${ET_VBF}" "(et_max_index==1)*(et_max_score>0.8)"
echo

echo ">>> MT, qqH:"
./shapes/venn_count.sh mt "((m_sv>115)*(m_sv<155)*(mjj>1100))*${MT_VBF}" "(mt_max_index==1)*(mt_max_score>0.8)"
echo

echo ">>> TT, qqH:"
./shapes/venn_count.sh tt "((m_sv>110)*(m_sv<130)*(mjj>300)*(mjj<800)+(m_sv>110)*(m_sv<150)*(mjj>800))*${TT_VBF}" "(tt_max_index==1)*(tt_max_score>0.8)"
echo

echo ">>> ET, ggH:"
./shapes/venn_count.sh et "((m_sv>110)*(m_sv<140)*(pt_tt>250))*${ET_BOOSTED}" "(et_max_index==0)*(et_max_score>0.5)"
echo

echo ">>> MT, ggH:"
./shapes/venn_count.sh mt "((m_sv>110)*(m_sv<140)*((pt_tt>300)+(pt_tt>0)*(pt_tt<100)+(pt_tt>150)*(pt_tt<200)))*${MT_BOOSTED}" "(mt_max_index==0)*(mt_max_score>0.5)"
echo

echo ">>> TT, ggH:"
./shapes/venn_count.sh tt "((m_sv>110)*(m_sv<150))*${TT_BOOSTED}" "(tt_max_index==0)*(tt_max_score>0.5)"
echo
