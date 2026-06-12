package schedule;

import java.io.*;
import java.util.*;

class MR1_Checker{
  String so;
  String fo;
  public MR1_Checker(String a,String b)
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
		strListA = new ArrayList<String>();
	              	
		String line = brA.readLine();
		while (line != null) {
			if (!"".equals(line)) {
				strListA.add(line);
			}
			line = brA.readLine();
		}

		strListB = new ArrayList<String>();
		line = brB.readLine();
		while (line != null) {
			if (!"".equals(line)) {
				strListB.add(line);
			}
			line = brB.readLine();
		}
		if (strListA.equals(strListB)) {
			System.out.println("Sat");
		} else {
			System.out.println("Vol");
		}
		brA.close();
		brB.close();
  }

public static void main(String[] args) throws IOException
  {
     MR1_Checker mc=new MR1_Checker(args[0],args[1]);
     mc.Check();
  } 
}


