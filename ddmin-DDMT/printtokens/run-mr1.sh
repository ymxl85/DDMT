#!/bin/bash
#this is the script to MTDD all versions of printtokens

save=../../../0-2026/rawResults/DDMT/pt
mkdir $save

for i in {1..7}; do #versions
  save1=$save/v$i
  mkdir $save1

  for j in {1..3}; do #MRs
    mr=MR$j
    ver=../v$i
    tcdir=$ver/$mr"vmtg"
    echo $tcdir

    if [ "`ls -A $tcdir`" = "" ]
    then
      echo $tcdir" 0 tcs"
    else ###
      echo $tcdir"  MTDD"
      
      save2=$save1/$mr
      if [ -e $save2 ]
      then
	  rm -r $save2
      fi
      mkdir $save2
      echo $save2
      ############################################################run MTDD
     for file in $tcdir/*
     do
       fname=${file##*/}
       j=0
       
       python DDMT.py --trgName printtokens --trgPrefix pt --vID $i --ftc $file --MR $mr > $save2/$fname 2>&1

     done
     ################################################################
    fi ###
  done  #MRs
done  #versions
