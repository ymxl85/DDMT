package printtokens;
import java.io.*;
import java.util.ArrayList;

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
    /**
     * check whether the string c contains alphabetic characters
     * @param c
     * @return
     */
    public boolean containChars(String c)
    {
    	boolean r=false;
    	int i;
    	for(i=0;i<c.length();i++)
    	{
    		if(c.charAt(i)>='A' && c.charAt(i)<='z')
    		{
    			r=true;
    			break;
    		}
    	}
    	return r;
    }
    /**
     * check whether a from os matches the corresponding item in bl
     * a is not a keyword, the item in bl should be the same as a
     * otherwise: the item in bl contains the value of a should be an identifier
     * @param a
     * @param bl
     * @return
     */
    public boolean isMatch(String a,ArrayList<String> bl)
    {
    	boolean r=true;
    	int i=a.indexOf(",");
    	if(i>0)
    	{
    	String type=a.substring(0,i);
    	String value=a.substring(i+1,a.length()).trim();
    	//System.out.println(type+"[===]"+value);
    	boolean t;
    	int j;
    	String vpart="";
    	if(type.equals("keyword") && this.containChars(value))//a refers to a keyword
    	{
    		t=false;
    		for(j=0;j<bl.size();j++)
    		{
    			if(bl.get(j).indexOf("identifier")==0)
    			{
    				i=bl.get(j).indexOf(",");
    				vpart=bl.get(j).substring(i+1,bl.get(j).length()).trim();
    				if(value.equalsIgnoreCase(vpart))
    				{
    				  //System.out.println("[OK1]"+bl.get(j));
    				  t=true;
    				  break;
    				}
    			}
    		}
    		if(t) r=t;
    		else r=false;
    	}
    	else //a does not refer to a keyword, then bl should contains a
    	{
    		t=false;
    		for(j=0;j<bl.size();j++)
    		{
    			if(a.equalsIgnoreCase(bl.get(j)))
    			{
    				t=true;
  				  //System.out.println("[OK2]"+bl.get(j));

    				break;
    			}
    		}
    		if(t)
    			r=true;
    		else
    			r=false;
    	}
    	}
    	return r;
    }
    public boolean compare()
    {
    	boolean r=true;
    	int i;
    	String line;
    	for(i=0;i<this.sl.size();i++)
    	{
    		line=this.sl.get(i);
    		if(!this.isMatch(line, this.fl))
    		{
    			r=false;
    			break;
    		}
    	}
    	return r;
    }
    public void checker() throws IOException {

        BufferedReader br1 = new BufferedReader(new FileReader(new File(this.path_so)));
        BufferedReader br2 = new BufferedReader(new FileReader(new File(this.path_fo)));
        String line="";
        ////////read the source output and follow-up output
        while((line=br1.readLine())!=null)
        	sl.add(line);
        while((line=br2.readLine())!=null)
        	fl.add(line);
        if(sl.size()!=fl.size())//os.size !=of.size==>violation
        	System.out.println("Vol");
        else
        {
          if(this.compare())
          	System.out.println("Sat");
          else
          	System.out.println("Vol");

        }
        
        
    }
    public static void main(String[] args) throws IOException {
    	MR1_Checker mg = new MR1_Checker(args[0],args[1]);
        mg.checker();
    }
}
