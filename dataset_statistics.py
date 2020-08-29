import os
import re
from pathlib import Path

def count_words(filePath):
    counter = 0
    for file in os.listdir(filePath):
        x = (filePath / file).read_text()
        x = re.sub(r'\n|\t', ' ', x)
        x = re.sub(r'[^A-Za-z\s]', ' ', x)
        x = re.sub(r'\s{2,}', ' ', x)
        counter += len(x.strip().split())
    return counter / len(os.listdir(filePath))

TEST_SET_PATH = Path('/home/tzvi/PycharmProjects/HSdataprocessLinux/data')
test_stats = dict()

test_stats['size'] = len(os.listdir(TEST_SET_PATH))
test_stats['words'] = count_words(TEST_SET_PATH)
print()
