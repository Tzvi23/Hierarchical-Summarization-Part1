import nltk.data
import re
from nltk.stem import WordNetLemmatizer
from nltk.util import ngrams
from nltk.corpus import stopwords
import os
from xmlTree import createXmlDocument, createXmlDocument_v2, read_xml_file
from xmlTree import calculateStats
from utils.util_functions import re_structure_text, create_txt_file, import_regex, word_number_ratio
# import ssl
# region Overcome ssl error when downloading nltk data
# try:
#     _create_unverified_https_context = ssl._create_unverified_context
# except AttributeError:
#     pass
# else:
#     ssl._create_default_https_context = _create_unverified_https_context
#
# nltk.download()
# endregion


def get_jaccard_sim(str1, str2):
    str1 = re.sub('[^A-Za-z0-9\s%]+', '', str1).lower().split()
    lemmatizer = WordNetLemmatizer()
    for item in range(len(str1)):
        str1[item] = lemmatizer.lemmatize(str1[item])
    a = set(str1)
    str2 = str2.split()
    for item in range(len(str2)):
        str2[item] = lemmatizer.lemmatize(str2[item])
    b = set(str2)
    c = a.intersection(b)
    return float(len(c)) / (len(a) + len(b) - len(c))


def convertTupleToString(tup):
    return ' '.join(tup)


def surroundSectionTag(sentence, section_name, tag='\n<P>\n'):
    """
    This function surrounds the section_name found in the sentence with the tag provided.
    By default its <P>
    :param sentence: sentence that founded relation in the result dict
    :param section_name: key setcion name
    :param tag: default tag is <P>
    :return: new string with surrounded tag
    """
    if sentence.find(tag) == -1:
        sentence = re.sub('[^a-zA-Z0-9\s]', '', sentence)
        x = re.search(section_name, sentence, re.IGNORECASE)
        # if x is not None:
        if x is not None and x.start() == 0:
            return sentence[:x.start()] + ' ' + tag + sentence[x.start():x.end()] + tag + ' ' + sentence[x.end():]
    return sentence


# sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')  # punkt tokenizer from nltk package

sections_types = ['chairmans statement', 'chief executive officer ceo review', 'chief executive officer ceo report',
                  'governance statement',
                  'remuneration report',
                  'business review', 'financial review', 'operating review', 'highlights', 'auditors report',
                  'risk management', 'chairmans governance introduction',
                  'Corporate Social Responsibility CSR disclosures']


results_dict = dict()
sizeOfNGrams = 3
stop_words = stopwords.words('english')


# def chooseBest_NGram(test_ngrams, threshold, numSent):
#     for index in range(len(sections_types)):
#         res = [0] * sizeOfNGrams
#         for ngramtest in range(len(test_ngrams)):
#             res[ngramtest] = get_jaccard_sim(test_ngrams[ngramtest], sections_types[index])
#         maximum = res.index(max(res))
#         if res[maximum] > threshold:
#             # test_ngrams[maximum] = re.sub('[0-9]+\s?', '', test_ngrams[maximum])  # Removes numbers from the section name e: 04 chairmans statement => chairmans statement
#             if results_dict.get((test_ngrams[maximum], sections_types[index])) is None:
#                 results_dict[(test_ngrams[maximum], sections_types[index])] = [(max(res), numSent)]
#             else:
#                 results_dict[(test_ngrams[maximum], sections_types[index])].append((max(res), numSent))


