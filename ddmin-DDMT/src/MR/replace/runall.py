import os
import re

currentpath = os.getcwd()

def getrunallcon():           
    runallpath = '/home/tky/Anew/replace/runall.sh'
    try:
        with open(runallpath,'r')as f:
            conlists = f.readlines()
            f.close()
        return conlists
    except:
        return None

def bools(filename,runcons):   
    _filename = filename.split('_')
    for runcon in runcons:
        if _filename[0] in runcon and _filename[1] in runcon:
            return runcon
    else:
        return None

def universal(paths):  
    reslists = []
    # paths = 'F:\\pycharm\\Delta Debugging1111111\\replace\\MR1_args'
    try:
        filelists = os.listdir(paths)
    except:
        filelists = None
        print('input wrong')
    if filelists is not None:
        if runallcontent is not None:   
            for filename in filelists:     
                result = bools(filename,runallcontent)  
                if result is not None:
                    with open(paths + '/' + filename,'r')as f:
                        reslists.append([result,f.read()])
                        f.close()

    return reslists
if __name__ == '__main__':
    runallcontent = getrunallcon()
    # originalres = universal()
    # print(originalres)
    MR1_args = universal('/home/tky/Anew/replace/MR1_args')
    #MR2_args = universal('/home/tky/Anew/replace/MR2_args')
    #MR3_args = universal('/home/tky/Anew/replace/MR3_args')
    original_args = universal('/home/tky/Anew/replace/original_args')
    # print(MR1_args)

    for i in MR1_args:
        #print(i)
        # os.system(i[0].replace('..',currentpath.replace('\\','/')).replace('<','').replace('>',''))
        # print(i[0].replace('..',currentpath.replace('\\','/')).replace('<','').replace('>',''))
        # os.system(new_result)
        MR1_result = i[0].replace('..', currentpath.replace('\\', '/'))
        res = re.compile("exe (.*) <").findall(i[0])
        if not res or res[0] == '':
	    # print(res)
            pass
        else:
            MR1_result = MR1_result.replace(re.compile("exe (.*) <").findall(i[0])[0], i[1])
            # print(MR1_result)
            with open('MR1_runall.sh','a') as f1:
                f1.writelines(MR1_result)
            f1.close()
    print('MR1_SH END')

    for i in original_args:
	original_result = i[0].replace('..', currentpath.replace('\\', '/'))
        # print(new_result)
        ress = re.compile("exe (.*) <").findall(i[0])
        if not ress or ress[0] == '':
            pass
        else:
            original_result = original_result.replace(re.compile("exe (.*) <").findall(i[0])[0], i[1])
            with open('original_runall.sh', 'a') as f3:
                f3.writelines(original_result)
            f3.close()
    print('original_SH END')

"""
    for i in MR3_args:
        MR3_result = i[0].replace('..', currentpath.replace('\\', '/')).replace(
            re.compile("exe (.*) .*?<").findall(i[0])[0], i[1])
        # print(new_result)
        with open('MR3_runall.sh', 'a') as f3:
            f3.writelines(MR3_result)
        f3.close()
    print('MR3_SH END')
"""


"""
    for i in MR2_args:
        MR2_result = i[0].replace('..', currentpath.replace('\\', '/')).replace(
            re.compile("exe (.*) .*?<").findall(i[0])[0], i[1])
        # print(new_result)
        with open('MR2_runall.sh', 'a') as f2:
            f2.writelines(MR2_result)
        f2.close()
    print('MR2_SH END')
"""



