package schedule;

import java.io.*;
import java.util.ArrayList;
/**
*replace 1 i+1 with 1 i 2 i 1.00
*/

public class MR2_GenFollow{

	String in,out;
	public MR2_GenFollow(String a,String b)
	{
		this.in=a;
		this.out=b;
	}
	public int find(String a,String b)
	{
		int x=0;
		int i,j;
		j=0;
		while(j<a.length() && (i=a.indexOf(b,j))>=0)
		{
			if(i==0)
				x++;
			else if(a.charAt(i-1)==' ')
				x++;
			j=i+1;
		}
		return x;
		
	}

	public void GenFollow() throws IOException
	{
		BufferedReader fr1=new BufferedReader(new FileReader(new File(this.in)));
		BufferedReader fr2=new BufferedReader(new FileReader(new File(this.in)));
		BufferedWriter fw=new BufferedWriter(new FileWriter(new File(this.out)));
		String line,tmp="";
		int i;
		int n3=0,n4=0,n5_total=0,n5=0;
		boolean t=false;
		while((line=fr1.readLine())!=null)
		{
			n5_total+=this.find(line,"5");
		}
		//System.out.println(n5_total);
		while((line=fr2.readLine())!=null)
		{
			tmp="";
			//n3+=this.find(line,"1");
			//n4+=this.find(line,"2");
			n5+=this.find(line,"5");
			
			if(t==false && (n5 == n5_total))
			{
				//System.out.println("1 2 at===="+Integer.toString(i));
				if((i=line.indexOf("1 2"))==0)
				{
					
					line="1 1\n2 1 0.99 "+line.substring(3,line.length());
					t=true;
				}
				else if(t==false && (i=line.indexOf("1 3"))==0)
				{
					
					line="1 2\n2 2 0.99 "+line.substring(3,line.length());
					t=true;
				}
				else if (t==false && (i=line.indexOf("1 2"))>0)
				{
					if(i-2>0)
						tmp=line.substring(0,i-1);
						//System.out.println(tmp);
					tmp=tmp+" 1 1\n2 1 0.9999 ";
					if(i+1<line.length())
						tmp=tmp+line.substring(i+3,line.length());
					line=tmp;
					t=true;
				}
				else if (t==false && (i=line.indexOf("1 3"))>0)
				{
					if(i-2>0)
						tmp=line.substring(0,i-1);
					tmp=tmp+" 1 2\n2 2 0.9999 ";
					if(i+1<line.length())
						tmp=tmp+line.substring(i+3,line.length());
					line=tmp;
					t=true;
				}
			}
			fw.write(line);
			fw.newLine();	
		}
		fr1.close();
		fr2.close();
		fw.flush();
		fw.close();
	}
	 	
	public static void main(String[] args) throws IOException
	{
		MR2_GenFollow mg=new MR2_GenFollow(args[0],args[1]);
		mg.GenFollow();
	}
}
