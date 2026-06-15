package printtokens;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;

public class MR2_Checker {
	String path_so;
	String path_fo;
    ArrayList<String> sl,fl;

	public MR2_Checker(String a, String b) {
		this.path_so = a;
		this.path_fo = b;
		sl=new ArrayList<String>();
        fl=new ArrayList<String>();
	}

	public void Checker() throws IOException {
		 BufferedReader br1 = new BufferedReader(new FileReader(new File(this.path_so)));
	        BufferedReader br2 = new BufferedReader(new FileReader(new File(this.path_fo)));
	        String line="";
	        boolean t=true;
	        int i;
	        ////////read the source output and follow-up output
	        while((line=br1.readLine())!=null)
	        {
	        	if(!line.contains("It can not get charcter"))
	        	  sl.add(line);
	        }
	        while((line=br2.readLine())!=null)
	        {
	        	if(!line.contains("It can not get charcter"))
	        	fl.add(line);
	        }
	        /////////////////////////////////////check fl is a subset of sl
	           if(fl.size()>sl.size()) t=false;
	           else{
               t=true;
               for(i=0;i<fl.size();i++)
               {
            	   if(!sl.contains(fl.get(i)))
            	   {
            		   t=false;
            		   break;
            	   }
               }
	           }
               if(t) System.out.println("Sat");
   	           else  System.out.println("Vol");      
	         
	}

	

	public static void main(String[] args) throws IOException {
		MR2_Checker mg = new MR2_Checker(args[0],args[1]);
		mg.Checker();
	}
}
