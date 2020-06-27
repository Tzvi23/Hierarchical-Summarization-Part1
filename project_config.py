from configparser import ConfigParser

config_file_path = 'project_paths.ini'

parser = ConfigParser()
parser.read(config_file_path)
