import main_pipeline as mp
import argparse
import json
import pprint

pp = pprint.PrettyPrinter()

# Construct argument parser
ap = argparse.ArgumentParser(description='HS Main pipeline CLI')

# Add arguments

FUNCTIONS = [
    'first_stage',
    'second_stage',
    'third_stage',
    'config_update',
    'config_print'
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

def update_config(stage_choice=None):
    with open('json_config.txt', 'r') as update_file:
        configFile = json.load(update_file)
        options = list(configFile.keys())
        if stage_choice is None:
            choice = input('Choose one: ' + str(options) + '\nEnter Choice: ')
        else:
            choice = stage_choice
        for field in configFile[choice].keys():
            if isinstance(configFile[choice][field], str):
                print(f'Current: \n\t {field}: {configFile[choice][field]}')
                configFile[choice][field] = input(f'New {field} : ')
            elif field == 'models':
                for model_number in configFile[choice][field].keys():
                    print(f'Current: \n\t {model_number}: {configFile[choice][field][model_number]}')
                    new_status = input(f'New {model_number} Status [y,n]: ')
                    configFile[choice][field][model_number] = True if new_status.lower() in ['yes', 'y', 'true'] else False
    with open('json_config.txt', 'w') as update_file:
        json.dump(configFile, update_file)

def print_config():
    with open('json_config.txt', 'r') as update_file:
        configFile = json.load(update_file)
        print(json.dumps(configFile, indent=2))


ap.add_argument('command', choices=FUNCTIONS, help='Functions of the main pipeline')
ap.add_argument('-us', '--updateSpecific', help='Choose: ' + str(list(config.keys())))
args = ap.parse_args()

if args.command == 'config_print':
    print_config()
elif args.command == 'config_update':
    update_config(args.updateSpecific)
elif args.command == 'first_stage':
    mp.first_stage(config['first_stage']['inputFile_path'], config['first_stage']['discourseInput'])
elif args.command == 'second_stage':
    mp.second_stage(config['second_stage']['xml_result_path'], config['second_stage']['discourse_script_path'])
elif args.command == 'third_stage':
    argument_list = [
        config['third_stage']['models'],
        config['third_stage']['models_path']
    ]
    mp.third_stage(config['third_stage']['file_id'], argument_list)
