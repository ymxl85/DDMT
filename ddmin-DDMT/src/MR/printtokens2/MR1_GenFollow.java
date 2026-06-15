package printtokens;
import java.io.*;

public class MR1_GenFollow {
	String path_stc;
	String path_ftc;

	public MR1_GenFollow(String a, String b) {
		this.path_stc = a;
		this.path_ftc = b;
	}
    public boolean isCommentLine(int[] a,int pos)
    {
    	boolean r=true;
    	int i;
    	for(i=0;i<pos;i++)
    	{
    		if(a[i]!=' ')
    		{
    			r=false;
    			break;
    		}
    	}
    	
    	return r;
    }
	public void GenFollow() throws IOException {   
		FileInputStream fr=new FileInputStream(new File(this.path_stc));
		  FileOutputStream fw=new FileOutputStream(new File(this.path_ftc));
		  int c=1;
		  int[] line=new int[1000];
		  int i=0,j;
		  int pos,le,re;
		  while(true)
		  {
			 c=fr.read();
			 //System.out.println(c);
			 if(c==-1) break; //the	 end of the file
			 
			 i=0;
			 pos=-1;
			 le=-1;re=-1;//ready for record "
			 while(c!=-1 && c!='\n' && c!='\r')//read a line,line stores all characters except of \n
			 {	
				 line[i]=c;
				 if(c==';' && pos==-1) 
				 {
					// System.out.println("[;]"+Integer.toString(i)+"[l;]"+Integer.toString(le)+"[r:]"+Integer.toString(re));
					 pos=i; //record the first location of ';'
					 if(i-1>=0 && line[i-1]=='#')//#;, ; does not indicate a comment
						 pos=-1;
				 }
				 if(c=='\t')
				 {
					 if(le>=0 && re<0) 
				     {
					//System.out.println("tab:le-1");
					 le=-1;}
					 pos=-1;
				 }
				 if(c=='"')
				 {
					// System.out.println("[\"]"+Integer.toString(i));
					 if(le<0)//read the left quotation
					 {
						 le=i;
					 }
					 else if(le>=0 && re<0) //read the right quotation
					 {
						 re=i;
						 if(pos>le && pos<re) //";"this is not a comment
						 {
							 //System.out.println("inside");
							 pos=-1;
						 }
						 le=-1;re=-1;//ready for record the next pair of ""
					 }
				 }
				 
				 i++;
				 c=fr.read();
				 //System.out.println("[line]"+c);

			 }
			 if(le>=0 && re<0) pos=-1;
			 line[i]=c;//the last character
			 if(pos>=0)//line contains comments
			 {
				 if(pos==0 || this.isCommentLine(line, pos))//the whole line is a comment, then print nothing in tf
					 continue;
				 else
				 {
					 for(j=0;j<pos;j++)
						 fw.write(line[j]);
					 if(line[i]!=-1) fw.write(line[i]);
				 }
			 }
			 else //line does not contain comments
			 {
				 for(j=0;j<=i;j++)
					 fw.write(line[j]);
			 }
		  }
        fr.close();
        fw.flush();
        fw.close();
    }
	public static void main(String[] args) throws IOException {
		MR1_GenFollow mg = new MR1_GenFollow(args[0], 
	    		 args[1]);
		mg.GenFollow();

	}
}


