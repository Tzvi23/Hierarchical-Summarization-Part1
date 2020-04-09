import json
import os
import re

def run_show_case(fileId, modelNumber, **pathParams):
    class section_obj:
        def __init__(self, code, isTopic=False, status='0'):
            self.status = status
            self.code = str(code)
            self.isTopic = isTopic
            self.text = ''
            if self.isTopic is True:
                self.code = self.convert_to_topic_code()
            self.html_code = self.merge()

        def merge(self):
            return self.code + '_' + self.status

        def convert_to_topic_code(self):
            return '0' + self.code

        def set_text(self, text):
            self.text = text
            self.status = '1'

        def set_status(self, stat):
            self.status = stat

    sections_types = ['other', 'chairmans statement', 'chief executive officer ceo review', 'chief executive officer ceo report',
                      'governance statement',
                      'remuneration report',
                      'business review', 'financial review', 'operating review', 'highlights', 'auditors report',
                      'risk management', 'chairmans governance introduction',
                      'Corporate Social Responsibility CSR disclosures']

    # define variables to update
    params = dict()
    # Original text data - %original_text%
    params['%original_text%'] = 'original_text'
    # Xml processed text - %xml_processed_text%
    params['%xml_processed_text%'] = 'xml_processed_txt'

    # region Sections
    off = '0'
    on = '1'
    disabled = '3'

    # Create object for regular tree
    for index in range(len(sections_types)):
        key = '%' + sections_types[index].lower().replace(' ', '_') + '_text%'
        obj = section_obj(index)
        key_stat = '%' + obj.code + '%'
        params[key] = obj
        params[key_stat] = obj.merge()
    # Create object for  topic tree
    for index in range(len(sections_types)):
        key = '%' + sections_types[index].lower().replace(' ', '_') + '_text_topic%'
        obj = section_obj(index, isTopic=True)
        key_stat = '%' + obj.code + '%'
        params[key] = obj
        params[key_stat] = obj.merge()
    # endregion

    # Final stage - %final_stage_result%
    final_stage_text = '\'\''
    params['%final_stage_result%'] = final_stage_text

    # region dir paths
    original_text_dir = pathParams['original_text_dir']
    xml_processed_dir = pathParams['xml_processed_dir']
    xml_parse_dir = pathParams['xml_parse_dir']
    topic_class_dir = pathParams['topic_class_dir']
    trees_dir = pathParams['trees_dir']
    final_stage_dir = pathParams['final_stage_dir']
    # endregion

    def load_data(file_id, model_number):
        def load_original_text(file_name, dir_path=original_text_dir):
            with open(os.path.join(dir_path, str(file_name) + '.txt'), mode='r') as file:
                nonlocal params
                params['%original_text%'] = file.read()

        def load_xml_processed(file_name, dir_path=xml_processed_dir):
            with open(os.path.join(dir_path, str(file_name) + '.txt'), mode='r') as file:
                nonlocal params
                params['%xml_processed_text%'] = file.read()

        def load_sections_data(file_name, model, dir_path=topic_class_dir):
            path = os.path.join(dir_path, str(model))
            for files in os.listdir(path):
                print(files)
                if files == 'textData':
                    continue
                cur_id = int(files[:-23].split('_')[0])
                if file_name == cur_id:
                    section_name = '%' + re.sub('[^a-zA-z_]', '', files[:-23]).strip()[1:] + '_text_topic%'
                    if section_name == '%non_section_text_topic%':
                        section_name = '%other_text_topic%'
                    with open(os.path.join(path, files), mode='r') as cur_file:
                        text = cur_file.read()
                        params[section_name].set_text(text)
                        params['%' + params[section_name].code + '%'] = params[section_name].merge()

        def load_tree_data(file_name, dir_path=trees_dir):
            for files in os.listdir(dir_path):
                path = os.path.join(dir_path, files)
                if os.path.isdir(path):
                    continue
                print(files)
                cur_id = int(files.split('_')[0])
                if file_name == cur_id:
                    # Process the file name
                    if 'strip_output' in files and ('FAILED_PARSE' in files or 'FAILED_SEG' in files):
                        if 'FAILED_PARSE' in files:
                            adjust = -30
                        else:
                            adjust = -28
                        section_name = '%' + re.sub('[^a-zA-z_]', '', files[:adjust]).strip()[1:] + '_text%'

                        params[section_name].set_status(disabled)
                        params['%' + params[section_name].code + '%'] = params[section_name].merge()

                    elif 'strip_output' in files:
                        section_name = '%' + re.sub('[^a-zA-z_]', '', files[:-17]).strip()[1:] + '_text%'
                        if section_name == '%non_section_text%':
                            section_name = '%other_text%'

                        with open(os.path.join(dir_path, files), mode='r') as cur_file:
                            text = cur_file.read()
                            params[section_name].set_text(text)
                            params['%' + params[section_name].code + '%'] = params[section_name].merge()

        def load_final_stage_data(file_name, model, dir_path=final_stage_dir):
            path = os.path.join(dir_path, str(model))
            for files in os.listdir(path):
                print(files)
                if file_name == int(files[:-4]):
                    with open(os.path.join(path, files), mode='r') as cur_file:
                        text = cur_file.read()
                        write_final_stage_file(json.loads(text), file_name, model, mode='text')
                        write_final_stage_file(json.loads(text), file_name, model, mode='nucleus')
                        params['%final_stage_result%'] = text

        load_tree_data(file_id)
        load_original_text(file_id)
        load_xml_processed(file_id)
        load_sections_data(file_id, model_number)
        load_final_stage_data(file_id, model_number)

    def write_final_stage_file(json_dict, filename, model, mode='all'):
        cur_dir = os.path.join(os.path.join(os.path.join(os.path.join(os.getcwd(), 'show_case'), 'final_report'), str(model)), mode)
        if not os.path.exists(cur_dir):
            os.mkdir(cur_dir)
        filename = str(filename) + '_' + mode + '.txt'
        text = ''
        root = json_dict[0]['children']
        for section in root:
            text += section['name'] + '\n'
            for topic in section['children']:
                text += 'Topic: ' + topic['name'] + '\n'
                if mode == 'all':
                    text += topic['children'][0]['children'][0]['name'] + '\n'  # All the text
                    text += '<--- Nucleus Text ---> \n'
                    text += topic['children'][1]['children'][0]['name'] + '\n'  # All the text
                elif mode == 'nucleus':
                    text += topic['children'][1]['children'][0]['name'] + '\n'  # All the text
                elif mode == 'text':
                    text += topic['children'][0]['children'][0]['name'] + '\n'  # All the text
                text += '\n'
            text += '\n'
        with open(os.path.join(cur_dir, filename), mode='w') as output_file:
            output_file.write(text)

    filename_id = fileId
    model_number = modelNumber
    load_data(filename_id, model_number)

    with open(os.path.join(os.path.join(os.getcwd(), 'show_case'), 'show_case_template.html'), mode='r') as show_case:
        html_data = show_case.read()

        for key in params.keys():
            print(key, params[key])
            if isinstance(params[key], str):
                html_data = html_data.replace(key, params[key])
            else:
                html_data = html_data.replace(key, params[key].text)
    with open(os.path.join(os.path.join(os.getcwd(), 'show_case'), 'show_case_' + str(filename_id) + '_' + str(model_number) + '.html'), mode='w') as show_case:
        show_case.write(html_data)
        return os.path.join(os.path.join(os.getcwd(), 'show_case'), 'show_case_' + str(filename_id) + '_' + str(model_number) + '.html')
