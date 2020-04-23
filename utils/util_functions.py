import csv
import os
import re
import copy
from nltk import WordNetLemmatizer


def import_regex(path='/home/tzvi/PycharmProjects/HSdataprocessLinux/utils/regex_preprocess.csv'):
    """
    Imports as list of regex expressions from file
    :param path: path to regex file
    :return: list of regex expressions in lower state
    """
    if not os.path.isfile(path):
        raise FileNotFoundError('File Not exists, supply full path with extension')
    else:
        regex_arguments = list()
        with open(path, mode='r') as regex_file:
            csv_reader = csv.reader(regex_file, delimiter=',')
            for row in csv_reader:
                regex_arguments.append(row[2])
            regex_arguments.pop(0)
        return regex_arguments


def test_regex_import():
    test = import_regex()
    print(test)


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


def strip_tags(sent, tag):
    if tag != 'H':
        return sent.replace('<'+tag+'>', '').replace('</'+tag+'>', '').strip()
    else:
        current_tag = sent[:sent.find('>') + 1]
        current_tag_split = current_tag.split('-')
        sent = sent.replace('<'+tag+'-'+current_tag_split[1][:-1]+'>', '').replace('</'+tag+'-'+current_tag_split[1][:-1]+'>', '').strip()
        return (sent, int(current_tag_split[1][:-1]))


def create_txt_file(data, filename, path='output/'):
    local_path = path + 'text'
    if not os.path.isdir(local_path):
        os.mkdir(local_path)
    with open(local_path + '/' + filename, mode='w') as writer:
        for sent in data:
            if sent.startswith('<S'):
                stripSent = strip_tags(sent, 'S')
            elif sent.startswith('<OneItem'):
                stripSent = strip_tags(sent, 'OneItem')
            else:
                stripSent = strip_tags(sent, 'H')[0]
            writer.write(stripSent + '\n')


def create_txt(data):
    """
    Data input: parsed text to xml
    Output: String the text without tags
    """
    updated_text = ''
    for sent in data:
        if sent.startswith('<S'):
            stripSent = strip_tags(sent, 'S')
        elif sent.startswith('<OneItem'):
            stripSent = strip_tags(sent, 'OneItem')
        else:
            stripSent = strip_tags(sent, 'H')[0]
        updated_text = updated_text + stripSent + ' '
    return updated_text


# ============= Restructure Functions ==========================================

# region ==== Section Processing ====
def init_section_structure():
    sections = {
        0: 'other',
        1: 'chairmans statement',
        2: 'chief executive officer ceo review',
        3: 'chief executive officer ceo report',
        4: 'governance statement',
        5: 'remuneration report',
        6: 'business review',
        7: 'financial review',
        8: 'operating review',
        9: 'highlights',
        10: 'auditors report',
        11: 'risk management',
        12: 'chairmans governance introduction',
        13: 'Corporate Social Responsibility CSR disclosures'
    }
    return sections


def check_if_section(test_string, threshold=0.4):
    section_types = init_section_structure()  # TODO: initialize the variable once (memory consumption)
    ans = [0] * len(section_types)
    for _ in range(len(section_types)):
        ans[_] = get_jaccard_sim(test_string, section_types[_])
    max_value = max(ans)
    if max_value > threshold:
        print('Test string: {0} | Section type: {1}'.format(test_string, section_types[ans.index(max_value)]))
        # return True
        return ans.index(max_value)
    else:
        return False
# endregion


def fix_missing_sentences(processed_text):
    """ Recursive function - depth problem"""
    index_for_del = list()
    for index in range(len(processed_text)):
        if not processed_text[index]:
            index_for_del.append(index)  # Record indexes that now empty after merge
            continue
        if processed_text[index][0] != '<S>':
            continue
        if index + 1 < len(processed_text) - 1:
            if processed_text[index][0] == '<S>' and processed_text[index + 1][0] != '<S>' and processed_text[index + 1][-1] == '</S>':
                processed_text[index].pop(-1)  # Removes the current </S> tag
                processed_text[index] = processed_text[index] + processed_text[index + 1]
                processed_text[index + 1].clear()
    if not index_for_del:
        processed_text = merge_sentences(processed_text)
        return processed_text
    for index in sorted(index_for_del, reverse=True):  # Delete all the indexes that now empty in reverse
        del processed_text[index]
    return fix_missing_sentences(processed_text)


def fix_missing_sentences_loop(processed_text):
    processed_text, index = fix_missing_sentences_v2(processed_text)
    while index:
        processed_text, index = fix_missing_sentences_v2(processed_text)
    processed_text = merge_sentences(processed_text)
    return processed_text


