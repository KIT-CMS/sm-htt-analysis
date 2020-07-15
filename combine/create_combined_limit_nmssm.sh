#!/bin/bash

IFS=',' read -r -a ERAS <<< $1
CHANNEL=$2
for ERA in ${ERAS[@]}; do
echo $ERA
done

echo $CHANNEL
echo $GC_JOB_ID

if [ "$GC_JOB_ID" -eq 0 ]; then
MASS=240
MASS_H2=60
fi
        

if [ "$GC_JOB_ID" -eq 1 ]; then
MASS=240
MASS_H2=70
fi
        

if [ "$GC_JOB_ID" -eq 2 ]; then
MASS=240
MASS_H2=75
fi
        

if [ "$GC_JOB_ID" -eq 3 ]; then
MASS=240
MASS_H2=80
fi
        

if [ "$GC_JOB_ID" -eq 4 ]; then
MASS=240
MASS_H2=85
fi
        

if [ "$GC_JOB_ID" -eq 5 ]; then
MASS=240
MASS_H2=90
fi
        

if [ "$GC_JOB_ID" -eq 6 ]; then
MASS=240
MASS_H2=95
fi
        

if [ "$GC_JOB_ID" -eq 7 ]; then
MASS=240
MASS_H2=100
fi
        

if [ "$GC_JOB_ID" -eq 8 ]; then
MASS=240
MASS_H2=110
fi
        

if [ "$GC_JOB_ID" -eq 9 ]; then
MASS=280
MASS_H2=60
fi
        

if [ "$GC_JOB_ID" -eq 10 ]; then
MASS=280
MASS_H2=70
fi
        

if [ "$GC_JOB_ID" -eq 11 ]; then
MASS=280
MASS_H2=75
fi
        

if [ "$GC_JOB_ID" -eq 12 ]; then
MASS=280
MASS_H2=80
fi
        

if [ "$GC_JOB_ID" -eq 13 ]; then
MASS=280
MASS_H2=85
fi
        

if [ "$GC_JOB_ID" -eq 14 ]; then
MASS=280
MASS_H2=90
fi
        

if [ "$GC_JOB_ID" -eq 15 ]; then
MASS=280
MASS_H2=95
fi
        

if [ "$GC_JOB_ID" -eq 16 ]; then
MASS=280
MASS_H2=100
fi
        

if [ "$GC_JOB_ID" -eq 17 ]; then
MASS=280
MASS_H2=110
fi
        

if [ "$GC_JOB_ID" -eq 18 ]; then
MASS=280
MASS_H2=120
fi
        

if [ "$GC_JOB_ID" -eq 19 ]; then
MASS=280
MASS_H2=130
fi
        

if [ "$GC_JOB_ID" -eq 20 ]; then
MASS=280
MASS_H2=150
fi
        

if [ "$GC_JOB_ID" -eq 21 ]; then
MASS=320
MASS_H2=60
fi
        

if [ "$GC_JOB_ID" -eq 22 ]; then
MASS=320
MASS_H2=70
fi
        

if [ "$GC_JOB_ID" -eq 23 ]; then
MASS=320
MASS_H2=75
fi
        

if [ "$GC_JOB_ID" -eq 24 ]; then
MASS=320
MASS_H2=80
fi
        

if [ "$GC_JOB_ID" -eq 25 ]; then
MASS=320
MASS_H2=85
fi
        

if [ "$GC_JOB_ID" -eq 26 ]; then
MASS=320
MASS_H2=90
fi
        

if [ "$GC_JOB_ID" -eq 27 ]; then
MASS=320
MASS_H2=95
fi
        

if [ "$GC_JOB_ID" -eq 28 ]; then
MASS=320
MASS_H2=100
fi
        

if [ "$GC_JOB_ID" -eq 29 ]; then
MASS=320
MASS_H2=110
fi
        

if [ "$GC_JOB_ID" -eq 30 ]; then
MASS=320
MASS_H2=120
fi
        

if [ "$GC_JOB_ID" -eq 31 ]; then
MASS=320
MASS_H2=130
fi
        

if [ "$GC_JOB_ID" -eq 32 ]; then
MASS=320
MASS_H2=150
fi
        

if [ "$GC_JOB_ID" -eq 33 ]; then
MASS=320
MASS_H2=170
fi
        

if [ "$GC_JOB_ID" -eq 34 ]; then
MASS=320
MASS_H2=190
fi
        

if [ "$GC_JOB_ID" -eq 35 ]; then
MASS=360
MASS_H2=60
fi
        

if [ "$GC_JOB_ID" -eq 36 ]; then
MASS=360
MASS_H2=70
fi
        

if [ "$GC_JOB_ID" -eq 37 ]; then
MASS=360
MASS_H2=75
fi
        

if [ "$GC_JOB_ID" -eq 38 ]; then
MASS=360
MASS_H2=80
fi
        

if [ "$GC_JOB_ID" -eq 39 ]; then
MASS=360
MASS_H2=85
fi
        

if [ "$GC_JOB_ID" -eq 40 ]; then
MASS=360
MASS_H2=90
fi
        

if [ "$GC_JOB_ID" -eq 41 ]; then
MASS=360
MASS_H2=95
fi
        

if [ "$GC_JOB_ID" -eq 42 ]; then
MASS=360
MASS_H2=100
fi
        

if [ "$GC_JOB_ID" -eq 43 ]; then
MASS=360
MASS_H2=110
fi
        

if [ "$GC_JOB_ID" -eq 44 ]; then
MASS=360
MASS_H2=120
fi
        

if [ "$GC_JOB_ID" -eq 45 ]; then
MASS=360
MASS_H2=130
fi
        

if [ "$GC_JOB_ID" -eq 46 ]; then
MASS=360
MASS_H2=150
fi
        

if [ "$GC_JOB_ID" -eq 47 ]; then
MASS=360
MASS_H2=170
fi
        

if [ "$GC_JOB_ID" -eq 48 ]; then
MASS=360
MASS_H2=190
fi
        

if [ "$GC_JOB_ID" -eq 49 ]; then
MASS=400
MASS_H2=60
fi
        

if [ "$GC_JOB_ID" -eq 50 ]; then
MASS=400
MASS_H2=70
fi
        

if [ "$GC_JOB_ID" -eq 51 ]; then
MASS=400
MASS_H2=75
fi
        

if [ "$GC_JOB_ID" -eq 52 ]; then
MASS=400
MASS_H2=80
fi
        

if [ "$GC_JOB_ID" -eq 53 ]; then
MASS=400
MASS_H2=85
fi
        

