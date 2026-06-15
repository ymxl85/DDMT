import re
import os
with open('MR1_runall.sh','r+') as f1:
    MR1_lines = f1.readlines()
    # print(MR1_lines)
    MR1_lineresult = ""
    for line in MR1_lines:
        line_split = line.split('/')[-1]  
        line_replace = line_split.replace(line_split, 'ftc.txt\n')
        MR1line_result = line.replace(line_split, line_replace)
        MR1_lineresult += MR1line_result
    #print(MR1_lineresult)
with open('MR1_runall.sh','w+') as w1:
    w1.write(MR1_lineresult)
f1.close()
"""
with open('MR2_runall.sh','r+') as f2:
    MR2_lines = f2.readlines()
    # print(MR1_lines)
    MR2_lineresult = ""
    for line in MR2_lines:
        line_split = line.split('/')[-1]  
        line_replace = line_split.replace(line_split, 'ftc.txt\n')
        MR2line_result = line.replace(line_split, line_replace)
        MR2_lineresult += MR2line_result
    #print(MR1_lineresult)
with open('MR2_runall.sh','w+') as w2:
    w2.write(MR2_lineresult)
f2.close()

with open('MR3_runall.sh','r+') as f3:
    MR3_lines = f3.readlines()
    # print(MR1_lines)
    MR3_lineresult = ""
    for line in MR3_lines:
        line_split = line.split('/')[-1]  
        line_replace = line_split.replace(line_split, 'ftc.txt\n')
        MR3line_result = line.replace(line_split, line_replace)
        MR3_lineresult += MR3line_result
    #print(MR1_lineresult)
with open('MR3_runall.sh','w+') as w3:
    w3.write(MR3_lineresult)
f3.close()
"""


with open('original_runall.sh','r+') as f4:
    ori_lines = f4.readlines()
    # print(MR1_lines)
    ori_lineresult = ""
    for line in ori_lines:
        line_split = line.split('/')[-1]  
        line_replace = line_split.replace(line_split, 'stc.txt\n')
        oriline_result = line.replace(line_split, line_replace)
        ori_lineresult += oriline_result
    #print(MR1_lineresult)
with open('original_runall.sh','w+') as w4:
    w4.write(ori_lineresult)
f4.close()