def fix_missing_sentences_v2(processed_text):
    """ Non recursive function"""
    index_for_del = list()
    for index in range(len(processed_text)):
        if not processed_text[index]:
            index_for_del.append(index)  # Record indexes that now empty after merge
            continue
        if processed_text[index][0] != '<S>':
            continue
        if index + 1 < len(processed_text) - 1:
            if processed_text[index][0] == '<S>' and processed_text[index + 1][0] != '<S>' and processed_text[index + 1][-1] == '</S>':
                processed_text[index].pop(-1)  # Removes the current </S> tag
                processed_text[index] = processed_text[index] + processed_text[index + 1]
                processed_text[index + 1].clear()
    # if not index_for_del:
    #     processed_text = merge_sentences(processed_text)
    #     return processed_text
    for index in sorted(index_for_del, reverse=True):  # Delete all the indexes that now empty in reverse
        del processed_text[index]
    return processed_text, index_for_del


def merge_sentences(text):
    for sentNo in range(len(text)):
        text[sentNo] = ' '.join(text[sentNo])
    return text


def check_if_header(item):
    first_upper_letter_words_flag = True
    first_upper_letter_words_counter = 0
    item_split = item.split()  # Split the sentence by white space
    if len(item_split) == 1 and item_split[0].isnumeric():  # Checks if item is just number ex: '10'
        first_upper_letter_words_flag = False
        return 'Number'
    for word in item_split:
        if not word[0].isupper() and not word[0].isnumeric():  # Check for each word in item if first char is not upper and not numeric
            first_upper_letter_words_flag = False
        elif not word[0].isnumeric():  # Ignore words with numbers
            first_upper_letter_words_counter += 1
    if (first_upper_letter_words_counter != 0 and first_upper_letter_words_counter / len(item_split) <= 0.5) or first_upper_letter_words_counter == 0:  # Checks the Ratio between upper words and the length of the sentence
        first_upper_letter_words_flag = False
    else:
        first_upper_letter_words_flag = True
        if len(item_split) == 1:
            return 'OneItem'
    # Jaccard similarity
    if first_upper_letter_words_flag is True:
        return check_if_section(item)
    else:
        return first_upper_letter_words_flag  # Returns False


def remove_bad_sentences(processed_text):
    index_for_del = list()
    for index in range(len(processed_text)):
        if processed_text[index].endswith('</S>') and not processed_text[index].startswith('<S>'):
            index_for_del.append(index)
    if not index_for_del:
        return processed_text
    for index in sorted(index_for_del, reverse=True):  # Delete all the indexes that now empty in reverse
        del processed_text[index]
    return remove_bad_sentences(processed_text)


def re_structure_text(originalText):
    regex_rules = import_regex()
    print(originalText)
    originalText = re.sub('&', 'and', originalText)  # Convert & to 'and'
    # originalText = re.sub(regex_rules[0], 'site', originalText)
    originalText = loop_regex_rules(originalText, regex_rules)
    originalText = re.sub('\.{2,}', ' ', originalText)
    originalText = re.sub('\.[^0-9]', '\.\n', originalText)
    originalText = re.sub('[^a-zA-Z0-9\s\.%]', '', originalText.strip())  # Remove all non a-z 0-9 \s . symbols
    lines_text = originalText.split('\n')
    lines_text = correct_after_split(lines_text, regex_rules)

    started_sentence_flag = False
    text = list()
    current_sentence = list()
    for line in lines_text:
        if line == '':
            continue
        line = line.strip()
        if len(line) == 0:
            continue
        isHeader = check_if_header(line)
        # if not isHeader or isHeader == 'OneItem':
        if not isHeader:
            if (line[0].isupper() or line[0].isnumeric()) and started_sentence_flag is False:
                current_sentence.append('<S>')
                current_sentence.append(line)
                started_sentence_flag = True
                if line.endswith('.'):
                    current_sentence.append('</S>')
                    text.append(copy.deepcopy(current_sentence))
                    current_sentence.clear()
                    started_sentence_flag = False
            elif started_sentence_flag and not line.endswith('.'):
                current_sentence.append(line)
            # If the first sentence in the text starts with lower and the text is empty.
            # Check if text is empty + check if line ends with .
            # If true -> add whole sentence with tags | Else -> start sentence and find the next dot .
            elif started_sentence_flag is False and not text:
                if line.endswith('.'):
                    current_sentence.append('<S>')
                    current_sentence.append(line)
                    current_sentence.append('</S>')
                    text.append(copy.deepcopy(current_sentence))
                    current_sentence.clear()
                else:
                    current_sentence.append('<S>')
                    current_sentence.append(line)
                    started_sentence_flag = True
            elif started_sentence_flag is False and len(text[-1]) == 1 and text[-1][0].startswith('<OneItem>') and not line[0].isupper() and len(current_sentence) == 0:
                try:
                    reduced_OneItem = text[-1][0].strip('<OneItem>')[:-2]
                    isUpper = reduced_OneItem[0].isupper()
                except IndexError:
                    # For some reason strip not working properly ex: <OneItem>In</OneItem> reduced to / when using strip
                    # To Solve this problem catches the exception and using two times the replace function for removal
                    reduced_OneItem = text[-1][0].replace('<OneItem>', '').replace('</OneItem>', '')
                    isUpper = reduced_OneItem[0].isupper()
                if isUpper is True:
                    current_sentence.append('<S>')
                    current_sentence.append(reduced_OneItem)
                    text.pop(len(text) - 1)
                    started_sentence_flag = True
                    if line.endswith('.'):
                        current_sentence.append(line)
                        current_sentence.append('</S>')
                        started_sentence_flag = False
                        text.append(copy.deepcopy(current_sentence))
                        current_sentence.clear()
                    else:
                        current_sentence.append(line)
            elif line.endswith('.'):
                current_sentence.append(line)
                current_sentence.append('</S>')
                text.append(copy.deepcopy(current_sentence))
                current_sentence.clear()
                started_sentence_flag = False
        elif isHeader == 'OneItem' and started_sentence_flag is False:
            current_sentence.append('<OneItem>' + line + '</OneItem>')
            text.append(copy.deepcopy(current_sentence))
            current_sentence.clear()
        elif isHeader == 'Number':
            pass
        elif isHeader:
            if started_sentence_flag is True:
                current_sentence.append('</S>')
                text.append(copy.deepcopy(current_sentence))
                current_sentence.clear()
                started_sentence_flag = False
            if isinstance(isHeader, int):
                current_sentence.append('<H-'+str(isHeader)+'>' + line + '</H-'+str(isHeader)+'>')
                text.append(copy.deepcopy(current_sentence))
                current_sentence.clear()
    text = fix_missing_sentences_loop(text)
    text = remove_bad_sentences(text)
    return text


