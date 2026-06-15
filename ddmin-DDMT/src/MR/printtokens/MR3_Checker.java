package printtokens;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;

public class MR3_Checker {
	String path_so;
	String path_fo;
    ArrayList<String> sl,fl;

	public MR3_Checker(String a, String b) {
		this.path_so = a;
		this.path_fo = b;
	}

	public void Checker() throws IOException {
		BufferedReader br1 = new BufferedReader(new FileReader(new File(this.path_so)));
		BufferedReader br2 = new BufferedReader(new FileReader(new File(this.path_fo)));
		String line;
		int err_num=0,num_num=0,mr_err_num=0,mr_num_num=0;
		int s_total,f_total;
		
	    while( (line=br1.readLine()) != null) {
	    	if(line.startsWith("error")) {           	  
          	  	  err_num+=1;
            }
            else if(line.startsWith("numeric")) {
          	  	  num_num+=1;
            }
	    }
	    //System.out.println("error "+err_num+"numeric "+num_num);
	    s_total=err_num+num_num;
	    
	    while( (line=br2.readLine()) != null) {
	    	if(line.startsWith("error")) {           	  
	    		mr_err_num+=1;
            }
            else if(line.startsWith("numeric")) {
            	mr_num_num+=1;
            }
	    }
	    //System.out.println("error "+mr_err_num+"numeric "+mr_num_num);
	    f_total=mr_err_num+mr_num_num;
	    
	    if(s_total == f_total) 
	    	System.out.println("Sat");
	    else
	    	System.out.println("Vol");
	    
	}

	

	public static void main(String[] args) throws IOException {
		MR3_Checker mg = new MR3_Checker(args[0],args[1]);
		mg.Checker();
	}
}