# def main_preProcess():
#     # Checks if output directory exists, if not creates one
#     if not os.path.isdir("output"):
#         os.mkdir("output")
#
#     targetDataFolder = 'data/'
#     outputFolder = 'output/'
#     counterFile = 1  # For progress notification
#     numberOfFiles = len(os.listdir(targetDataFolder))
#     for filename in os.listdir(targetDataFolder):
#         if os.path.isfile(outputFolder + '/xml/' + filename + '.xml'):  # checks if file was already processed
#             print('[!] {0} already been processed. | Progress: {1}/{2}'.format(filename, counterFile, numberOfFiles))
#             counterFile += 1
#             continue
#         results_dict.clear()
#         print("Processing: {0} | Progress: {1}/{2}".format(filename, counterFile, numberOfFiles))
#         with open(targetDataFolder + filename, mode='r') as data:
#             originalData = data.read()
#             re_structure_text(originalData)
#             originalData = re.sub('\s+', ' ', originalData)  # Remove new lines
#             tokenized_text = sent_detector.tokenize(originalData.strip())  # Find sentences
#
#             for sent in range(len(tokenized_text)):
#                 s = tokenized_text[sent].lower()
#                 s = re.sub('[^a-zA-Z0-9\s]', '', s)
#                 tokens = [token for token in s.split() if token != ""]  # Tokenize by white space the sentence
#                 tokens = [word for word in tokens if word not in stop_words]  # Remove stop words from nltk.stopwords english
#                 output = list(ngrams(tokens, sizeOfNGrams))
#
#                 current_ngrams = list()
#                 counter = 0
#                 for ngram in range(len(output)):
#                     output[ngram] = convertTupleToString(output[ngram])
#                     # print(output[ngram])
#                     if not counter == 0 and (counter % sizeOfNGrams == 0 or ngram >= len(output)):
#                         chooseBest_NGram(current_ngrams, 0.5, sent)
#                         current_ngrams.clear()
#                     current_ngrams.append(output[ngram])
#                     counter += 1
#
#             # print(results_dict)
#             for key in results_dict.keys():
#                 for index_tuple in results_dict[key]:
#                     tokenized_text[index_tuple[1]] = surroundSectionTag(tokenized_text[index_tuple[1]], key[0])
#             if not os.path.exists(outputFolder):
#                 os.mkdir(outputFolder)
#             with open(outputFolder + filename, mode='w') as writer:
#                 for sent in tokenized_text:
#                     writer.write(sent + '\n')
#             createXmlDocument(tokenized_text, filename)
#         counterFile += 1
#
#     calculateStats()


# def main_preProcess_v2():
#     # Checks if output directory exists, if not creates one
#     if not os.path.isdir("output"):
#         os.mkdir("output")
#
#     targetDataFolder = 'data/'
#     outputFolder = 'output/'
#     counterFile = 1  # For progress notification
#     numberOfFiles = len(os.listdir(targetDataFolder))
#     for filename in os.listdir(targetDataFolder):
#         if os.path.isfile(outputFolder + '/xml/' + filename + '.xml'):  # checks if file was already processed
#             print('[!] {0} already been processed. | Progress: {1}/{2}'.format(filename, counterFile, numberOfFiles))
#             counterFile += 1
#             continue
#         results_dict.clear()
#         print("Processing: {0} | Progress: {1}/{2}".format(filename, counterFile, numberOfFiles))
#         with open(targetDataFolder + filename, mode='r') as data:
#             originalData = data.read()
#             restructured_text = re_structure_text(originalData)
#             create_txt_file(restructured_text, filename)
#             xml_filename = createXmlDocument_v2(restructured_text, filename)
#             read_xml_file(xml_filename, filename)
#         counterFile += 1


