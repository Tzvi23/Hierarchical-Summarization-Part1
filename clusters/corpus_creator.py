import os
import csv
import re

def create_clustering_corpus(dir_data_path, output_path, file_name='after_corpus.csv'):
    if not os.path.isdir(dir_data_path):
        print(f'Cant find dir path try again. Dir path given: {dir_data_path}')
        return
    else:
        print('[!!] Starting the corpus creation ...')
        with open(os.path.join(output_path, file_name), 'w') as output_file:
            fieldNames = ['file_id', 'text']
            out_write = csv.DictWriter(output_file, fieldnames=fieldNames)
            out_write.writeheader()

            for file in os.listdir(dir_data_path):
                file_path = os.path.join(dir_data_path, file)
                with open(file_path, 'r') as input_file:
                    txt = input_file.read().strip()
                    txt = re.sub(r'[\n]', ' ', txt).strip()
                if file_name != 'after_corpus.csv':
                    out_write.writerow({'file_id': file[:-4], 'text': txt})
                else:
                    out_write.writerow({'file_id': file[:-12], 'text': txt})
        print('[!!] New after_corpus.csv Created!')


