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
        if not isinstance(match,tuple) and match=="":
            workl[index-1]=(workl[index-1][0]+workl[index+1][0], workl[index-1][1]+workl[index+1][1])
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
    ## drop in-between number matches rg 1.{22|33}55{11,22}
    ### first split match "234 adjen" -> "234"," adjen"
    # #print "Drop on between"
    # tmpmatches=[]
    # for index,match in enumerate(matches):
    #         matchstr=str1[match[0]:match[0]+match[2]]
    #         digitend=re.compile('^[0-9,.]+\s+')
    #         m=digitend.match(matchstr)
    #         if m:
    #             dm=re.compile('^[0-9,.]+').match(matchstr)
    #             dis=dm.end() - dm.start()
    #             m1=[match[0],match[1], dis]
    #             m2=[match[0]+dis,match[1]+dis, match[2]-dis]
    #             tmpmatches.append(m1)
    #             tmpmatches.append(m2)
    #             #print "Splitting"+matchstr+" to '"+matchtostr(m1)+"' and '" + matchtostr(m2)+"'"
    #         else:
    #             tmpmatches.append(match)
    # matches=tmpmatches
    # del tmpmatches
    # #print [matchtostr(match) for match in matches]
    #
    #
    # ### here is decided which match is removed
    # ###workwörk
    # #print "workwörk"
    # matchsToRemove=[]
    # for index,match in enumerate(matches):
    #     matchstr=str1[match[0]:match[0]+match[2]]
    #     if digits.match(matchstr):
    #         if index==0:
    #             prematch=[0,0,0]
    #         else:
    #             prematch=matches[index-1]
    #         if index==len(matches)-1:
    #             nxtmatch=[len(str1), len(str2)]
    #         else:
    #             nxtmatch=matches[index+1]
    #         prediff1=str1[prematch[0]+prematch[2]:match[0]]
    #         prediff2=str2[prematch[1]+prematch[2]:match[1]]
    #         nxtdiff1=str1[match[0]+match[2]:nxtmatch[0]]
    #         nxtdiff2=str2[match[1]+match[2]:nxtmatch[1]]
    #         #print matchstr
    #         gp= [prediff1,prediff2,nxtdiff1,nxtdiff2]
    #         #print "[prediff1,prediff2,nxtdiff1,nxtdiff2]"
    #         #print gp
    #         nbo=all([x=="" or bool(digitsstart.match(x)) for x in gp])
    #         #if digits.match(matchstr) and (len(matchstr)==1 or nbo) :
    #         if len(matchstr)==1 or ( digits.match(matchstr) and nbo) :
    #             #print "Remoing match "+matchstr+" :"+ str(match)
    #             matchsToRemove.append(match)
    #     elif len(matchstr)==1:
    #         matchsToRemove.append(match)
    #
    #
    # for match in matchsToRemove:
    #     matches.remove(match)
    # #print [matchtostr(match) for match in matches]
    #
    #
    #
    # ##reconnect matched with 0 distance
    # #print "reconnect"
    # tmpmatches=[]
    # index=0
    # while index < len(matches) : # -1 for index
    #     #print index
    #     match=matches[index]
    #     if index <  len(matches)-1:
    #         nxtmatch=matches[index+1]
    #         if match[0]+match[2]==nxtmatch[0] and match[1]+match[2]==nxtmatch[1]:
    #             tmpmatches.append([match[0],match[1],match[2]+nxtmatch[2]])
    #             #skip next match
    #             #print "Reconnecting"+matchtostr(match)+" and " + matchtostr(nxtmatch)
    #             index=index+1
    #         else:
    #             tmpmatches.append(match)
    #             #print "Appending"+matchtostr(match)
    #
    #     else:
    #         tmpmatches.append(match)
    #         #print "Appending"+matchtostr(match)
    #     index=index+1
    # matches=tmpmatches
    # del tmpmatches
    # del index
    # #print [matchtostr(match) for match in matches]
    #
    # ##### Generate output here
    # ##Start of the line
    # res=""
    # if matches[0][0]!= 0 or matches[0][1]!=0:
    #         nxtmatch=matches[0]
    #         diffstr1=str1[0:nxtmatch[0]]
    #         diffstr2=str2[0:nxtmatch[1]]
    #         res=res+sbra+diffstr1+mbar + diffstr2 + ebra
    #
    # for index,match in enumerate(matches):
    #     newmatch= str1[match[0]:match[0]+match[2]]
    #     res=res+newmatch
    #     if len(matches)-1>index:
    #         #print "foo"
    #         nxtmatch=matches[index+1]
    #         diffstr1=str1[match[0]+match[2]:nxtmatch[0]]
    #         diffstr2=str2[match[1]+match[2]:nxtmatch[1]]
    #         res=res+sbra+diffstr1+mbar + diffstr2 + ebra
    # ###end of the lines difference
    # ###
    # diffstr1=str1[matches[-1][0]+matches[-1][2]:len(str1)]
    # diffstr2=str2[matches[-1][1]+matches[-1][2]:len(str2)]
    # if diffstr1!="" or diffstr2!="":
    #         res=res+sbra+diffstr1+mbar + diffstr2 + ebra
    # #print str1
    # #print str2
    # #print res1
    # print res