if [ "$GC_JOB_ID" -eq 54 ]; then
MASS=400
MASS_H2=90
fi
        

if [ "$GC_JOB_ID" -eq 55 ]; then
MASS=400
MASS_H2=95
fi
        

if [ "$GC_JOB_ID" -eq 56 ]; then
MASS=400
MASS_H2=100
fi
        

if [ "$GC_JOB_ID" -eq 57 ]; then
MASS=400
MASS_H2=110
fi
        

if [ "$GC_JOB_ID" -eq 58 ]; then
MASS=400
MASS_H2=120
fi
        

if [ "$GC_JOB_ID" -eq 59 ]; then
MASS=400
MASS_H2=130
fi
        

if [ "$GC_JOB_ID" -eq 60 ]; then
MASS=400
MASS_H2=150
fi
        

if [ "$GC_JOB_ID" -eq 61 ]; then
MASS=400
MASS_H2=170
fi
        

if [ "$GC_JOB_ID" -eq 62 ]; then
MASS=400
MASS_H2=190
fi
        

if [ "$GC_JOB_ID" -eq 63 ]; then
MASS=400
MASS_H2=250
fi
        

if [ "$GC_JOB_ID" -eq 64 ]; then
MASS=450
MASS_H2=60
fi
        

if [ "$GC_JOB_ID" -eq 65 ]; then
MASS=450
MASS_H2=70
fi
        

if [ "$GC_JOB_ID" -eq 66 ]; then
MASS=450
MASS_H2=75
fi
        

if [ "$GC_JOB_ID" -eq 67 ]; then
MASS=450
MASS_H2=80
fi
        

if [ "$GC_JOB_ID" -eq 68 ]; then
MASS=450
MASS_H2=85
fi
        

if [ "$GC_JOB_ID" -eq 69 ]; then
MASS=450
MASS_H2=90
fi
        

if [ "$GC_JOB_ID" -eq 70 ]; then
MASS=450
MASS_H2=95
fi
        

if [ "$GC_JOB_ID" -eq 71 ]; then
MASS=450
MASS_H2=100
fi
        

if [ "$GC_JOB_ID" -eq 72 ]; then
MASS=450
MASS_H2=110
fi
        

if [ "$GC_JOB_ID" -eq 73 ]; then
MASS=450
MASS_H2=120
fi
        

if [ "$GC_JOB_ID" -eq 74 ]; then
MASS=450
MASS_H2=130
fi
        

if [ "$GC_JOB_ID" -eq 75 ]; then
MASS=450
MASS_H2=150
fi
        

if [ "$GC_JOB_ID" -eq 76 ]; then
MASS=450
MASS_H2=170
fi
        

if [ "$GC_JOB_ID" -eq 77 ]; then
MASS=450
MASS_H2=190
fi
        

if [ "$GC_JOB_ID" -eq 78 ]; then
MASS=450
MASS_H2=250
fi
        

if [ "$GC_JOB_ID" -eq 79 ]; then
MASS=450
MASS_H2=300
fi
        

if [ "$GC_JOB_ID" -eq 80 ]; then
MASS=500
MASS_H2=60
fi
        

if [ "$GC_JOB_ID" -eq 81 ]; then
MASS=500
MASS_H2=70
fi
        

if [ "$GC_JOB_ID" -eq 82 ]; then
MASS=500
MASS_H2=75
fi
        

if [ "$GC_JOB_ID" -eq 83 ]; then
MASS=500
MASS_H2=80
fi
        

if [ "$GC_JOB_ID" -eq 84 ]; then
MASS=500
MASS_H2=85
fi
        

if [ "$GC_JOB_ID" -eq 85 ]; then
MASS=500
MASS_H2=90
fi
        

if [ "$GC_JOB_ID" -eq 86 ]; then
MASS=500
MASS_H2=95
fi
        

if [ "$GC_JOB_ID" -eq 87 ]; then
MASS=500
MASS_H2=100
fi
        

if [ "$GC_JOB_ID" -eq 88 ]; then
MASS=500
MASS_H2=110
fi
        

if [ "$GC_JOB_ID" -eq 89 ]; then
MASS=500
MASS_H2=120
fi
        

if [ "$GC_JOB_ID" -eq 90 ]; then
MASS=500
MASS_H2=130
fi
        

if [ "$GC_JOB_ID" -eq 91 ]; then
MASS=500
MASS_H2=150
fi
        

if [ "$GC_JOB_ID" -eq 92 ]; then
MASS=500
MASS_H2=170
fi
        

if [ "$GC_JOB_ID" -eq 93 ]; then
MASS=500
MASS_H2=190
fi
        

if [ "$GC_JOB_ID" -eq 94 ]; then
MASS=500
MASS_H2=250
fi
        

if [ "$GC_JOB_ID" -eq 95 ]; then
MASS=500
MASS_H2=300
fi
        

if [ "$GC_JOB_ID" -eq 96 ]; then
MASS=500
MASS_H2=350
fi
        

if [ "$GC_JOB_ID" -eq 97 ]; then
MASS=550
MASS_H2=60
fi
        

if [ "$GC_JOB_ID" -eq 98 ]; then
MASS=550
MASS_H2=70
fi
        

if [ "$GC_JOB_ID" -eq 99 ]; then
MASS=550
MASS_H2=75
fi
        

if [ "$GC_JOB_ID" -eq 100 ]; then
MASS=550
MASS_H2=80
fi
        

if [ "$GC_JOB_ID" -eq 101 ]; then
MASS=550
MASS_H2=85
fi
        

if [ "$GC_JOB_ID" -eq 102 ]; then
MASS=550
MASS_H2=90
fi
        

if [ "$GC_JOB_ID" -eq 103 ]; then
MASS=550
MASS_H2=95
fi
        

if [ "$GC_JOB_ID" -eq 104 ]; then
MASS=550
MASS_H2=100
fi
        

if [ "$GC_JOB_ID" -eq 105 ]; then
MASS=550
MASS_H2=110
fi
        

if [ "$GC_JOB_ID" -eq 106 ]; then
MASS=550
MASS_H2=120
fi
        

if [ "$GC_JOB_ID" -eq 107 ]; then
MASS=550
MASS_H2=130
fi
        

if [ "$GC_JOB_ID" -eq 108 ]; then
MASS=550
MASS_H2=150
fi
        

if [ "$GC_JOB_ID" -eq 109 ]; then
MASS=550
MASS_H2=170
fi
        

if [ "$GC_JOB_ID" -eq 110 ]; then
MASS=550
MASS_H2=190
fi
        

if [ "$GC_JOB_ID" -eq 111 ]; then
MASS=550
MASS_H2=250
fi
        

