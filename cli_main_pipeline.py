"""
Author: Tzvi Puchinsky
"""
import main_pipeline as mp
import argparse
import json
import pprint
import os
import datetime
import csv
from print_colors import bcolors
from gensimModelServer import build_model
from utils.json_converter import convert_data_to_json
import testing_grounds as tg
from Rouge.kavgan_rouge.kavganRouge import run_rouge_kavgan
import pickle

pp = pprint.PrettyPrinter()

# Construct argument parser
ap = argparse.ArgumentParser(description='HS Main pipeline CLI')

# Add arguments

FUNCTIONS = [
    'first_stage',
    'first_stage_loop',
    'second_stage',
    'third_stage',
    'fourth_stage',
    'run_stages',
    'build_model',
    'convert_corpus',
    'run_kmeans',
    'cluster_eval',
    'rouge_eval',
    'config_update',
    'config_print',
    'reset_data'
]

# Load config file
try:
    with open('json_config.txt', 'r') as config_file:
        config = json.load(config_file)
        print('\tNote: Config file loaded')
except FileNotFoundError as e:
    print(e)
    print('Error while loading config file. \n\t EXITING')
    exit(0)

def update_config(stage_choice=None, update_all=False):
    def choice_update(choice):
        """
        This function loops over the field in the json file based on the choice provided
        """
        for field in configFile[choice].keys():
            if isinstance(configFile[choice][field], str):
                print(f'Current: \n\t {field}: {configFile[choice][field]}')
                configFile[choice][field] = input(f'New {field} : ')
            elif field == 'models':
                for model_number in configFile[choice][field].keys():
                    print(f'Current: \n\t {model_number}: {configFile[choice][field][model_number]}')
                    new_status = input(f'New {model_number} Status [y,n]: ')
                    configFile[choice][field][model_number] = True if new_status.lower() in ['yes', 'y', 'true'] else False
            else:
                for path_name in configFile[choice][field].keys():
                    print(f'Current: \n\t {path_name}: {configFile[choice][field][path_name]}')
                    new_path = input(f'New {path_name} path: ')
                    configFile[choice][field][path_name] = new_path

    with open('json_config.txt', 'r') as update_file:
        configFile = json.load(update_file)
        options = list(configFile.keys())
        if update_all is True:
            for choice in options:
                print(f'{bcolors.FAIL}\t<! {choice} !>{bcolors.ENDC}')
                choice_update(choice)
        else:
            if stage_choice is None:
                choice = input('Choose one: ' + str(options) + '\nEnter Choice: ')
            else:
                choice = stage_choice
            choice_update(choice)
    # Write updated config file
    with open('json_config.txt', 'w') as update_file:
        json.dump(configFile, update_file)

def print_config():
    with open('json_config.txt', 'r') as update_file:
        configFile = json.load(update_file)
        print(json.dumps(configFile, indent=2))

def write_log(path, f_id, val_d, val_t, startEnd):
    with open(path, 'a+') as file:
        file.write(','.join([startEnd, f_id, val_d, val_t]) + '\n')

def build_queue(working_dir):
    print('Building queue')
    queue = list()
    for file in os.listdir(working_dir):
        with open(os.path.join(working_dir, file), 'r') as dataFile:
            text = dataFile.read()
            queue.append((file, len(text)))
    queue.sort(key=lambda x: x[1])
    return [file[0] for file in queue]

def processed_list(log_file):
    file_list = list()
    with open(log_file, 'r') as logFile:
        csv_reader = csv.reader(logFile, delimiter=',')
        for row in csv_reader:
            if row[1] not in file_list and (row[0] == 'end' or row[0] == 'proc'):
                file_list.append(row[1])
    return file_list


# Define parser arguments
ap.add_argument('command', choices=FUNCTIONS, help='Functions of the main pipeline')
ap.add_argument('-us', '--updateSpecific', help='[config_update VAR] Choose: ' + str(list(config.keys())))
ap.add_argument('-ap', '--all_path', help='[run_stages VAR] Provide path to data dir')
ap.add_argument('-NOT', '--number_of_topics', help='[build_model VAR] Number of topics: 4,6,10')
ap.add_argument('-cl', '--checkLog', help='[run_stages VAR] Provide log path to check if files been processed and skip them')
ap.add_argument('-cp', '--cluster_path', help='[run_kmeans VAR] path to the corpus for clustering. CSV file.')
ap.add_argument('-op', '--output_plots', help='[run_kmeans VAR] path to save plot files - directory')
args = ap.parse_args()

if args.command == 'config_print':
    print_config()
elif args.command == 'config_update':
    update_config(args.updateSpecific)
elif args.command == 'first_stage':
    mp.first_stage(config['first_stage']['inputFile_path'], config['first_stage']['discourseInput'])
elif args.command == 'first_stage_loop':
    if args.all_path is None:
        raise ImportError('Data path not provided use: [-ap] or [--all-path] <dir-path>')
    else:
        dir_path = args.all_path
        for file in os.listdir(dir_path):
            mp.first_stage(os.path.join(dir_path, file), config['first_stage']['discourseInput'])
        print(f'{bcolors.OKGREEN}Finished pre-processing{bcolors.ENDC}')
elif args.command == 'second_stage':
    mp.second_stage(config['second_stage']['xml_result_path'], config['second_stage']['discourse_script_path'])
