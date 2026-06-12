package printtokens;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;

public class MR2_GenFollow {
	String path_stc;
	String path_ftc;

	public MR2_GenFollow(String a, String b) {
		this.path_stc = a;
		this.path_ftc = b;
	}
	/**
	 * generate a random integer in the range [2,n]
	 * @param n
	 * @return
	 */
    public int GenRandomNum(int n)
    {
    	int r=2+(int)(Math.random()*(n-2+1));
    	return r;
    }
	public void GenFollow() throws IOException {   
		FileInputStream fr=new FileInputStream(new File(this.path_stc));
		  FileOutputStream fw=new FileOutputStream(new File(this.path_ftc));
		  int c;
		  int counter=1;
		  int r=this.GenRandomNum(20);
		  boolean w=true;//for the first line
		//  System.out.println(r);
		  while((c=fr.read())!=-1)
		  {
			  if(w) {fw.write(';');w=false;}
			  fw.write(c);
                          //System.out.println(c);
			  if(c=='\n'){ //|| c=='\r'
                                  //if(c=='\n') System.out.println('#');
                                  //else System.out.println('!');
				  if(counter==1 || counter==r) 
				  {
					 // System.out.println("***"+Integer.toString(counter));
					  w=true;//ready for write ;//fw.write(';'); //comment the 1st and the 3rd line
				  }
				  counter++;
			  }
		  }
        fr.close();
        fw.flush();
        fw.close();
    }
	public static void main(String[] args) throws IOException {
		MR2_GenFollow mg = new MR2_GenFollow(args[0], 
	    		 args[1]);
		mg.GenFollow();

	}
}