if [ "$GC_JOB_ID" -eq 112 ]; then
MASS=550
MASS_H2=300
fi
        

if [ "$GC_JOB_ID" -eq 113 ]; then
MASS=550
MASS_H2=350
fi
        

if [ "$GC_JOB_ID" -eq 114 ]; then
MASS=550
MASS_H2=400
fi
        

if [ "$GC_JOB_ID" -eq 115 ]; then
MASS=600
MASS_H2=60
fi
        

if [ "$GC_JOB_ID" -eq 116 ]; then
MASS=600
MASS_H2=70
fi
        

if [ "$GC_JOB_ID" -eq 117 ]; then
MASS=600
MASS_H2=75
fi
        

if [ "$GC_JOB_ID" -eq 118 ]; then
MASS=600
MASS_H2=80
fi
        

if [ "$GC_JOB_ID" -eq 119 ]; then
MASS=600
MASS_H2=85
fi
        

if [ "$GC_JOB_ID" -eq 120 ]; then
MASS=600
MASS_H2=90
fi
        

if [ "$GC_JOB_ID" -eq 121 ]; then
MASS=600
MASS_H2=95
fi
        

if [ "$GC_JOB_ID" -eq 122 ]; then
MASS=600
MASS_H2=100
fi
        

if [ "$GC_JOB_ID" -eq 123 ]; then
MASS=600
MASS_H2=110
fi
        

if [ "$GC_JOB_ID" -eq 124 ]; then
MASS=600
MASS_H2=120
fi
        

if [ "$GC_JOB_ID" -eq 125 ]; then
MASS=600
MASS_H2=130
fi
        

if [ "$GC_JOB_ID" -eq 126 ]; then
MASS=600
MASS_H2=150
fi
        

if [ "$GC_JOB_ID" -eq 127 ]; then
MASS=600
MASS_H2=170
fi
        

if [ "$GC_JOB_ID" -eq 128 ]; then
MASS=600
MASS_H2=190
fi
        

if [ "$GC_JOB_ID" -eq 129 ]; then
MASS=600
MASS_H2=250
fi
        

if [ "$GC_JOB_ID" -eq 130 ]; then
MASS=600
MASS_H2=300
fi
        

if [ "$GC_JOB_ID" -eq 131 ]; then
MASS=600
MASS_H2=350
fi
        

if [ "$GC_JOB_ID" -eq 132 ]; then
MASS=600
MASS_H2=400
fi
        

if [ "$GC_JOB_ID" -eq 133 ]; then
MASS=600
MASS_H2=450
fi
        

if [ "$GC_JOB_ID" -eq 134 ]; then
MASS=700
MASS_H2=60
fi
        

if [ "$GC_JOB_ID" -eq 135 ]; then
MASS=700
MASS_H2=70
fi
        

if [ "$GC_JOB_ID" -eq 136 ]; then
MASS=700
MASS_H2=75
fi
        

if [ "$GC_JOB_ID" -eq 137 ]; then
MASS=700
MASS_H2=80
fi
        

if [ "$GC_JOB_ID" -eq 138 ]; then
MASS=700
MASS_H2=85
fi
        

if [ "$GC_JOB_ID" -eq 139 ]; then
MASS=700
MASS_H2=90
fi
        

if [ "$GC_JOB_ID" -eq 140 ]; then
MASS=700
MASS_H2=95
fi
        

if [ "$GC_JOB_ID" -eq 141 ]; then
MASS=700
MASS_H2=100
fi
        

if [ "$GC_JOB_ID" -eq 142 ]; then
MASS=700
MASS_H2=110
fi
        

if [ "$GC_JOB_ID" -eq 143 ]; then
MASS=700
MASS_H2=120
fi
        

if [ "$GC_JOB_ID" -eq 144 ]; then
MASS=700
MASS_H2=130
fi
        

if [ "$GC_JOB_ID" -eq 145 ]; then
MASS=700
MASS_H2=150
fi
        

if [ "$GC_JOB_ID" -eq 146 ]; then
MASS=700
MASS_H2=170
fi
        

if [ "$GC_JOB_ID" -eq 147 ]; then
MASS=700
MASS_H2=190
fi
        

if [ "$GC_JOB_ID" -eq 148 ]; then
MASS=700
MASS_H2=250
fi
        

if [ "$GC_JOB_ID" -eq 149 ]; then
MASS=700
MASS_H2=300
fi
        

if [ "$GC_JOB_ID" -eq 150 ]; then
MASS=700
MASS_H2=350
fi
        

if [ "$GC_JOB_ID" -eq 151 ]; then
MASS=700
MASS_H2=400
fi
        

if [ "$GC_JOB_ID" -eq 152 ]; then
MASS=700
MASS_H2=450
fi
        

if [ "$GC_JOB_ID" -eq 153 ]; then
MASS=700
MASS_H2=500
fi
        

if [ "$GC_JOB_ID" -eq 154 ]; then
MASS=700
MASS_H2=550
fi
        

if [ "$GC_JOB_ID" -eq 155 ]; then
MASS=800
MASS_H2=60
fi
        

if [ "$GC_JOB_ID" -eq 156 ]; then
MASS=800
MASS_H2=70
fi
        

if [ "$GC_JOB_ID" -eq 157 ]; then
MASS=800
MASS_H2=75
fi
        

if [ "$GC_JOB_ID" -eq 158 ]; then
MASS=800
MASS_H2=80
fi
        

if [ "$GC_JOB_ID" -eq 159 ]; then
MASS=800
MASS_H2=85
fi
        

if [ "$GC_JOB_ID" -eq 160 ]; then
MASS=800
MASS_H2=90
fi
        

if [ "$GC_JOB_ID" -eq 161 ]; then
MASS=800
MASS_H2=95
fi
        

if [ "$GC_JOB_ID" -eq 162 ]; then
MASS=800
MASS_H2=100
fi
        

if [ "$GC_JOB_ID" -eq 163 ]; then
MASS=800
MASS_H2=110
fi
        

if [ "$GC_JOB_ID" -eq 164 ]; then
MASS=800
MASS_H2=120
fi
        

if [ "$GC_JOB_ID" -eq 165 ]; then
MASS=800
MASS_H2=130
fi
        

if [ "$GC_JOB_ID" -eq 166 ]; then
MASS=800
MASS_H2=150
fi
        

if [ "$GC_JOB_ID" -eq 167 ]; then
MASS=800
MASS_H2=170
fi
        

if [ "$GC_JOB_ID" -eq 168 ]; then
MASS=800
MASS_H2=190
fi
        

