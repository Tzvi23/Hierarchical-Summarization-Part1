import subprocess
from print_colors import bcolors
from project_config import parser
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

def run_rouge_kavgan():
    # ROUGE - 1
    kavgan_jar = parser.get('rouge', 'abs_jar')
    # kavgan_jar = '/home/tzvi/PycharmProjects/HSdataprocessLinux/Rouge/kavgan_rouge/rouge2-1.2.2.jar'  # Absolute path to the jar file
    subprocess.call(['java', '-jar', kavgan_jar])

    # ROUGE - 2
    with open('rouge.properties', 'r') as prop_file:
        txt = prop_file.read()
        txt = txt.replace('ngram=1', 'ngram=2').replace('R1', 'R2')
    with open('rouge.properties', 'w') as prop_file:
        prop_file.write(txt)

    # kavgan_jar = '/home/tzvi/PycharmProjects/HSdataprocessLinux/Rouge/kavgan_rouge/rouge2-1.2.2.jar'  # Absolute path to the jar file
    subprocess.call(['java', '-jar', kavgan_jar])

    # ROUGE - L
    with open('rouge.properties', 'r') as prop_file:
        txt = prop_file.read()
        txt = txt.replace('ngram=2', 'ngram=L').replace('R2', 'RL')
    with open('rouge.properties', 'w') as prop_file:
        prop_file.write(txt)

    # kavgan_jar = '/home/tzvi/PycharmProjects/HSdataprocessLinux/Rouge/kavgan_rouge/rouge2-1.2.2.jar'  # Absolute path to the jar file
    subprocess.call(['java', '-jar', kavgan_jar])

    # Reset
    with open('rouge.properties', 'r') as prop_file:
        txt = prop_file.read()
        txt = txt.replace('ngram=L', 'ngram=1').replace('RL', 'R1')
    with open('rouge.properties', 'w') as prop_file:
        prop_file.write(txt)