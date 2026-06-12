package schedule;

import java.io.*;
import java.util.ArrayList;
/**
 * replace "5" witth "3 4 0.9999"
 * @author jmy
 *
 */
public class MR1_GenFollow {

	String in,out;
	public MR1_GenFollow(String a,String b)
	{
		this.in=a;
		this.out=b;
	}
	public int find(String a,String b)
	{
		int x=0,y=0;
		int i,j=0;
		
		while(j<a.length() && (i=a.indexOf(b,j))>=0)
		{
			if(i==0) 
				x++;
			else if((i==1) && (a.charAt(i-1)==' '))
				x++;
			else if((i>=2) && (a.charAt(i-2)==' '))
				x++;
			j=i+1;
		}
		return x;
	}
	
	//valid: the nubmer of commmand 3 == number of command 4
	public boolean isValid(String a)
	{
		boolean r=false;
		int m=0,n=0;
		int i;
		for(i=0;i<a.length();i++)
		{
			if(a.charAt(i)=='3' && (i==0 || (i>0 && a.charAt(i-1)==' ')))
				m++;
			if(a.charAt(i)=='4' && (i==0 || (i>0 && a.charAt(i-1)==' ')))
				n++;
		}
		if(m==n) r=true;
		return r;
	}
	public void GenFollow() throws IOException
	{
		BufferedReader fr=new BufferedReader(new FileReader(new File(this.in)));
		BufferedWriter fw=new BufferedWriter(new FileWriter(new File(this.out)));
		String line,tmp="",all="";
		int i,j;
		int n3=0,n4=0;
		boolean t=false,q=true,p=false;
		while((line=fr.readLine())!=null)
		{
			//System.out.println(line);
                        all+=line;
			tmp="";
			
			if(q){
				j=this.find(line, "3");
				if(j>0){
					//System.out.println("is 3");
					q=false;
				}
				n3+=j;			
			}
			if(!q){
				j=this.find(line, "4");
				if(j>0){
					//System.out.println("is 4");
					q=true;
				}
				n4+=j;
			}
			if(n3==n4)
				p=true;
			else
				p=false;			
			
			//System.out.println(Integer.toString(n3)+"#"+Integer.toString(n4));
			  if(t==false && (i=line.indexOf("5"))>=0 && p==true)
			  {
				 
				 //if(i==0 && n3==n4) //5 ...
				 if(i==0)
				 {
					//the index of the unblock proc is calculated as: length*0.9999+1
					line="3\n 4 0.9999"+line.substring(1,line.length());
					t=true;
				 }
				 //else if (i>0 && line.charAt(i-1)==' ' && (n3+this.find(line.substring(0,i), "3")==(n4+this.find(line.substring(0,i), "4"))))
				 else if (i>0 && line.charAt(i-1)==' ')
				 {	
						if(i-2>0)
						  tmp=line.substring(0,i-2);
						tmp=tmp+" 3\n 4 0.99";
						if(i+1<line.length())
							tmp=tmp+line.substring(i+1,line.length());
						line=tmp;
						t=true;
			          }
			}
			//System.out.println("==>"+line);
			fw.write(line);
			fw.newLine();
		}
		fr.close();
		fw.flush();
		fw.close();
	}
	public static void main(String[] args) throws IOException
	{
		MR1_GenFollow mg=new MR1_GenFollow(args[0],args[1]);
		mg.GenFollow();
	}
}