elif args.command == 'third_stage':
    argument_list = [
        config['third_stage']['models'],
        config['third_stage']['models_path']
    ]
    mp.third_stage(config['third_stage']['file_id'], argument_list)
elif args.command == 'fourth_stage':
    mp.fourth_stage(config['fourth_stage']['file_id'])
elif args.command == 'run_stages':
    if args.all_path is None:
        raise ImportError('Data path not provided use: [-ap] or [--all-path] <dir-path>')
    else:
        if os.path.exists(args.all_path) and os.path.isdir(args.all_path):
            dir_path = args.all_path  # just a local variable for ease
            print(f'{bcolors.OKBLUE}You have first to initialize all the config data \n\t[Dont worry about the file ids] {bcolors.ENDC}')
            # update_config(stage_choice=None, update_all=True)  # TODO uncomment
            with open('json_config.txt', 'r') as config_file:
                config = json.load(config_file)
                print('\tNote: Config file loaded')
            print(f'{bcolors.OKGREEN}Great. Now that we done the process will loop over all the files in the data path. {bcolors.ENDC}')
            start = input('Start? [y/n]')
            if start.lower() in ['y', 'yes', 'yep']:
                # Create directory for logs if not exists
                if not os.path.exists('logs'):
                    os.mkdir('logs')
                log_path = 'logs'
                # Create log file for current run
                current_log = datetime.datetime.now().strftime("D%d_%m_%yM%H_%M")
                log_path = os.path.join(log_path, current_log) + '.txt'
                with open(log_path, 'w'):
                    pass
                # Build queue
                queue = build_queue(dir_path)
                # Build processed list if required
                proc_list = None
                if args.checkLog is not None:
                    try:
                        proc_list = processed_list(args.checkLog)
                    except FileNotFoundError:
                        print(f'{bcolors.FAIL}File not found!{bcolors.ENDC}')
                        exit(0)
                # Start the process
                for file in queue:
                    # Check if file been processed
                    if proc_list is not None and file in proc_list:
                        print(f'{bcolors.OKGREEN}{file} processed already.{bcolors.ENDC}')
                        write_log(log_path, file, datetime.datetime.now().strftime("%d/%m/%y"),datetime.datetime.now().strftime("%H:%M"), 'proc')
                        continue
                    write_log(log_path, file, datetime.datetime.now().strftime("%d/%m/%y"), datetime.datetime.now().strftime("%H:%M"), 'start')
                    # First stage
                    mp.first_stage(os.path.join(dir_path, file), config['first_stage']['discourseInput'])
                    # Second stage
                    mp.second_stage(file + '.xml',
                                    config['second_stage']['discourse_script_path'])

                    # Third stage
                    argument_list = [
                        config['third_stage']['models'],
                        config['third_stage']['models_path']
                    ]
                    mp.third_stage(file[:-4], argument_list)
                    # Fourth stage
                    mp.fourth_stage(int(file[:-4]))

                    # Fifth stage - show case
                    for key in config['third_stage']['models'].keys():
                        if config['third_stage']['models'][key] is True:
                            try:
                                mp.show_case(file[:-4], int(key))
                            except FileNotFoundError as e:
                                if not os.path.exists('show_case_error'):
                                    os.mkdir('show_case_error')
                                with open(os.path.join('show_case_error', file[:-4])) as error_file:
                                    error_file.write(str(e))
                    write_log(log_path, file, datetime.datetime.now().strftime("%d/%m/%y"), datetime.datetime.now().strftime("%H:%M"), 'end')
        else:
            raise FileExistsError('[--all-path] Check path: Exists? Is it a directory?')
elif args.command == 'build_model':
    if args.number_of_topics is None:
        raise ValueError('Provide number of topics 4/6/10')
    else:
        print(f'{bcolors.HEADER}\tBuild LDA model started{bcolors.ENDC}')
        build_model(int(args.number_of_topics))
elif args.command == 'convert_corpus':
    print(f'{bcolors.HEADER}\tConverting corpus to json{bcolors.ENDC}')
    convert_data_to_json()
elif args.command == 'run_kmeans':
    if args.cluster_path is None:
        raise ValueError('Provide corpus path using [-cp] / [--cluster_path]')
    if args.output_plots is None:
        raise ValueError('Provide output plots path using [-op] / [--output_plots]')
    else:
        print(f'{bcolors.WARNING}Importing cluster engine code...{bcolors.ENDC}')
        from clusters.cluster_engine_updated import run_kmeans
        run_kmeans(args.cluster_path, args.output_plots)
# Cluster eval
elif args.command == 'cluster_eval':
    if args.number_of_topics is None:
        raise ValueError('Provide number of topics 4/6/10')
    if args.checkLog is None:
        raise ValueError('Provide log file')
    tg.cluster_eval(topic_number=args.number_of_topics, log_path=args.checkLog)
# Rouge kavgan eval
elif args.command == 'rouge_eval':
    run_rouge_kavgan()
# Reset project - DELETE ALL DATA!!
elif args.command == 'reset_data':
    print(f'{bcolors.FAIL} Warning! Will delete all data after confirmation.\nAll paths can be seen at reset_project_paths.txt. {bcolors.ENDC}')
    from reset_project import reset_project
    reset_project()

