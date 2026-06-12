package printtokens;

import java.io.*;
import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;


public class MR3_GenFollow {
	String path_stc;
	String path_ftc;
    String path_sop; //source output

	public MR3_GenFollow(String a, String b, String c) {
		this.path_stc = a;
		this.path_ftc = b;
		this.path_sop=c;
	}
	
	public boolean isContainsNum(String str) {
		String regex=".*[0-9]+.*";
		Matcher m = Pattern.compile(regex).matcher(str);
		return m.matches();
	}
	
	public void GenFollow() throws IOException {   
		BufferedReader fr=new BufferedReader(new FileReader(new File(this.path_stc)));
		BufferedReader fr2=new BufferedReader(new FileReader(new File(this.path_sop)));
		BufferedWriter fw=new BufferedWriter(new FileWriter(new File(this.path_ftc)));
		  String line="",tmp="",str="",mr_str;
		  int i,c,r;
		  List<String> numList = new ArrayList<>();
		  List<String> errList = new ArrayList<>();
		  while((line=fr2.readLine())!=null)
		  {
              if(line.startsWith("error")) {           	  
            	  c=line.indexOf("\"",8);            	  
            	  str=line.substring(8,c);
            	  errList.add(str);
              }
              else if(line.startsWith("numeric")) {
            	  c=line.indexOf(".",9);
            	  str=line.substring(9,c);
            	  numList.add(str);
              }
		  }
		  
		  while((line=fr.readLine())!=null) {
			  tmp=tmp+line+"\n";
		  }
		  
			  
		  for(i=0;i<numList.size();i++) { 
					 str=numList.get(i);
					 //System.out.println(str);
				     r=tmp.indexOf(str);
				     //System.out.println(r);
					 if( r==0 || (r>0 && tmp.substring(r-1,r) != "#")) {
						 //System.out.println(str);
						 tmp=tmp.substring(0, r)+"1"+tmp.substring(r);
				     }
							/*
							 * mr_str="11"+str; tmp=tmp.replace(str, mr_str);
							 */
					 
		  }
			  
		  for(i=0;i<errList.size();i++) {
				  str=errList.get(i);
				  if( isContainsNum(str) ) {					  
					  mr_str=str.replaceAll("[^0-9]", "");
					  tmp=tmp.replace(str,mr_str);
				  }
		  }
			  fw.write(tmp);
			  fw.newLine();
		  
			
			/*
			 * for(i=0;i<numList.size();i++) { str=numList.get(i); mr_str=str.substring(0,
			 * 1)+"19"+str.substring(1); numList.set(i, mr_str);
			 * System.out.println(numList.get(i)); } for(i=0;i<errList.size();i++) {
			 * str=errList.get(i); if(isContainsNum(str)){
			 * System.out.println("it's sat token :"+errList.get(i));
			 * mr_str=str.replaceAll("[^0-9]", ""); errList.set(i, mr_str);
			 * System.out.println("it's mr token :"+errList.get(i)); }
			 * //System.out.println(numList.get(i)); }
			 */
			 
		  
		 
        fr.close();
        fr2.close();
        fw.flush();
        fw.close();
    }
	public static void main(String[] args) throws IOException {
		MR3_GenFollow mg = new MR3_GenFollow(args[0], args[1],args[2]);
		mg.GenFollow();

	}
}
