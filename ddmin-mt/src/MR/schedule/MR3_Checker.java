package schedule;

import java.util.regex.*;
import java.io.*;
import java.util.*;

class MR3_Checker{
  String so;
  String fo;
  public MR3_Checker(String a,String b)
  {
    this.so=a;
    this.fo=b;
  }
  public void Check() throws IOException
  {
	    	List<String> strListA = null;
		List<String> strListB = null;	
		BufferedReader brA = new BufferedReader(new FileReader(new File(this.so)));
		BufferedReader brB = new BufferedReader(new FileReader(new File(this.fo)));
		Pattern p = Pattern.compile("[0-9]+");
		strListA = new ArrayList<String>();
	        int sum_A=0;  	
		String line = brA.readLine();
		while (line != null) {
			Matcher m=p.matcher(line);
			if (!"".equals(line)) {
				boolean result_A=m.find();
				while(result_A){
					sum_A++;
					result_A=m.find();
				}
				strListA.add(line);
				/*String arr[]=line.split("\\s+");
				for(String a:arr)
				{
					sum_A+=1;
				}*/
			}
			line = brA.readLine();
		}
		//System.out.println(sum_A);
		int sum_B=0;
		strListB = new ArrayList<String>();
		line = brB.readLine();
		while (line != null) {
			Matcher n=p.matcher(line);
			if (!"".equals(line)) {
				boolean result_B=n.find();
				while(result_B){
					sum_B++;
					result_B=n.find();
				}
				strListB.add(line);
				/*&String brr[]=line.split("\\s+");
				for(String b:brr)
				{
					sum_B+=1;
				}*/
			}
			line = brB.readLine();
		}
		//System.out.println(sum_B);
		/*if (strListA.equals(strListB)) {
			System.out.println("Sat");
		} else {
			System.out.println("Vol");
		}*/
		if (sum_A==sum_B) {
			System.out.println("Sat");
		} else {
			System.out.println("Vol");
		}
		brA.close();
		brB.close();
  }

public static void main(String[] args) throws IOException
  {
     MR3_Checker mc=new MR3_Checker(args[0],args[1]);
     mc.Check();
  } 
}