if [ "$GC_JOB_ID" -eq 169 ]; then
MASS=800
MASS_H2=250
fi
        

if [ "$GC_JOB_ID" -eq 170 ]; then
MASS=800
MASS_H2=300
fi
        

if [ "$GC_JOB_ID" -eq 171 ]; then
MASS=800
MASS_H2=350
fi
        

if [ "$GC_JOB_ID" -eq 172 ]; then
MASS=800
MASS_H2=400
fi
        

if [ "$GC_JOB_ID" -eq 173 ]; then
MASS=800
MASS_H2=450
fi
        

if [ "$GC_JOB_ID" -eq 174 ]; then
MASS=800
MASS_H2=500
fi
        

if [ "$GC_JOB_ID" -eq 175 ]; then
MASS=800
MASS_H2=550
fi
        

if [ "$GC_JOB_ID" -eq 176 ]; then
MASS=800
MASS_H2=600
fi
        

if [ "$GC_JOB_ID" -eq 177 ]; then
MASS=800
MASS_H2=650
fi
        

if [ "$GC_JOB_ID" -eq 178 ]; then
MASS=900
MASS_H2=60
fi
        

if [ "$GC_JOB_ID" -eq 179 ]; then
MASS=900
MASS_H2=70
fi
        

if [ "$GC_JOB_ID" -eq 180 ]; then
MASS=900
MASS_H2=75
fi
        

if [ "$GC_JOB_ID" -eq 181 ]; then
MASS=900
MASS_H2=80
fi
        

if [ "$GC_JOB_ID" -eq 182 ]; then
MASS=900
MASS_H2=85
fi
        

if [ "$GC_JOB_ID" -eq 183 ]; then
MASS=900
MASS_H2=90
fi
        

if [ "$GC_JOB_ID" -eq 184 ]; then
MASS=900
MASS_H2=95
fi
        

if [ "$GC_JOB_ID" -eq 185 ]; then
MASS=900
MASS_H2=100
fi
        

if [ "$GC_JOB_ID" -eq 186 ]; then
MASS=900
MASS_H2=110
fi
        

if [ "$GC_JOB_ID" -eq 187 ]; then
MASS=900
MASS_H2=120
fi
        

if [ "$GC_JOB_ID" -eq 188 ]; then
MASS=900
MASS_H2=130
fi
        

if [ "$GC_JOB_ID" -eq 189 ]; then
MASS=900
MASS_H2=150
fi
        

if [ "$GC_JOB_ID" -eq 190 ]; then
MASS=900
MASS_H2=170
fi
        

if [ "$GC_JOB_ID" -eq 191 ]; then
MASS=900
MASS_H2=190
fi
        

if [ "$GC_JOB_ID" -eq 192 ]; then
MASS=900
MASS_H2=250
fi
        

if [ "$GC_JOB_ID" -eq 193 ]; then
MASS=900
MASS_H2=300
fi
        

if [ "$GC_JOB_ID" -eq 194 ]; then
MASS=900
MASS_H2=350
fi
        

if [ "$GC_JOB_ID" -eq 195 ]; then
MASS=900
MASS_H2=400
fi
        

if [ "$GC_JOB_ID" -eq 196 ]; then
MASS=900
MASS_H2=450
fi
        

if [ "$GC_JOB_ID" -eq 197 ]; then
MASS=900
MASS_H2=500
fi
        

if [ "$GC_JOB_ID" -eq 198 ]; then
MASS=900
MASS_H2=550
fi
        

if [ "$GC_JOB_ID" -eq 199 ]; then
MASS=900
MASS_H2=600
fi
        

if [ "$GC_JOB_ID" -eq 200 ]; then
MASS=900
MASS_H2=650
fi
        

if [ "$GC_JOB_ID" -eq 201 ]; then
MASS=900
MASS_H2=700
fi
        

if [ "$GC_JOB_ID" -eq 202 ]; then
MASS=900
MASS_H2=750
fi
        

if [ "$GC_JOB_ID" -eq 203 ]; then
MASS=1000
MASS_H2=60
fi
        

if [ "$GC_JOB_ID" -eq 204 ]; then
MASS=1000
MASS_H2=70
fi
        

if [ "$GC_JOB_ID" -eq 205 ]; then
MASS=1000
MASS_H2=75
fi
        

if [ "$GC_JOB_ID" -eq 206 ]; then
MASS=1000
MASS_H2=80
fi
        

if [ "$GC_JOB_ID" -eq 207 ]; then
MASS=1000
MASS_H2=85
fi
        

if [ "$GC_JOB_ID" -eq 208 ]; then
MASS=1000
MASS_H2=90
fi
        

if [ "$GC_JOB_ID" -eq 209 ]; then
MASS=1000
MASS_H2=95
fi
        

if [ "$GC_JOB_ID" -eq 210 ]; then
MASS=1000
MASS_H2=100
fi
        

if [ "$GC_JOB_ID" -eq 211 ]; then
MASS=1000
MASS_H2=110
fi
        

if [ "$GC_JOB_ID" -eq 212 ]; then
MASS=1000
MASS_H2=120
fi
        

if [ "$GC_JOB_ID" -eq 213 ]; then
MASS=1000
MASS_H2=130
fi
        

if [ "$GC_JOB_ID" -eq 214 ]; then
MASS=1000
MASS_H2=150
fi
        

if [ "$GC_JOB_ID" -eq 215 ]; then
MASS=1000
MASS_H2=170
fi
        

if [ "$GC_JOB_ID" -eq 216 ]; then
MASS=1000
MASS_H2=190
fi
        

if [ "$GC_JOB_ID" -eq 217 ]; then
MASS=1000
MASS_H2=250
fi
        

if [ "$GC_JOB_ID" -eq 218 ]; then
MASS=1000
MASS_H2=300
fi
        

if [ "$GC_JOB_ID" -eq 219 ]; then
MASS=1000
MASS_H2=350
fi
        

if [ "$GC_JOB_ID" -eq 220 ]; then
MASS=1000
MASS_H2=400
fi
        

if [ "$GC_JOB_ID" -eq 221 ]; then
MASS=1000
MASS_H2=450
fi
        

if [ "$GC_JOB_ID" -eq 222 ]; then
MASS=1000
MASS_H2=500
fi
        

if [ "$GC_JOB_ID" -eq 223 ]; then
MASS=1000
MASS_H2=550
fi
        

if [ "$GC_JOB_ID" -eq 224 ]; then
MASS=1000
MASS_H2=600
fi
        

if [ "$GC_JOB_ID" -eq 225 ]; then
MASS=1000
MASS_H2=650
fi
        

