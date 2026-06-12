import java.io.*;
import java.util.ArrayList;


public class ResultAnalyzer {
  String rFile;
  String size;
  String runtime;
  String nTest;
  String fDeltas;
  //int numOfTests;
  public ResultAnalyzer(String a)
  {
	  this.rFile=a;
	  this.size="";
	  //this.numOfTests=0;
          this.nTest="";
          this.runtime="";
	  this.fDeltas="";
  }
  public void analyze() throws IOException
  {
	  RandomAccessFile rf=new RandomAccessFile(this.rFile,"r");
	  long flength=rf.length();
	  long head=rf.getFilePointer();
	  long cur=head+flength-1;
      	  String end="";
	  String line;
	  rf.seek(cur);
	  int c,i,j;
	  //System.out.println(this.rFile);
      	  String min1;
	  while(cur>head)
	  {
		  c=rf.read();
		  if(c=='\n' || c=='\r')
		  {
			  line=rf.readLine();
			  if(line!=null)
			    end=line+"\n"+end;
			  /*if(this.fDeltas.equals("") && line!=null && line.startsWith("dd: ") && line.indexOf("deltas left") !=-1)
	     		  {
				  System.out.println(line);
		 		  i=line.indexOf("dd: ")+"dd: ".length();
		 		  j=line.indexOf("deltas left");
		 		  this.fDeltas=end.substring(i,j-1).trim();
	     		  }*/
			  if(line!=null && line.startsWith("The 1-minimal failure-inducing input is"))
			  {
				  //i=line.lastIndexOf(" ");
				  i=end.indexOf("The 1-minimal failure-inducing input is")+"The 1-minimal failure-inducing input is ".length();
                  		  j=end.indexOf("The number of tests:");
				  min1=end.substring(i,j-1);
                                  this.fDeltas=min1;
                                 // System.out.println(min1);
                                  this.size=Integer.toString(min1.length());
                                  
			  }
		          if(line!=null && line.startsWith("The number of tests:"))
		          {
			   	  String tests;
		         	  i=end.indexOf("The number of tests:")+"The number of tests:".length();
		         	  j=end.indexOf("Removing any element will make the failure go away.");
			 	  this.nTest=end.substring(i,j-1).replace("None","").trim();
		         //this.nTest=end.substring(i,j-1).trim();
		          }
			  /*if(line!=null && line.startsWith("dd (run #"))
			  {
				  i=line.indexOf("#");
				  j=line.indexOf(")", i+1);
				  this.numOfTests=Integer.parseInt(line.substring(i+1,j));
				  break;
			  }*/
                          
		          if(line!=null && line.startsWith("The run time is:"))
		          {
		                  i=end.indexOf("The run time is:")+"The run time is:".length();
		                  this.runtime=end.substring(i).trim();
		          }
	     
		  }
		  cur--;
		  rf.seek(cur);
	  }
  }
  public static void main(String[] args) throws IOException
  {
	  ResultAnalyzer ar=new ResultAnalyzer(args[0]);
	  ar.analyze();
	  //System.out.println(ar.min1);//size
	  System.out.println(ar.size+";"+ar.nTest+";"+ar.runtime+";"+ar.fDeltas);//runs
          //System.out.println(ar.runtime);//time
  }
}
