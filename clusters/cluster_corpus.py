import os
import csv
import sys
sys.path.insert(0, '/home/tzvi/PycharmProjects/HSdataprocessLinux/utils')  # added this so we can load the util functions from another directory
import util_functions as uf

data_path = '/home/tzvi/PycharmProjects/HSdataprocessLinux/data'
output_path = '/home/tzvi/PycharmProjects/HSdataprocessLinux/clusters'

with open(os.path.join(output_path, 'corpus.csv'), 'w') as output_file:
    fieldNames = ['file_id', 'text']
    out_write = csv.DictWriter(output_file, fieldnames=fieldNames)
    out_write.writeheader()

    for file in os.listdir(data_path):
        file_path = os.path.join(data_path, file)
        with open(file_path, 'r') as input_file:
            text = input_file.read().strip()
            text = uf.re_structure_text(text)
            text = uf.create_txt(text)
        out_write.writerow({'file_id': file[:-4], 'text': text})
