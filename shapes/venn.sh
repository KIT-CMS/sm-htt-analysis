#!/bin/bash

# How to use: ./shapes/venn_count.sh CHANNEL CUT16043 CUT18032

echo ">>> ET, qqH:"
./shapes/venn_count.sh et "(m_sv>95)*(m_sv<135)*(mjj>1100)*(mjj<1500)+(m_sv>115)*(m_sv<155)*(mjj>1500)" "(et_max_index==1)*(et_max_score>0.8)"
echo

echo ">>> MT, qqH:"
./shapes/venn_count.sh mt "(m_sv>115)*(m_sv<155)*(mjj>1100)" "(mt_max_index==1)*(mt_max_score>0.8)"
echo

echo ">>> TT, qqH:"
./shapes/venn_count.sh tt "(m_sv>110)*(m_sv<130)*(mjj>500)*(mjj<800)+(m_sv>110)*(m_sv<150)*(mjj>800)" "(tt_max_index==1)*(tt_max_score>0.8)"
echo

echo ">>> ET, ggH:"
./shapes/venn_count.sh et "(m_sv>110)*(m_sv<140)*(pt_tt>250)" "(et_max_index==0)*(et_max_score>0.5)"
echo

echo ">>> MT, ggH:"
./shapes/venn_count.sh mt "(m_sv>110)*(m_sv<140)*(pt_tt>300)" "(mt_max_index==0)*(mt_max_score>0.5)"
echo

echo ">>> TT, ggH:"
./shapes/venn_count.sh tt "(m_sv>110)*(m_sv<130)*(pt_tt>170)" "(tt_max_index==0)*(tt_max_score>0.5)"
echo
