import os
import subprocess
from project_config import parser

def reset_project():
    with open('reset_project_paths.txt', 'r') as rst_path:
        paths = rst_path.readlines()
        paths = ['rm ' + line[:-1] for line in paths]
        choice1 = input('[WARNING!] This will delete all the data for the project!\nAre you sure? [to continue type yes]\n')
        if choice1.lower() == 'yes':
            choice2 = input('Verify again! type yes!\n')
            if choice2.lower() == 'yes!':
                for path in paths:
                    print(f'Deleting data: {path}')
                    subprocess.run(path, shell=True)
                discourse_output = parser.get('LDA_process', 'loop_discourse_results_one_file_discourse_output_dir') # from project_paths.ini
                discourse_output1 = discourse_output + '/*'
                discourse_output2 = discourse_output + '/Nucleus/*'
                print('Deleting data: ' + discourse_output1)
                subprocess.run('rm ' + discourse_output1, shell=True)
                print('Deleting data: ' + discourse_output2)
                subprocess.run('rm ' + discourse_output2, shell=True)
                discourse_input = parser.get('main_pipeline', 'discourseInput')
                discourse_input1 = discourse_input + '*'
                discourse_input2 = ' '.join(['rm', '-r', discourse_input1.replace('xml/', 'xmlParse/')])
                print('Deleting data: ' + discourse_input1)
                subprocess.run('rm ' + discourse_input1, shell=True)
                print('Deleting data: ' + discourse_input2)
                subprocess.run(discourse_input2, shell=True)
            else:
                print('Aborted')
        else:
            print('Aborted')

reset_project()
