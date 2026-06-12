package printtokens;
import java.io.*;
import java.util.*;

public class MR1_Checker {
	String path_so;
	String path_fo;
    ArrayList<String> sl,fl;

	public MR1_Checker(String a, String b) {
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
	        while((line=br1.readLine())!=null){
	        	if(!line.contains("It can not get charcter"))
	        	sl.add(line);
	        }
	        while((line=br2.readLine())!=null){
	        	if(!line.contains("It can not get charcter"))
	        	fl.add(line);
	        }
	        if(sl.size()!=fl.size())//os.size !=of.size==>not equal ==>violation
	        	System.out.println("Vol");
	        else
	        {
               t=true;
               for(i=0;i<sl.size();i++)//sl==fl
               {
            	   if(!sl.get(i).equals(fl.get(i)))
            	   {
            		   t=false;
            		   break;
            	   }
               }
               if(t) System.out.println("Sat");
   	           else  System.out.println("Vol");      
	        } 
	}

	

	public static void main(String[] args) throws IOException {
		MR1_Checker mg = new MR1_Checker(args[0],args[1]);
		mg.Checker();
	}
}