if [ "$GC_JOB_ID" -eq 226 ]; then
MASS=1000
MASS_H2=700
fi
        

if [ "$GC_JOB_ID" -eq 227 ]; then
MASS=1000
MASS_H2=750
fi
        

if [ "$GC_JOB_ID" -eq 228 ]; then
MASS=1000
MASS_H2=800
fi
        

if [ "$GC_JOB_ID" -eq 229 ]; then
MASS=1000
MASS_H2=850
fi
        

if [ "$GC_JOB_ID" -eq 230 ]; then
MASS=1200
MASS_H2=60
fi
        

if [ "$GC_JOB_ID" -eq 231 ]; then
MASS=1200
MASS_H2=70
fi
        

if [ "$GC_JOB_ID" -eq 232 ]; then
MASS=1200
MASS_H2=80
fi
        

if [ "$GC_JOB_ID" -eq 233 ]; then
MASS=1200
MASS_H2=90
fi
        

if [ "$GC_JOB_ID" -eq 234 ]; then
MASS=1200
MASS_H2=100
fi
        

if [ "$GC_JOB_ID" -eq 235 ]; then
MASS=1200
MASS_H2=120
fi
        

if [ "$GC_JOB_ID" -eq 236 ]; then
MASS=1200
MASS_H2=150
fi
        

if [ "$GC_JOB_ID" -eq 237 ]; then
MASS=1200
MASS_H2=170
fi
        

if [ "$GC_JOB_ID" -eq 238 ]; then
MASS=1200
MASS_H2=190
fi
        

if [ "$GC_JOB_ID" -eq 239 ]; then
MASS=1200
MASS_H2=250
fi
        

if [ "$GC_JOB_ID" -eq 240 ]; then
MASS=1200
MASS_H2=300
fi
        

if [ "$GC_JOB_ID" -eq 241 ]; then
MASS=1200
MASS_H2=350
fi
        

if [ "$GC_JOB_ID" -eq 242 ]; then
MASS=1200
MASS_H2=400
fi
        

if [ "$GC_JOB_ID" -eq 243 ]; then
MASS=1200
MASS_H2=450
fi
        

if [ "$GC_JOB_ID" -eq 244 ]; then
MASS=1200
MASS_H2=500
fi
        

if [ "$GC_JOB_ID" -eq 245 ]; then
MASS=1200
MASS_H2=550
fi
        

if [ "$GC_JOB_ID" -eq 246 ]; then
MASS=1200
MASS_H2=600
fi
        

if [ "$GC_JOB_ID" -eq 247 ]; then
MASS=1200
MASS_H2=650
fi
        

if [ "$GC_JOB_ID" -eq 248 ]; then
MASS=1200
MASS_H2=700
fi
        

if [ "$GC_JOB_ID" -eq 249 ]; then
MASS=1200
MASS_H2=800
fi
        

if [ "$GC_JOB_ID" -eq 250 ]; then
MASS=1200
MASS_H2=900
fi
        

if [ "$GC_JOB_ID" -eq 251 ]; then
MASS=1200
MASS_H2=1000
fi
        

if [ "$GC_JOB_ID" -eq 252 ]; then
MASS=1400
MASS_H2=60
fi
        

if [ "$GC_JOB_ID" -eq 253 ]; then
MASS=1400
MASS_H2=70
fi
        

if [ "$GC_JOB_ID" -eq 254 ]; then
MASS=1400
MASS_H2=80
fi
        

if [ "$GC_JOB_ID" -eq 255 ]; then
MASS=1400
MASS_H2=90
fi
        

if [ "$GC_JOB_ID" -eq 256 ]; then
MASS=1400
MASS_H2=100
fi
        

if [ "$GC_JOB_ID" -eq 257 ]; then
MASS=1400
MASS_H2=120
fi
        

if [ "$GC_JOB_ID" -eq 258 ]; then
MASS=1400
MASS_H2=150
fi
        

if [ "$GC_JOB_ID" -eq 259 ]; then
MASS=1400
MASS_H2=170
fi
        

if [ "$GC_JOB_ID" -eq 260 ]; then
MASS=1400
MASS_H2=190
fi
        

if [ "$GC_JOB_ID" -eq 261 ]; then
MASS=1400
MASS_H2=250
fi
        

if [ "$GC_JOB_ID" -eq 262 ]; then
MASS=1400
MASS_H2=300
fi
        

if [ "$GC_JOB_ID" -eq 263 ]; then
MASS=1400
MASS_H2=350
fi
        

if [ "$GC_JOB_ID" -eq 264 ]; then
MASS=1400
MASS_H2=400
fi
        

if [ "$GC_JOB_ID" -eq 265 ]; then
MASS=1400
MASS_H2=450
fi
        

if [ "$GC_JOB_ID" -eq 266 ]; then
MASS=1400
MASS_H2=500
fi
        

if [ "$GC_JOB_ID" -eq 267 ]; then
MASS=1400
MASS_H2=550
fi
        

if [ "$GC_JOB_ID" -eq 268 ]; then
MASS=1400
MASS_H2=600
fi
        

if [ "$GC_JOB_ID" -eq 269 ]; then
MASS=1400
MASS_H2=650
fi
        

if [ "$GC_JOB_ID" -eq 270 ]; then
MASS=1400
MASS_H2=700
fi
        

if [ "$GC_JOB_ID" -eq 271 ]; then
MASS=1400
MASS_H2=800
fi
        

if [ "$GC_JOB_ID" -eq 272 ]; then
MASS=1400
MASS_H2=900
fi
        

if [ "$GC_JOB_ID" -eq 273 ]; then
MASS=1400
MASS_H2=1000
fi
        

if [ "$GC_JOB_ID" -eq 274 ]; then
MASS=1400
MASS_H2=1100
fi
        

if [ "$GC_JOB_ID" -eq 275 ]; then
MASS=1400
MASS_H2=1200
fi
        

if [ "$GC_JOB_ID" -eq 276 ]; then
MASS=1600
MASS_H2=60
fi
        

if [ "$GC_JOB_ID" -eq 277 ]; then
MASS=1600
MASS_H2=70
fi
        

if [ "$GC_JOB_ID" -eq 278 ]; then
MASS=1600
MASS_H2=80
fi
        

if [ "$GC_JOB_ID" -eq 279 ]; then
MASS=1600
MASS_H2=90
fi
        

if [ "$GC_JOB_ID" -eq 280 ]; then
MASS=1600
MASS_H2=100
fi
        

if [ "$GC_JOB_ID" -eq 281 ]; then
MASS=1600
MASS_H2=120
fi
        

