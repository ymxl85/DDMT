# $Id: GCCDD.py,v 1.1 2001/11/05 19:53:33 zeller Exp $
# Using delta debugging on GCC input
import argparse
import sys
sys.path.append('/home/tzl/0DDMT/SIR/MT-and-DD/src')
import DD
import setN
import getN
import commands
import string
import os
import time

stc="stc.txt" #the file storing candiate test cases
ftc="ftc.txt"
mr_gen="";# MRi_GenFollow
mr_chk=""; #MRi_Checker
trg_exe=""; #*.exe
f_ftc=""; #the original source tc of the violating MTG

class MyDD(DD.DD): #MyDD is a subclass of DD.DD
    def __init__(self):
        DD.DD.__init__(self)
    
       
    def _test(self, deltas):
	setN.recordN()
        # Build input
        input = ""
        for (index, character) in deltas:
            input = input + character

        # Write source test input
        out = open(stc, 'w')
        out.write(input)
        out.close()
        
        print self.coerce(deltas)

        # testing
          # gen follow-up tc
        cmd="java "+mr_gen+" "+stc+" "+ftc+"; ./"+trg_exe+" < "+stc+" > o1; ./"+trg_exe+" < "+ftc+" > o2"
        #print cmd        
        os.system(cmd)
        #print "***************MT****************"
        (status, output) = commands.getstatusoutput(
            "(cat "+stc+") 2>&1")
        #print "[source tc] "+output
         
        (status, output) = commands.getstatusoutput(
            "(cat "+ftc+") 2>&1")
        #print "[follow-up tc] "+output
         
        (status, output) = commands.getstatusoutput(
            "(cat o1) 2>&1")
        #print "[source output] "+output
         
        (status, output) = commands.getstatusoutput(
            "(cat o2) 2>&1")
        #print "[follow-up output] "+output
          #MR check
        (status, output) = commands.getstatusoutput(
            "(java "+mr_chk+" o1 o2) 2>&1")
        
        if output == "Sat":
            return self.PASS
        else:
            return self.FAIL
        

    def coerce(self, deltas):
        # Pretty-print the configuration
        input = ""
        for (index, character) in deltas:
            input = input + character
        return input


if __name__ == '__main__':
    #######################################################################
    start_time=time.time()
    parser=argparse.ArgumentParser()
    parser.add_argument("--trgName",help="the name of the target program.i.e, printtokens")
    parser.add_argument("--trgPrefix",help="the name of the target program.i.e, printtokens")
    parser.add_argument("--vID",type=int,help="the id of the faulty version")
    parser.add_argument("--ftc",help="the failing test case")
    parser.add_argument("--MR",help="the used MR,i.e.,MR1")
    args=parser.parse_args();
    

    trg_exe="../v"+str(args.vID)+"/"+args.trgPrefix+str(args.vID)+".exe"
    f_ftc=args.ftc
    mr_gen=args.trgName+"."+args.MR+"_GenFollow"
    mr_chk=args.trgName+"."+args.MR+"_Checker"
    #######################################################################
    # Load deltas from `bug.c'
    deltas = []
    index = 1
    for character in open(f_ftc).read():
        deltas.append((index, character))
        index = index + 1

    mydd = MyDD()
    
    print "Simplifying failure-inducing input..."
    c = mydd.ddmin(deltas)              # Invoke DDMIN
    print "The 1-minimal failure-inducing input is", mydd.coerce(c)
    getN.printN()
    print "Removing any element will make the failure go away."
    end_time=time.time()
    run_time=end_time-start_time
    print "The run time is:", run_time
    # print
    
    # print "Isolating the failure-inducing difference..."
    # (c, c1, c2) = mydd.dd(deltas)	# Invoke DD
    # print "The 1-minimal failure-inducing difference is", c
    # print mydd.coerce(c1), "passes,", mydd.coerce(c2), "fails"




# Local Variables:
# mode: python
# End:
