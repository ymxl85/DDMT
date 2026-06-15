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
import time

candidate="ctc.txt" #the file storing candiate test cases
e_oracle=""
e_trg=""
f_tc=""
f_args=""
class MyDD(DD.DD): #MyDD is a subclass of DD.DD
    def __init__(self):
        DD.DD.__init__(self)
    
       
    def _test(self, deltas):
	setN.recordN()
        # Build input
        input = ""
        for (index, character) in deltas:
            input = input + character

        # Write candidate input
        out = open(candidate, 'w')
        out.write(input)
        out.close()
        
        print self.coerce(deltas)

	cmd=e_oracle+" < "+candidate+" > o1; "+e_trg+" < "+candidate+" > o2"
        #print cmd        
        #os.system(cmd)
        # testing
	(status, output) = commands.getstatusoutput(
            "(cat "+candidate+") 2>&1")
        #print "[tc] "+output

        (status, output) = commands.getstatusoutput(
            "./"+e_oracle+" < "+candidate+"")
        expOutput=output
        #print "[source output]"+output
        (status, output) = commands.getstatusoutput(
            "./"+e_trg+" < "+candidate+"")
        realOutput=output;
        #print "[follow output]"+realOutput
        
        if expOutput == realOutput:
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
    parser.add_argument("--trgName",help="the prefix for the exe file of the target program.i.e, pt for printtokens")
    parser.add_argument("--vID",type=int,help="the id of the faulty version")
    parser.add_argument("--ftc",help="the failing test case")
    parser.add_argument("--MR",help="the used MR,i.e.,MR1")
    parser.add_argument("--fName",help="")
    args=parser.parse_args();

    file1="/home/tzl/0DDMT/SIR/MT-and-DD/data/Replace/ori_args/"+args.fName
    fp=open(file1,"r")
    file_args=fp.read()

    file2="/home/tzl/0DDMT/SIR/MT-and-DD/data/Replace/Args_MR/"+args.MR+"_args/"+args.fName
    f=open(file2,"r")
    file_args2=f.read()
    file_args2=file_args2.replace("\n","")
    
    e_oracle="../v"+str(args.vID)+"/"+args.trgName+str(args.vID)+".exe"+" "+file_args
    e_trg="../v"+str(args.vID)+"/"+args.trgName+str(args.vID)+".exe"+" "+file_args2
    f_ftc=args.ftc

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
    print getN.printN()
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