if [ "$GC_JOB_ID" -eq 282 ]; then
MASS=1600
MASS_H2=150
fi
        

if [ "$GC_JOB_ID" -eq 283 ]; then
MASS=1600
MASS_H2=170
fi
        

if [ "$GC_JOB_ID" -eq 284 ]; then
MASS=1600
MASS_H2=190
fi
        

if [ "$GC_JOB_ID" -eq 285 ]; then
MASS=1600
MASS_H2=250
fi
        

if [ "$GC_JOB_ID" -eq 286 ]; then
MASS=1600
MASS_H2=300
fi
        

if [ "$GC_JOB_ID" -eq 287 ]; then
MASS=1600
MASS_H2=350
fi
        

if [ "$GC_JOB_ID" -eq 288 ]; then
MASS=1600
MASS_H2=400
fi
        

if [ "$GC_JOB_ID" -eq 289 ]; then
MASS=1600
MASS_H2=450
fi
        

if [ "$GC_JOB_ID" -eq 290 ]; then
MASS=1600
MASS_H2=500
fi
        

if [ "$GC_JOB_ID" -eq 291 ]; then
MASS=1600
MASS_H2=550
fi
        

if [ "$GC_JOB_ID" -eq 292 ]; then
MASS=1600
MASS_H2=600
fi
        

if [ "$GC_JOB_ID" -eq 293 ]; then
MASS=1600
MASS_H2=650
fi
        

if [ "$GC_JOB_ID" -eq 294 ]; then
MASS=1600
MASS_H2=700
fi
        

if [ "$GC_JOB_ID" -eq 295 ]; then
MASS=1600
MASS_H2=800
fi
        

if [ "$GC_JOB_ID" -eq 296 ]; then
MASS=1600
MASS_H2=900
fi
        

if [ "$GC_JOB_ID" -eq 297 ]; then
MASS=1600
MASS_H2=1000
fi
        

if [ "$GC_JOB_ID" -eq 298 ]; then
MASS=1600
MASS_H2=1100
fi
        

if [ "$GC_JOB_ID" -eq 299 ]; then
MASS=1600
MASS_H2=1200
fi
        

if [ "$GC_JOB_ID" -eq 300 ]; then
MASS=1600
MASS_H2=1300
fi
        

if [ "$GC_JOB_ID" -eq 301 ]; then
MASS=1600
MASS_H2=1400
fi
        

if [ "$GC_JOB_ID" -eq 302 ]; then
MASS=1800
MASS_H2=60
fi
        

if [ "$GC_JOB_ID" -eq 303 ]; then
MASS=1800
MASS_H2=70
fi
        

if [ "$GC_JOB_ID" -eq 304 ]; then
MASS=1800
MASS_H2=80
fi
        

if [ "$GC_JOB_ID" -eq 305 ]; then
MASS=1800
MASS_H2=90
fi
        

if [ "$GC_JOB_ID" -eq 306 ]; then
MASS=1800
MASS_H2=100
fi
        

if [ "$GC_JOB_ID" -eq 307 ]; then
MASS=1800
MASS_H2=120
fi
        

if [ "$GC_JOB_ID" -eq 308 ]; then
MASS=1800
MASS_H2=150
fi
        

if [ "$GC_JOB_ID" -eq 309 ]; then
MASS=1800
MASS_H2=170
fi
        

if [ "$GC_JOB_ID" -eq 310 ]; then
MASS=1800
MASS_H2=190
fi
        

if [ "$GC_JOB_ID" -eq 311 ]; then
MASS=1800
MASS_H2=250
fi
        

if [ "$GC_JOB_ID" -eq 312 ]; then
MASS=1800
MASS_H2=300
fi
        

if [ "$GC_JOB_ID" -eq 313 ]; then
MASS=1800
MASS_H2=350
fi
        

if [ "$GC_JOB_ID" -eq 314 ]; then
MASS=1800
MASS_H2=400
fi
        

if [ "$GC_JOB_ID" -eq 315 ]; then
MASS=1800
MASS_H2=450
fi
        

if [ "$GC_JOB_ID" -eq 316 ]; then
MASS=1800
MASS_H2=500
fi
        

if [ "$GC_JOB_ID" -eq 317 ]; then
MASS=1800
MASS_H2=550
fi
        

if [ "$GC_JOB_ID" -eq 318 ]; then
MASS=1800
MASS_H2=600
fi
        

if [ "$GC_JOB_ID" -eq 319 ]; then
MASS=1800
MASS_H2=650
fi
        

if [ "$GC_JOB_ID" -eq 320 ]; then
MASS=1800
MASS_H2=700
fi
        

if [ "$GC_JOB_ID" -eq 321 ]; then
MASS=1800
MASS_H2=800
fi
        

if [ "$GC_JOB_ID" -eq 322 ]; then
MASS=1800
MASS_H2=900
fi
        

if [ "$GC_JOB_ID" -eq 323 ]; then
MASS=1800
MASS_H2=1000
fi
        

if [ "$GC_JOB_ID" -eq 324 ]; then
MASS=1800
MASS_H2=1100
fi
        

if [ "$GC_JOB_ID" -eq 325 ]; then
MASS=1800
MASS_H2=1200
fi
        

if [ "$GC_JOB_ID" -eq 326 ]; then
MASS=1800
MASS_H2=1300
fi
        

if [ "$GC_JOB_ID" -eq 327 ]; then
MASS=1800
MASS_H2=1400
fi
        

if [ "$GC_JOB_ID" -eq 328 ]; then
MASS=1800
MASS_H2=1600
fi
        

if [ "$GC_JOB_ID" -eq 329 ]; then
MASS=2000
MASS_H2=60
fi
        

if [ "$GC_JOB_ID" -eq 330 ]; then
MASS=2000
MASS_H2=70
fi
        

if [ "$GC_JOB_ID" -eq 331 ]; then
MASS=2000
MASS_H2=80
fi
        

if [ "$GC_JOB_ID" -eq 332 ]; then
MASS=2000
MASS_H2=90
fi
        

if [ "$GC_JOB_ID" -eq 333 ]; then
MASS=2000
MASS_H2=100
fi
        

if [ "$GC_JOB_ID" -eq 334 ]; then
MASS=2000
MASS_H2=120
fi
        

if [ "$GC_JOB_ID" -eq 335 ]; then
MASS=2000
MASS_H2=150
fi
        

if [ "$GC_JOB_ID" -eq 336 ]; then
MASS=2000
MASS_H2=170
fi
        

if [ "$GC_JOB_ID" -eq 337 ]; then
MASS=2000
MASS_H2=190
fi
        

