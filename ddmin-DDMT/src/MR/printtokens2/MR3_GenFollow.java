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
	
	public boolean isContainsNumStr(String str) {
		String regex=".*[0-9a-zA-Z]+.*";
		Matcher m = Pattern.compile(regex).matcher(str);
		return m.matches();
	}
	
	public void GenFollow() throws IOException {   
		BufferedReader fr=new BufferedReader(new FileReader(new File(this.path_stc)));
		BufferedReader fr2=new BufferedReader(new FileReader(new File(this.path_sop)));
		BufferedWriter fw=new BufferedWriter(new FileWriter(new File(this.path_ftc)));
		  String line="",tmp="",str="",mr_str;
		  int i,c;
		  List<String> keyList = new ArrayList<>();
		  List<String> errList = new ArrayList<>();
		  while((line=fr2.readLine())!=null)
		  {
              if(line.startsWith("error")) {           	  
            	  c=line.indexOf("\"",8);            	  
            	  str=line.substring(8,c);
            	  errList.add(str);
              }
              else if(line.startsWith("keyword")) {
            	  c=line.indexOf("\"",10);
            	  str=line.substring(10,c);
            	  keyList.add(str);
              }
		  }
			/*
			 * for(i=0;i<keyList.size();i++) { System.out.println(keyList.get(i)); }
			 */
		  while((line=fr.readLine())!=null) {
			  tmp=tmp+line+"\n";
		  }
			  
	      for(i=0;i<errList.size();i++) {
				  str=errList.get(i);
				  //System.out.println(isContainsNumStr(str));
				  //change the error tokens that contains num or alpha
				  if( tmp.contains(str) && isContainsNumStr(str) ) {					  
					  str=str.replaceAll("[^0-9a-zA-Z]", "");
					  mr_str="x"+str.substring(0,1)+"z"+str.substring(1);
					  //System.out.println(mr_str);
					  tmp=tmp.replace(str,mr_str);
					  //errList.remove(i);
				  }
				  //System.out.println(errList.get(i));
		  }
			  
		  for(i=0;i<keyList.size();i++) {
				  str=keyList.get(i);
				  //change the keyword like and or xor lambda.
				  if( tmp.contains(str) && isContainsNumStr(str)) {
					  mr_str=str.substring(0,1)+"xz"+str.substring(1);
					  tmp=tmp.replace(str,mr_str);
					  //keyList.remove(i);
				  }
				  //System.out.println(keyList.get(i));
		  }
		  fw.write(tmp);
		  fw.newLine();
		  
		  
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