# def regression_reduction(target_folder, source_folder='output/text_xml'):
#     regex_rules = import_regex()
#     if not os.path.isdir(target_folder):
#         os.mkdir(target_folder)
#     counterFile = 1
#     numberOfFiles = len(os.listdir(source_folder))
#     for filename in os.listdir(source_folder):
#         print('Regex filtering for file {0} | Progress {1}/{2}'.format(filename, counterFile, numberOfFiles))
#         # if not os.path.isfile(target_folder + '/' + filename) and not filename == '18050.txt' and not filename == '6688.txt':
#         if not os.path.isfile(os.path.join(target_folder, filename)):
#             with open(os.path.join(source_folder, filename), mode='r') as txtXml:
#                 data_read = txtXml.read()
#                 data = data_read.split('\n')
#                 for index in range(len(data)):
#                     if word_number_ratio(data[index]) is False:
#                         data[index] = ''
#                         continue
#                     data[index] = re.sub(regex_rules[7], 'date', data[index])  # Date
#                     # print('[==]Filename: {0} \nSent: {1} \nRule:{2} \n'.format(filename, index, str(7)))
#                     data[index] = re.sub(regex_rules[8], 'date', data[index])  # Date
#                     # print('[==]Filename: {0} \nSent: {1} \nRule:{2} \n'.format(filename, index, str(8)))
#                     data[index] = re.sub(regex_rules[9], 'time', data[index])  # Time
#                     # print('[==]Filename: {0} \nSent: {1} \nRule:{2} \n'.format(filename, index, str(9)))
#                     data[index] = re.sub(regex_rules[10], 'time', data[index])  # Time
#                     # print('[==]Filename: {0} \nSent: {1} \nRule:{2} \n'.format(filename, index, str(10)))
#                     data[index] = re.sub(regex_rules[2], 'tel', data[index])  # Telephone
#                     # print('[==]Filename: {0} \nSent: {1} \nRule:{2} \n'.format(filename, index, str(2)))
#                     data[index] = re.sub(regex_rules[3], 'tel', data[index])  # Telephone
#                     # print('[==]Filename: {0} \nSent: {1} \nRule:{2} \n'.format(filename, index, str(3)))
#                     data[index] = re.sub(regex_rules[4], 'tel', data[index])  # Telephone
#                     # print('[==]Filename: {0} \nSent: {1} \nRule:{2} \n'.format(filename, index, str(4)))
#                     data[index] = re.sub(regex_rules[5], 'tel', data[index])  # Telephone
#                     # print('[==]Filename: {0} \nSent: {1} \nRule:{2} \n'.format(filename, index, str(5)))
#                     data[index] = re.sub(regex_rules[6], 'tel', data[index])  # Telephone
#                     # print('[==]Filename: {0} \nSent: {1} \nRule:{2} \n'.format(filename, index, str(6)))
#                     data[index] = re.sub(regex_rules[0], 'site', data[index])  # Site
#                     # print('[==]Filename: {0} \nSent: {1} \nRule:{2} \n'.format(filename, index, str(0)))
#                     data[index] = re.sub(regex_rules[1], 'email', data[index])  # Email
#                     # print('[==]Filename: {0} \nSent: {1} \nRule:{2} \n'.format(filename, index, str(1)))
#                     # for subIndex in range(11, 16):  # Long numbers
#                     #     data[index] = re.sub(regex_rules[subIndex], '', data[index])
#                     #     # print('[==]Filename: {0} \nSent: {1} \nRule:{2} \n'.format(filename, index, str(subIndex)))
#                 data = '\n'.join(x for x in data if x)
#                 with open(os.path.join(target_folder, filename), mode='w') as newTxtXml:
#                     newTxtXml.write(data)
#         counterFile += 1


def pre_process_single_file(original_file, discourse_project_input_dir):
    # Checks if output directory exists, if not creates one
    if not os.path.isdir("output"):
        os.mkdir("output")

    # Extracts just the file name from the path
    filename = original_file.split(os.path.sep)[-1]

    with open(original_file, mode='r', encoding='utf-8') as data:
        originalData = data.read()
        restructured_text = re_structure_text(originalData)
        create_txt_file(restructured_text, filename)
        xml_filename = createXmlDocument_v2(restructured_text, filename, path=discourse_project_input_dir)
        read_xml_file(xml_filename, filename)


# regression_reduction('output/regex_xml')
# main_preProcess_v2()
# pre_process_single_file(original_file='/home/tzvi/PycharmProjects/HSdataprocessLinux/30502.txt', discourse_project_input_dir='/home/tzvi/PycharmProjects/linuxDiscourse/src/Input/xml/')