if [ "$GC_JOB_ID" -eq 338 ]; then
MASS=2000
MASS_H2=250
fi
        

if [ "$GC_JOB_ID" -eq 339 ]; then
MASS=2000
MASS_H2=300
fi
        

if [ "$GC_JOB_ID" -eq 340 ]; then
MASS=2000
MASS_H2=350
fi
        

if [ "$GC_JOB_ID" -eq 341 ]; then
MASS=2000
MASS_H2=400
fi
        

if [ "$GC_JOB_ID" -eq 342 ]; then
MASS=2000
MASS_H2=450
fi
        

if [ "$GC_JOB_ID" -eq 343 ]; then
MASS=2000
MASS_H2=500
fi
        

if [ "$GC_JOB_ID" -eq 344 ]; then
MASS=2000
MASS_H2=550
fi
        

if [ "$GC_JOB_ID" -eq 345 ]; then
MASS=2000
MASS_H2=600
fi
        

if [ "$GC_JOB_ID" -eq 346 ]; then
MASS=2000
MASS_H2=650
fi
        

if [ "$GC_JOB_ID" -eq 347 ]; then
MASS=2000
MASS_H2=700
fi
        

if [ "$GC_JOB_ID" -eq 348 ]; then
MASS=2000
MASS_H2=800
fi
        

if [ "$GC_JOB_ID" -eq 349 ]; then
MASS=2000
MASS_H2=900
fi
        

if [ "$GC_JOB_ID" -eq 350 ]; then
MASS=2000
MASS_H2=1000
fi
        

if [ "$GC_JOB_ID" -eq 351 ]; then
MASS=2000
MASS_H2=1100
fi
        

if [ "$GC_JOB_ID" -eq 352 ]; then
MASS=2000
MASS_H2=1200
fi
        

if [ "$GC_JOB_ID" -eq 353 ]; then
MASS=2000
MASS_H2=1300
fi
        

if [ "$GC_JOB_ID" -eq 354 ]; then
MASS=2000
MASS_H2=1400
fi
        

if [ "$GC_JOB_ID" -eq 355 ]; then
MASS=2000
MASS_H2=1600
fi
        

if [ "$GC_JOB_ID" -eq 356 ]; then
MASS=2000
MASS_H2=1800
fi
        

if [ "$GC_JOB_ID" -eq 357 ]; then
MASS=2500
MASS_H2=60
fi
        

if [ "$GC_JOB_ID" -eq 358 ]; then
MASS=2500
MASS_H2=70
fi
        

if [ "$GC_JOB_ID" -eq 359 ]; then
MASS=2500
MASS_H2=80
fi
        

if [ "$GC_JOB_ID" -eq 360 ]; then
MASS=2500
MASS_H2=90
fi
        

if [ "$GC_JOB_ID" -eq 361 ]; then
MASS=2500
MASS_H2=100
fi
        

if [ "$GC_JOB_ID" -eq 362 ]; then
MASS=2500
MASS_H2=120
fi
        

if [ "$GC_JOB_ID" -eq 363 ]; then
MASS=2500
MASS_H2=150
fi
        

if [ "$GC_JOB_ID" -eq 364 ]; then
MASS=2500
MASS_H2=170
fi
        

if [ "$GC_JOB_ID" -eq 365 ]; then
MASS=2500
MASS_H2=190
fi
        

if [ "$GC_JOB_ID" -eq 366 ]; then
MASS=2500
MASS_H2=250
fi
        

if [ "$GC_JOB_ID" -eq 367 ]; then
MASS=2500
MASS_H2=300
fi
        

if [ "$GC_JOB_ID" -eq 368 ]; then
MASS=2500
MASS_H2=350
fi
        

if [ "$GC_JOB_ID" -eq 369 ]; then
MASS=2500
MASS_H2=400
fi
        

if [ "$GC_JOB_ID" -eq 370 ]; then
MASS=2500
MASS_H2=450
fi
        

if [ "$GC_JOB_ID" -eq 371 ]; then
MASS=2500
MASS_H2=500
fi
        

if [ "$GC_JOB_ID" -eq 372 ]; then
MASS=2500
MASS_H2=550
fi
        

if [ "$GC_JOB_ID" -eq 373 ]; then
MASS=2500
MASS_H2=600
fi
        

if [ "$GC_JOB_ID" -eq 374 ]; then
MASS=2500
MASS_H2=650
fi
        

if [ "$GC_JOB_ID" -eq 375 ]; then
MASS=2500
MASS_H2=700
fi
        

if [ "$GC_JOB_ID" -eq 376 ]; then
MASS=2500
MASS_H2=800
fi
        

if [ "$GC_JOB_ID" -eq 377 ]; then
MASS=2500
MASS_H2=900
fi
        

if [ "$GC_JOB_ID" -eq 378 ]; then
MASS=2500
MASS_H2=1000
fi
        

if [ "$GC_JOB_ID" -eq 379 ]; then
MASS=2500
MASS_H2=1100
fi
        

if [ "$GC_JOB_ID" -eq 380 ]; then
MASS=2500
MASS_H2=1200
fi
        

if [ "$GC_JOB_ID" -eq 381 ]; then
MASS=2500
MASS_H2=1300
fi
        

if [ "$GC_JOB_ID" -eq 382 ]; then
MASS=2500
MASS_H2=1400
fi
        

if [ "$GC_JOB_ID" -eq 383 ]; then
MASS=2500
MASS_H2=1600
fi
        

if [ "$GC_JOB_ID" -eq 384 ]; then
MASS=2500
MASS_H2=1800
fi
        

if [ "$GC_JOB_ID" -eq 385 ]; then
MASS=2500
MASS_H2=2000
fi
        

if [ "$GC_JOB_ID" -eq 386 ]; then
MASS=2500
MASS_H2=2200
fi
        

if [ "$GC_JOB_ID" -eq 387 ]; then
MASS=3000
MASS_H2=60
fi
        

if [ "$GC_JOB_ID" -eq 388 ]; then
MASS=3000
MASS_H2=70
fi
        

if [ "$GC_JOB_ID" -eq 389 ]; then
MASS=3000
MASS_H2=80
fi
        

if [ "$GC_JOB_ID" -eq 390 ]; then
MASS=3000
MASS_H2=90
fi
        

if [ "$GC_JOB_ID" -eq 391 ]; then
MASS=3000
MASS_H2=100
fi
        

if [ "$GC_JOB_ID" -eq 392 ]; then
MASS=3000
MASS_H2=120
fi
        

if [ "$GC_JOB_ID" -eq 393 ]; then
MASS=3000
MASS_H2=150
fi
        

