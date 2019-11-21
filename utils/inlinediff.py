#!/usr/bin/env python
 # -*- coding: utf-8 -*-
import sys
import re
import os
from difflib import SequenceMatcher as SM
#digits=re.compile('[0-9,.]+')
digitsstart=re.compile(r'.*[0-9,\.]+')
digits=re.compile(r'^[0-9,\.]+$')

def startWithDiget(s):
    if s=="":
        return False
    else:
        return bool(digits.match(s[0]))

HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'

sbra= FAIL+'{' +ENDC + OKBLUE
mbar=ENDC + FAIL + "|" + ENDC + OKGREEN
ebra=ENDC + FAIL + "}" + ENDC

if sys.argv[1]=="--help":
    print("Compares output file with different numbers. Takes two pipes as options. Do something like this ./utils/inlinediff.py <( cat emb-stxs_stage0-inclusive.txt) <(cat  mc-stxs_stage0-inclusive.txt)")
    print("Output:")
    print("r :    +1.000   -0.4{06|15}/+0.4{62|70} (68%)")
    exit()


##Mutliline input?
if (os.path.isfile(sys.argv[1]) and os.path.isfile(sys.argv[2])) or (sys.argv[1].startswith(("/proc/self/fd","/dev/fd")) and sys.argv[2].startswith(("/proc/self/fd","/dev/fd"))) :
    with open(sys.argv[1]) as f:
        lines1 = [line.rstrip('\n') for line in f]
    with open(sys.argv[2]) as f:
        lines2 = [line.rstrip('\n') for line in f]
    if len(lines1)!=len(lines2):
        print "Unequal number of lines!"
        exit(1)
else:
    lines1=[sys.argv[1]]
    lines2=[sys.argv[2]]




for iline in range(len(lines1)):
    str1, str2 = lines1[iline], lines2[iline]
    matches= SM(None, str1, str2).get_matching_blocks()[:-1]

    #no matches? end line
    if matches==[]:
        print sbra+str1+mbar+str2+ebra
        break
    def matchtostr(match):
        return str1[match[0]:match[0]+match[2]]
    # convert to working list
    workl=[]
    for index,match in enumerate(matches):
        if index==0:
            prevmatch=[0,0,0]
        else:
            prevmatch=matches[index-1]
        prevstr1=str1[prevmatch[0]+prevmatch[2]:match[0]]
        prevstr2=str2[prevmatch[1]+prevmatch[2]:match[1]]
        workl.append((prevstr1, prevstr2 ))
        workl.append(matchtostr(match))
    ## kill matches with lenght 1
    ## if a tuple ends with digests, move all numm
    for index,e in enumerate(workl):
        if not isinstance(e,tuple):
            preve=workl[index-1]
            if len(e)==1:
                workl[index-1]=(preve[0]+e, preve[1]+e)
                workl[index]=""
            if all([s!="" for s in preve]):
                if all([digits.match(s[-1]) for s in preve] ):
                    while startWithDiget(  workl[index]  ):
                        workl[index-1]=(workl[index-1][0]+workl[index][0], workl[index-1][1]+workl[index][0])
                        workl[index]=workl[index][1:]
    #merge diffs if match is empty
    for index,match in enumerate(workl):
        if not isinstance(match,tuple) and match=="" and index!=len(workl)-1:
            # print index
            # print [x for x in enumerate(workl)]
            # try:
            workl[index-1]=(workl[index-1][0]+workl[index+1][0], workl[index-1][1]+workl[index+1][1])
            # except IndexError:
            #     exit(1)
            # finally:
            #     print index
            #     print [x for x in enumerate(workl)]
            #     print workl[index]
            workl[index+1]=("","")


    # drop empties
    workl=filter(lambda x: x!="" and x!=("","") ,workl)
    outstr=""
    for e  in workl:
        if isinstance(e, tuple):
            outstr=outstr+sbra+e[0]+mbar + e[1] + ebra
        else:
            outstr=outstr+e
    print(outstr)