def word_number_ratio(sent, threshold=0.4, spaces_threshold=0.5):
    # sent = sent.replace(' ', '')
    if not sent or len(sent) == 1:
        return False
    spaces = sum(c.isspace() for c in sent)
    spaces_ratio = spaces / float(len(sent))
    if spaces_ratio > spaces_threshold:
        return False
    numbers = sum(c.isdigit() for c in sent)
    words = sum(c.isalpha() for c in sent)
    ratio = words / float(numbers + words)
    if ratio < threshold:
        return False
    else:
        return True


def loop_regex_rules(text, regex_rules):
    # text = re.sub(regex_rules[7], 'date', text)  # Date
    # text = re.sub(regex_rules[8], 'date', text)  # Date
    # text = re.sub(regex_rules[9], 'time', text)  # Time
    # text = re.sub(regex_rules[10], 'time', text)  # Time
    text = text.replace('\t', '')
    text = re.sub(regex_rules[2], 'tel', text)  # Telephone
    text = re.sub(regex_rules[3], 'tel', text)  # Telephone
    text = re.sub(regex_rules[4], 'tel', text)  # Telephone
    text = re.sub(regex_rules[5], 'tel', text)  # Telephone
    text = re.sub(regex_rules[6], 'tel', text)  # Telephone
    text = re.sub(regex_rules[0], 'site', text)  # Site
    text = re.sub(regex_rules[1], 'email', text)  # Email
    for subIndex in range(11, 16):  # Long numbers
        text = re.sub(regex_rules[subIndex], '', text)

    return text

def correct_after_split(text, regex_rules):
    index_to_remove = list()
    for line_number in range(len(text)):
        text[line_number] = text[line_number].strip()
        test_var = text[line_number].lower()
        test_var = re.sub(r'[0-9]{4}', 'date', test_var)
        if 'date' in test_var and word_number_ratio(test_var) is True:
            continue
        if text[line_number].endswith('.') and text[line_number].replace('.', '').isdigit() is True:
            index_to_remove.append(line_number)
        elif word_number_ratio(text[line_number]) is False and '%' not in text[line_number]:
            test_var = re.sub(regex_rules[7], 'date', test_var)
            test_var = re.sub(regex_rules[8], 'date', test_var)
            test_var = re.sub(regex_rules[16], 'date', test_var)
            if 'date' in test_var and word_number_ratio(test_var) is True:
                continue
            index_to_remove.append(line_number)
        elif text[line_number] == '.':
            index_to_remove.append(line_number)
        elif not len(text[line_number]):
            index_to_remove.append(line_number)
        elif text[line_number].isdigit():
            index_to_remove.append(line_number)
        else:
            test_var = text[line_number]
            test_var = re.sub(regex_rules[7], 'date', test_var.lower())
            test_var = re.sub(regex_rules[8], 'date', test_var.lower())
            test_var = re.sub(regex_rules[16], 'date', test_var.lower())
            if test_var == 'date':
                index_to_remove.append(line_number)
    for i in reversed(index_to_remove):
        del text[i]
    return text
