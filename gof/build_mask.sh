#!/usr/bin/env bash
function buildCategories () {
    MODE=$1
    TAG=$2
    ERA=$3
    CHANNEL=$4
    SIGNALS=$5
    # echo "Constructing background Categories with settings:"
    # echo "Mode:     ${MODE}"
    # echo "Tag:      ${TAG}"
    # echo "Era :     ${ERA}"
    # echo "Channel:  ${CHANNEL}"
    # echo "Signals:  ${SIGNALS}"
    if [[ $TAG == *"stage1p1"* ]]; then
        if [[ "$CHANNEL" == "em" ]]; then
            catlist=("100" "101" "102" "103" "104" "200" "201" "202" "203" "13" "14" "16" "19" "20")
        elif [[ "$CHANNEL" == "et" ]]; then
            catlist=("100" "101" "102" "103" "104" "200" "201" "202" "203" "13" "15" "16" "20" "21")
        elif [[ "$CHANNEL" == "mt" ]]; then
            catlist=("100" "101" "102" "103" "104" "200" "201" "202" "203" "13" "15" "16" "20" "21")
        elif [[ "$CHANNEL" == "tt" ]]; then
            catlist=("100" "101" "102" "103" "104" "200" "201" "202" "203" "16" "20" "21")
        elif [[ "$CHANNEL" == "cmb" ]]; then
            catlist=("100" "101" "102" "103" "104" "200" "201" "202" "203" "13" "14" "15" "16" "19" "20" "21")
        fi
        signallist=("100" "101" "102" "103" "104" "200" "201" "202" "203")
    elif [[ $TAG == *"stage0"* ]]; then
        if [[ "$CHANNEL" == "em" ]]; then
            catlist=("1" "13" "14" "16" "19" "20")
        elif [[ "$CHANNEL" == "et" ]]; then
            catlist=("1" "13" "15" "16" "20" "21")
        elif [[ "$CHANNEL" == "mt" ]]; then
            catlist=("1" "13" "15" "16" "20" "21")
        elif [[ "$CHANNEL" == "tt" ]]; then
            catlist=("1" "16" "20" "21")
        elif [[ "$CHANNEL" == "cmb" ]]; then
            catlist=("1" "13" "14" "15" "16" "19" "20" "21")
        fi
        signallist=("1")
    fi
    if [[ $MODE == *"15node"* ]]; then
        if [[ "$CHANNEL" == "em" ]]; then
            catlist=("100" "101" "102" "103" "104" "105" "106" "107" "108" "109" "110" "200" "201" "202" "203" "13" "14" "16" "19" "20")
        elif [[ "$CHANNEL" == "et" ]]; then
            catlist=("100" "101" "102" "103" "104" "105" "106" "107" "108" "109" "110" "200" "201" "202" "203" "13" "15" "16" "20" "21")
        elif [[ "$CHANNEL" == "mt" ]]; then
            catlist=("100" "101" "102" "103" "104" "105" "106" "107" "108" "109" "110" "200" "201" "202" "203" "13" "15" "16" "20" "21")
        elif [[ "$CHANNEL" == "tt" ]]; then
            catlist=("100" "101" "102" "103" "104" "105" "106" "107" "108" "109" "110" "200" "201" "202" "203" "16" "20" "21")
        elif [[ "$CHANNEL" == "cmb" ]]; then
            catlist=("100" "101" "102" "103" "104" "105" "106" "107" "108" "109" "110" "200" "201" "202" "203" "13" "14" "15" "16" "19" "20" "21")
        fi
        signallist=("100" "101" "102" "103" "104" "105" "106" "107" "108" "109" "110" "200" "201" "202" "203")
    fi
    backlist=($(echo ${catlist[@]} ${signallist[@]} | tr ' ' '\n' | sort | uniq -u | tr '\n' ' ' ))
    # echo "backlist:   ${backlist}"
    # echo "signallist: ${signallist}"
    # echo "catlist:    ${catlist}"
    if [[ $SIGNALS == "backgrounds" ]]; then
        echo $backlist
    elif [[ $SIGNALS == "signals" ]]; then
        echo $signallist
    elif [[ $SIGNALS == "categories" ]]; then
        echo $catlist
    fi
}

function buildMask () {
    MODE=$1
    TAG=$2
    ERA=$3
    CHANNEL=$4
    CATEGORY=$5
    tempmask=""
    finalmask=""
    backlist=($(buildCategories $MODE $TAG $ERA $CHANNEL "backgrounds"))
    signallist=($(buildCategories $MODE $TAG $ERA $CHANNEL "signals"))
    catlist=($(buildCategories $MODE $TAG $ERA $CHANNEL "categories"))

    # echo "Constructing tempmask with settings:"
    # echo "Mode:     ${MODE}"
    # echo "Tag:      ${TAG}"
    # echo "Era :     ${ERA}"
    # echo "Channel:  ${CHANNEL}"
    # echo "Category:  ${CATEGORY}"
    # echo "backlist:   ${backlist}"
    # echo "signallist: ${signallist}"
    # echo "catlist:    ${catlist}"
    # special case; cat == 999, meaning all backgrounds combined gof test
    if [[ $CHANNEL == *"cmb"* ]]; then
        if [[ $ERA == *"all"* ]]; then
            for y in "2016" "2017" "2018"; do
                for c in "et" "mt" "tt" "em"; do
                    for cat in "${signallist[@]}"; do
                        tempmask+="mask_htt_${c}_${cat}_${y}=1,"
                    done
                    for cat in "${backlist[@]}"; do
                        tempmask+="mask_htt_${c}_${cat}_${y}=0,"
                    done
                done
            done
        else
            for c in "et" "mt" "tt" "em"; do
                for cat in "${signallist[@]}"; do
                    tempmask+="mask_htt_${c}_${cat}_${ERA}=1,"
                done
                for cat in "${backlist[@]}"; do
                    tempmask+="mask_htt_${c}_${cat}_${ERA}=0,"
                done
            done
        fi
        finalmask=${tempmask:0:-1}
    elif [[ $CATEGORY == *"999"* ]]; then
        for cat in "${signallist[@]}"; do
            tempmask+="mask_htt_${CHANNEL}_${cat}_${ERA}=1,"
        done
        for cat in "${backlist[@]}"; do
            tempmask+="mask_htt_${CHANNEL}_${cat}_${ERA}=0,"
        done
    finalmask=${tempmask:0:-1}
    else
        for cat in "${catlist[@]}"; do
            if [ "$cat" != "$CATEGORY" ]; then
                finalmask+="mask_htt_${CHANNEL}_${cat}_${ERA}=1,"
            fi
            done
        finalmask+="mask_htt_${CHANNEL}_${CATEGORY}_${ERA}=0"
    fi
    echo $finalmask
}
