import subprocess
from print_colors import bcolors
import os
from shutil import copyfile

"""
Using https://github.com/kavgan/ROUGE-2.0 java package to evaluate the summaries.
Two folders need to be updated with results to work as an input to the evaluation process:
project/test-summarization/reference
project/test-summarization/system
Then a jar file is activated that starts the evaluation process.
Output: results.csv file with the results.
"""

# # Normalize the data files
# # System files
# system_files = os.listdir('/home/tzvi/PycharmProjects/HSdataprocessLinux/Rouge/kavgan_rouge/projects/test-summarization/reference')
# system_files = [file_id.split('_')[0] for file_id in system_files]
# # Reference files
# new_ref = '/home/tzvi/PycharmProjects/HSdataprocessLinux/Rouge/kavgan_rouge/norm_poly'
# cur_ref = '/home/tzvi/PycharmProjects/HSdataprocessLinux/Rouge/kavgan_rouge/projects/test-summarization/system'
# for ref_file in os.listdir(cur_ref):
#     print(ref_file)
#     if ref_file.split('_')[0] in system_files:
#         copyfile(os.path.join(cur_ref, ref_file), os.path.join(new_ref, ref_file))


"""
ans = input(f"Do you need to update the {bcolors.FAIL}reference folder?{bcolors.ENDC} [y/n] \npath:HSdataprocessLinux/Rouge/kavgan_rouge/projects/test-summarization/reference \nANSWER: ")
if ans.lower() == 'y':
    print(f'{bcolors.WARNING}Update folder and start again{bcolors.ENDC}')
    exit(0)

ans = input(f"Do you need to update the {bcolors.FAIL}system folder?{bcolors.ENDC} [y/n] \npath:HSdataprocessLinux/Rouge/kavgan_rouge/projects/test-summarization/system \nANSWER: ")
if ans.lower() == 'y':
    print(f'{bcolors.WARNING}Update folder and start again{bcolors.ENDC}')
    exit(0)
"""
# ROUGE - 1

kavgan_jar = '/home/tzvi/PycharmProjects/HSdataprocessLinux/Rouge/kavgan_rouge/rouge2-1.2.2.jar'  # Absolute path to the jar file
subprocess.call(['java', '-jar', kavgan_jar])

# ROUGE - 2
with open('rouge.properties', 'r') as prop_file:
    txt = prop_file.read()
    txt = txt.replace('ngram=1', 'ngram=2').replace('R1', 'R2')
with open('rouge.properties', 'w') as prop_file:
    prop_file.write(txt)

kavgan_jar = '/home/tzvi/PycharmProjects/HSdataprocessLinux/Rouge/kavgan_rouge/rouge2-1.2.2.jar'  # Absolute path to the jar file
subprocess.call(['java', '-jar', kavgan_jar])

# ROUGE - L
with open('rouge.properties', 'r') as prop_file:
    txt = prop_file.read()
    txt = txt.replace('ngram=2', 'ngram=L').replace('R2', 'RL')
with open('rouge.properties', 'w') as prop_file:
    prop_file.write(txt)

kavgan_jar = '/home/tzvi/PycharmProjects/HSdataprocessLinux/Rouge/kavgan_rouge/rouge2-1.2.2.jar'  # Absolute path to the jar file
subprocess.call(['java', '-jar', kavgan_jar])

# Reset
with open('rouge.properties', 'r') as prop_file:
    txt = prop_file.read()
    txt = txt.replace('ngram=L', 'ngram=1').replace('RL', 'R1')
with open('rouge.properties', 'w') as prop_file:
    prop_file.write(txt)