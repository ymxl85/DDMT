package schedule;

import java.io.*;
import java.util.ArrayList;
import java.util.List;
/**
 * k=num("3")-num("4")
 * @author jmy
 *
 */
public class MR3_GenFollow {

	String in,out;
	public MR3_GenFollow(String a,String b)
	{
		this.in=a;
		this.out=b;
	}
	
	//valid: the nubmer of commmand 3 == number of command 4
	public int isValid(String a)
	{
		int r;
		int m=0,n=0;
		int i;
		for(i=0;i<a.length();i++)
		{
			if(a.charAt(i)=='3' && (i==0 || (i==1 && a.charAt(i-1)==' ') || (i>1 && a.charAt(i-1)==' ' && a.charAt(i-2)==' ')))
				m++;
			if(a.charAt(i)=='4' && (i==0 || (i>0 && a.charAt(i-1)==' ')))
				n++;
		}
		r=m-n;
		return r;
	}
	public boolean isValid2(String a)
	{
		boolean t=false;
		int i;
		for(i=0;i<a.length();i++)
		{
			if(a.charAt(i)=='6' && (i==0 || (i==1 && a.charAt(i-1)==' ') || (i>1 && a.charAt(i-1)==' ' && a.charAt(i-2)==' ')))
				t=true;
			if(a.charAt(i)=='7' && (i==0 || (i==1 && a.charAt(i-1)==' ') || (i>1 && a.charAt(i-1)==' ' && a.charAt(i-2)==' ')))
				t=true;
		}
		return t;
	}
	
	public void GenFollow() throws IOException
	{
		BufferedReader fr=new BufferedReader(new FileReader(new File(this.in)));
		BufferedWriter fw=new BufferedWriter(new FileWriter(new File(this.out)));
		String line,tmp="";
		int i,m=0,n = 0,max=0,k=0,M=0,N=0,r=0;
		int n3=0,n4=0;
		boolean t=false,r6=false;
		List<String> stringList = new ArrayList<>();
		while((line=fr.readLine())!=null)
		{
			/*
			 * r=isValid(line); if(r==0) { fw.write(line); fw.newLine(); } else if(r>0) {
			 * n3+=1; fw.newLine(); } else { n4+=1; fw.newLine(); }
			 */
			stringList.add(line);
		}
		
		//get the longest commands consists of commands ‘‘1’’, ‘‘2’’, ‘‘3’’, ‘‘4’’ or ‘‘5’’
		for (i = 0; i < stringList.size(); i++) {
		    String str = stringList.get(i);
		    //System.out.println(str);
		    r6=this.isValid2(str);
		    
		    if( t==false && r6 == true ) {
		    	m=i;
		    	//System.out.println("m is "+m);
		    	t=true;
		    	continue;
		    }
		    if( t==true && r6 == true ) {
		    	n=i;
		    	//System.out.println("n is "+n);
		    	t=false;
		    	continue;
		    }
		    max=Math.abs(m-n);
		    if(max > k) {
		    	k=max;
		    	if(m>n) {
		    		M=n;
			    	N=m;
		    	}
		    	else if(m<n){
		    		M=m;
		    		N=n;
		    	}
		    	
		    }
		}
		//System.out.println(k+" "+M+" "+N);
		
		//find Command "3" and "4" in the longest of commands list
		for(i=M+1;i<N;i++) {
			r=isValid(stringList.get(i));
			if(r>0) {
				n3+=r;
				stringList.set(i, "");
			}
			else if(r<0){
				n4+=Math.abs(r);
				stringList.set(i, "");
			}
		}
		k=n3-n4;
		//System.out.println("k is "+Math.abs(k)+" n3 is "+n3+" n4 is "+n4);
		tmp=stringList.get(M);
		if(k > 0) {
			for(i=0;i<k;i++)
				tmp=tmp+"\n3 ";
		}
		if(k < 0) {
			for(i=0;i<Math.abs(k);i++)
				tmp=tmp+"\n4 0.99 ";
		}
		stringList.set(M, tmp);
		for (i = 0; i < stringList.size(); i++) {
			fw.write(stringList.get(i)+"\n");
		}
		fr.close();
		fw.flush();
		fw.close();
	}
	public static void main(String[] args) throws IOException
	{
		MR3_GenFollow mg=new MR3_GenFollow(args[0],args[1]);
		mg.GenFollow();
	}
}
