package printtokens;

import java.io.*;
class MR1_GenFollow{
	  String path_stc;
	  String path_ftc;
	  public MR1_GenFollow(String a,String b)
	  {
	    this.path_stc=a;
	    this.path_ftc=b;
	  }
	  public void GenFollow() throws IOException
	  {
	    /*BufferedReader br=new BufferedReader(new FileReader(new File(this.path_stc)));
	    BufferedWriter bw=new BufferedWriter(new FileWriter(new File(this.path_ftc)));
	    String stc;
	    //System.out.println("stc="+stc);
	    String ftc = "";
	    while ((stc=br.readLine()) != null) {
			   ftc= stc.toUpperCase();
			   bw.write(ftc);
			   bw.newLine();      
			   System.out.println(stc);
			   System.out.println(ftc);
        }
	    
	    // bw.write(ftc);
	    bw.flush();
	    br.close();
	    bw.close();*/
		  FileInputStream fr=new FileInputStream(new File(this.path_stc));
		  FileOutputStream fw=new FileOutputStream(new File(this.path_ftc));
		  int c;
		  while((c=fr.read())!=-1)
		  {
			  
			  if(c>=97 && c<=122)
				  c=c-32;		  	  
			  fw.write(c);
		  }
          fr.close();
          fw.flush();
          fw.close();
	  }
	  public static void main(String[] args) throws IOException
	  {
	     MR1_GenFollow mg=new MR1_GenFollow(args[0], 
	    		 args[1]);
	     mg.GenFollow();
	  } 
}