if [ "$GC_JOB_ID" -eq 394 ]; then
MASS=3000
MASS_H2=170
fi
        

if [ "$GC_JOB_ID" -eq 395 ]; then
MASS=3000
MASS_H2=190
fi
        

if [ "$GC_JOB_ID" -eq 396 ]; then
MASS=3000
MASS_H2=250
fi
        

if [ "$GC_JOB_ID" -eq 397 ]; then
MASS=3000
MASS_H2=300
fi
        

if [ "$GC_JOB_ID" -eq 398 ]; then
MASS=3000
MASS_H2=350
fi
        

if [ "$GC_JOB_ID" -eq 399 ]; then
MASS=3000
MASS_H2=400
fi
        

if [ "$GC_JOB_ID" -eq 400 ]; then
MASS=3000
MASS_H2=450
fi
        

if [ "$GC_JOB_ID" -eq 401 ]; then
MASS=3000
MASS_H2=500
fi
        

if [ "$GC_JOB_ID" -eq 402 ]; then
MASS=3000
MASS_H2=550
fi
        

if [ "$GC_JOB_ID" -eq 403 ]; then
MASS=3000
MASS_H2=600
fi
        

if [ "$GC_JOB_ID" -eq 404 ]; then
MASS=3000
MASS_H2=650
fi
        

if [ "$GC_JOB_ID" -eq 405 ]; then
MASS=3000
MASS_H2=700
fi
        

if [ "$GC_JOB_ID" -eq 406 ]; then
MASS=3000
MASS_H2=800
fi
        

if [ "$GC_JOB_ID" -eq 407 ]; then
MASS=3000
MASS_H2=900
fi
        

if [ "$GC_JOB_ID" -eq 408 ]; then
MASS=3000
MASS_H2=1000
fi
        

if [ "$GC_JOB_ID" -eq 409 ]; then
MASS=3000
MASS_H2=1100
fi
        

if [ "$GC_JOB_ID" -eq 410 ]; then
MASS=3000
MASS_H2=1200
fi
        

if [ "$GC_JOB_ID" -eq 411 ]; then
MASS=3000
MASS_H2=1300
fi
        

if [ "$GC_JOB_ID" -eq 412 ]; then
MASS=3000
MASS_H2=1400
fi
        

if [ "$GC_JOB_ID" -eq 413 ]; then
MASS=3000
MASS_H2=1600
fi
        

if [ "$GC_JOB_ID" -eq 414 ]; then
MASS=3000
MASS_H2=1800
fi
        

if [ "$GC_JOB_ID" -eq 415 ]; then
MASS=3000
MASS_H2=2000
fi
        

if [ "$GC_JOB_ID" -eq 416 ]; then
MASS=3000
MASS_H2=2200
fi
        

if [ "$GC_JOB_ID" -eq 417 ]; then
MASS=3000
MASS_H2=2400
fi
        

if [ "$GC_JOB_ID" -eq 418 ]; then
MASS=3000
MASS_H2=2600
fi
        

if [ "$GC_JOB_ID" -eq 419 ]; then
MASS=3000
MASS_H2=2800
fi
        
# mkdir output_${ERA}_${CHANNEL}_nmssm_${MASS}_

# source utils/setup_cmssw.sh


for ERA in ${ERAS[@]}; do
    if [ "$CHANNEL" == "all" ]
        then
        MorphingMSSMvsSM --era=${ERA} --auto_rebin=1 --binomial_bbb=1 --analysis=nmssm --channel="mt et tt" --heavy_mass=${MASS}  --light_mass=${MASS_H2} --output_folder="output_"${ERA}"_"${CHANNEL}
        else
        MorphingMSSMvsSM --era=${ERA} --auto_rebin=1 --binomial_bbb=1 --analysis=nmssm --channel=${CHANNEL} --heavy_mass=${MASS} --light_mass=${MASS_H2} --output_folder="output_"${ERA}"_"${CHANNEL}
    fi
done

TARGET=output_combined_${CHANNEL}_nmssm_${MASS}_${MASS_H2}/combined/cmb
## remove old files
ls $TARGET && rm -r $TARGET
[ ! -d $TARGET ] && mkdir -p $TARGET 
[ ! -d $TARGET/common ] && mkdir $TARGET/common
for ERA in ${ERAS[@]}; do
    echo "Copying datasets for "$ERA
    DATACARDDIR=output_${ERA}_${CHANNEL}_nmssm_${MASS}_${MASS_H2}/${ERA}/cmb
    cp ${DATACARDDIR}/htt_*_${ERA}.txt $TARGET/.
    cp ${DATACARDDIR}/common/htt_input_${ERA}.root $TARGET/common/.
    ls $TARGET
done

echo "HERE1"
ls
echo "HERE2"
ls *
echo "HERE3"
ls $TARGET
echo "HERE4"
ls $TARGET/*
echo "HERE5"

combineTool.py -M T2W -o "ws.root"  --PO '"map=^.*/NMSSM_'${MASS}'_125_'${MASS_H2}'$:r_NMSSM_'${MASS}'_125_'${MASS_H2}'[0,0,5]"' -i output_combined_${CHANNEL}_nmssm_${MASS}_${MASS_H2}/combined/cmb/ -m ${MASS_H2} --parallel 1 -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel
echo "HERE6"
combineTool.py -m $MASS_H2 -M AsymptoticLimits --rAbsAcc 0 --rRelAcc 0.0005  --setParameters r_NMSSM_${MASS}_125_${MASS_H2}=0 --redefineSignalPOIs r_NMSSM_${MASS}_125_${MASS_H2} -d output_combined_${CHANNEL}_nmssm_${MASS}_${MASS_H2}/combined/cmb/ws.root --there -n ".NMSSM_"${MASS}"_125_"  --task-name NMSSM_${MASS}_125_${MASS_H2} --parallel 1 -t -1

combineTool.py -M CollectLimits output_combined_${CHANNEL}_nmssm_${MASS}_${MASS_H2}/combined/cmb/higgsCombine*.root --use-dirs -o nmssm_combined_${CHANNEL}_${MASS}_${MASS_H2}.json

#PostFitShapesFromWorkspace -d output_combined_${CHANNEL}_nmssm_${MASS}_${MASS_H2}/combined/${CHANNEL}/combined.txt.${CHANNEL} -w output_combined_${CHANNEL}_nmssm_${MASS}_${MASS_H2}/combined/${CHANNEL}/ws.root -o output_combined_${CHANNEL}_nmssm_${MASS}_${MASS_H2}/${ERA}/${CHANNEL}/prefitshape.root --freeze r_NMSSM_${MASS}_125_${MASS_H2}=0.1

