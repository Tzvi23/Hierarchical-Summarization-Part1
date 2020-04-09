import json
import copy
import csv
import os
import pprint
import re
import gensim
from print_colors import bcolors
from Classes.base_class import Position
from Classes.node_class import node
from Classes.leaf_class import leaf
from Classes.unit_class import unit, find_max
from Classes.unit_class import unit_connector
from Classes.unit_class import one_leaf_unit
from Classes.graph_classes.graph_node import node_graph, nodeEncoder
import sent_rank as sr

score_data = list()  # declaration for global

def create_model_dict(model):
    model_dict = dict()
    model_data = model.print_topics()
    print(model_data)
    for t in model_data:
        model_dict[t[0]] = ' | '.join([item.strip()[6:] for item in t[1].replace('"', '').split('+')[0:4]])
    return model_dict
# Load models
topic_labels = dict()
topic4 = gensim.models.ldamodel.LdaModel.load('/home/tzvi/PycharmProjects/HSdataprocessLinux/gensim_models/4topics/lda_model_trained_4topics.model')
topic4 = create_model_dict(topic4)
topic_labels['4'] = topic4
topic6 = gensim.models.ldamodel.LdaModel.load('/home/tzvi/PycharmProjects/HSdataprocessLinux/gensim_models/6topics/lda_model_trained_6topics.model')
topic6 = create_model_dict(topic6)
topic_labels['6'] = topic6
topic10 = gensim.models.ldamodel.LdaModel.load('/home/tzvi/PycharmProjects/HSdataprocessLinux/gensim_models/10topics/lda_model_trained_10topics.model')
topic10 = create_model_dict(topic10)
topic_labels['10'] = topic10

pp = pprint.PrettyPrinter()

# region <------------------------------ Base tree struct functions --------------------------------------------->
def convert_to_tree_object(json_output, tree, node_filter=None):
    if 'root' in json_output['name'].lower():
        tree.text_description = json_output['name']
        tree.node_class = 'root'
        tree.parent = 'root'
        tree.rel2par = 'root'
        tree.set_depth(0)
    if len(json_output) == 1:  # leaf
        global score_data
        content = json_output['name']
        tree.text_description = content
        content = content.split('|')
        content_text = content[1][6:].strip()  # Leaf text
        tree.text = content_text
        node_type = content[0].strip().split()[0].split('ENDNODENUM')[1].lower()  # nucleus / satellite
        if node_type == 'nucleus':
            node_type = 'N'
        else:
            node_type = 'S'
        tree.node_class = node_type
        tree.topic_class = int(content[2].strip()[7:])  # int number of topic
        content_split = content[0].strip().replace('(', '').replace(')', '').split()
        tree.rel2par = content_split[4]
        tree.node_number_L = int(content_split[2])
        tree.score = sr.get_score(score_data, content_text)
        if node_filter is None:
            return tree
        elif node_filter == node_type:
            return tree
        else:
            return tree
    else:
        # <-- Children -->
        # ## RIGHT CHILD ##
        if len(json_output['children'][0]) > 1:
            tree.right_child = node(json_output['children'][0]['name'])
            tree.right_child.parent = tree
            tree.right_child.set_depth(tree.tree_depth + 1)
        else:
            tree.right_child = leaf()
            tree.right_child.set_position(Position.right)
            tree.right_child.parent = tree
            tree.right_child.set_depth(tree.tree_depth + 1)
        convert_to_tree_object(json_output['children'][0], tree.right_child, node_filter)
        # ## LEFT CHILD ##
        if len(json_output['children']) > 1:
            if len(json_output['children'][1]) > 1:
                tree.left_child = node(json_output['children'][1]['name'])
                tree.left_child.parent = tree
                tree.left_child.set_depth(tree.tree_depth + 1)
            else:
                tree.left_child = leaf()
                tree.left_child.set_position(Position.left)
                tree.left_child.parent = tree
                tree.left_child.set_depth(tree.tree_depth + 1)
            convert_to_tree_object(json_output['children'][1], tree.left_child, node_filter)
    return tree


def find_node_id(tree_root, node_l, node_r=0, found_node=None):
    """
    Returns the node and leaf object of enter node_l & node_r (ints) id.
    If not found returns None
    """
    if tree_root.node_number_L == node_l and tree_root.node_number_R == node_r:
        found_node = tree_root
        return found_node
    if isinstance(tree_root, node) and tree_root.right_child is not None:
        found_node = find_node_id(tree_root.right_child, node_l, node_r, found_node)
    if isinstance(tree_root, node) and tree_root.left_child is not None:
        found_node = find_node_id(tree_root.left_child, node_l, node_r, found_node)
    return found_node


def top_leaf(tree_root):
    return find_node_id(tree_root, 1)


def update_tree_data(tree_root):
    """
    Updates all the nodes with complexity, Is complex, tree_depth data
    """
    if isinstance(tree_root, leaf):
        return
    tree_root.set_IsComplex()
    tree_root.set_complexity()
    tree_root.set_depth_complex()
    if tree_root.right_child is not None:
        update_tree_data(tree_root.right_child)
    if tree_root.left_child is not None:
        update_tree_data(tree_root.left_child)
    return


def update_tree_complex_status(tree_root):
    """
    Updates all the nodes with complexity, Is complex, tree_depth data
    """
    if isinstance(tree_root, leaf):
        return
    tree_root.update_IsComplex()
    if tree_root.right_child is not None:
        update_tree_complex_status(tree_root.right_child)
    if tree_root.left_child is not None:
        update_tree_complex_status(tree_root.left_child)
    return

# endregion

# region <------------------------------ Unit functions ---------------------------------------------------->
def find_first_unit_node(base_node):
    """
        *L*
       /
    *N*     *L*
       \   /
     -->*N*<--
           \
            *L*
    :param base_node: base node
    :return:
    """
    if isinstance(base_node, node) and isinstance(base_node.right_child, leaf) and isinstance(base_node.left_child, leaf):
        return base_node
    if base_node.right_child is not None and isinstance(base_node.right_child, node):
        base_node = find_first_unit_node(base_node.right_child)
    if base_node.left_child is not None and isinstance(base_node.left_child, node):
        base_node = find_first_unit_node(base_node.left_child)
    return base_node


def create_one_leaf_unit(leaf_node):
    new_unit = one_leaf_unit()
    new_unit.set_unit_size(1)
    new_unit.set_unit_top_node(leaf_node)
    new_unit.update_leafs()
    new_unit.decide_topic()
    new_unit.update_pure_text()
    return new_unit


def create_unit(base_node, new_unit, previous_node, dest_node):
    if base_node is dest_node:
        return new_unit
    if base_node.left_child is previous_node or base_node.left_child is previous_node:
        new_unit.add_new_node(base_node.right_child)
        create_unit(base_node.parent, new_unit, base_node, dest_node)
        return new_unit
    # new_unit = unit()
    new_unit.set_unit_top_node(base_node)
    new_unit.set_unit_size(base_node.get_complexity() + 1)  # +1 to include the base node
    new_unit.update_leafs()
    new_unit.decide_topic()
    new_unit.update_pure_text()
    if base_node.parent is not None:
        create_unit(base_node.parent, new_unit, base_node, dest_node)
    new_unit.update_n_tuples()
    return new_unit


def create_unit_tree(unit_node, tree, rl=None):
    if tree.isComplex is False:
        new_unit = unit()
        first_node = find_first_unit_node(tree)
        if rl == 'r':
            unit_node.set_right_child(create_unit(first_node, new_unit, tree, tree.parent))
        elif rl == 'l':
            unit_node.set_left_child(create_unit(first_node, new_unit, tree, tree.parent))
        return
    new_unit_connector = unit_connector()
    if tree.right_child is not None:
        if isinstance(tree.right_child, leaf):
            unit_node.set_right_child(create_one_leaf_unit(tree.right_child))
        elif tree.right_child.isComplex is True:
            new_unit_connector.set_node(tree.right_child)
            unit_node.right_child = new_unit_connector
            create_unit_tree(unit_node.right_child, tree.right_child)
        else:  # Tree node is not complex
            create_unit_tree(unit_node, tree.right_child, 'r')
    if tree.left_child is not None:
        if isinstance(tree.left_child, leaf):
            unit_node.set_left_child(create_one_leaf_unit(tree.left_child))
        elif isinstance(tree.left_child, node) and tree.left_child.isComplex is True:
            if tree.node_class == 'root':
                new_unit_connector = unit_connector()
            new_unit_connector = unit_connector()
            new_unit_connector.set_node(tree.left_child)
            unit_node.left_child = new_unit_connector
            create_unit_tree(unit_node.left_child, tree.left_child)
        else:  # Tree node is not complex
            create_unit_tree(unit_node, tree.left_child, 'l')
            return
    return


topic_stats = dict()
def write_topic_stats(unit_node):
    global topic_stats
    if isinstance(unit_node, unit) or isinstance(unit_node, one_leaf_unit):
        if unit_node.unit_topic not in topic_stats:
            topic_stats[unit_node.unit_topic] = 1
        else:
            topic_stats[unit_node.unit_topic] += 1
        return
    write_topic_stats(unit_node.right_child)
    write_topic_stats(unit_node.left_child)
    return


def get_text(unit_node, topic_number, mode='A', text=''):
    if isinstance(unit_node, unit) or isinstance(unit_node, one_leaf_unit):
        if unit_node.unit_topic == topic_number:
            if mode == 'A':
                text += unit_node.pure_text
            elif mode == 'N':
                text += unit_node.nucleus_pure_text
            elif mode == 'SN':
                if unit_node.short_nucleus_text == '':
                    text += ''
                else:
                    text += unit_node.short_nucleus_text
        return text
    text = get_text(unit_node.right_child, topic_number, mode, text)
    text = get_text(unit_node.left_child, topic_number, mode, text)
    return text


def get_n_tuples(unit_node, topic_number, tuple_list):
    if isinstance(unit_node, unit) or isinstance(unit_node, one_leaf_unit):
        if unit_node.unit_topic == topic_number and len(unit_node.nucleus_tuples):
            tuple_list.extend(unit_node.nucleus_tuples)
        return tuple_list
    tuple_list = get_n_tuples(unit_node.right_child, topic_number, tuple_list)
    tuple_list = get_n_tuples(unit_node.left_child, topic_number, tuple_list)
    return tuple_list
# endregion

# region <------------------------------ Small tree functions --------------------------------------------->
def small_tree(tree_node):
    def traverse_tree(treeNode, sentences):
        """
        Recursive functions that deals with simple small tree struct that dont require units.
        This function goes over the tree and creates the following sentences list:
        item1: (text, N/S, topic number)
        """
        if isinstance(treeNode, leaf):
            sentences.append((treeNode.text, treeNode.node_class, treeNode.topic_class))
            return
        if tree_node.right_child is not None:
            traverse_tree(treeNode.right_child, sentences)
        if tree_node.left_child is not None:
            traverse_tree(treeNode.left_child, sentences)
        return

    def topics(s_list):
        """
        Finds the topic numbers in the specific tree and returns the max
        nucleus topic number.
        """
        n_topic = dict()
        s_topic = dict()
        choose_dict = None  # declaration
        for line in s_list:
            if line[1] == 'N':
                choose_dict = n_topic
            elif line[1] == 'S':
                choose_dict = s_topic
            if line[2] not in choose_dict:
                choose_dict[line[2]] = 1
            else:
                choose_dict[line[2]] += 1
        if len(n_topic):
            topic_max = max(n_topic.values())
            topic_number = find_max(n_topic, topic_max)
        else:
            topic_max = max(s_topic.values())
            topic_number = find_max(s_topic, topic_max)
        return topic_number

    def get_small_text(s_list, nucleus_flag=False):
        text = ''
        for line in s_list:
            if nucleus_flag is True and line[1] == 'N':
                text += line[0]
            else:
                text += line[0]
        return text

    sent_list = list()
    traverse_tree(tree_node, sent_list)
    topic_number = topics(sent_list)
    print('Topic class: ' + str(topic_number))
    c_text = get_small_text(sent_list, nucleus_flag=False)
    pp.pprint(c_text)
    return topic_number, c_text

# endregion

def write_data_csv(unit_root, topics, filename, dest_dir, complex_struct=True):
    filename = filename.split(os.path.sep)[-1][:-10] + '_processed.csv'
    filename = os.path.join(dest_dir, filename)
    fieldnames = ['topic_number', 'Text', 'Nucleus_text', 'Short_nucleus']
    writer_dict = dict()  # declaration
    with open(filename, mode='w') as proc_file:
        writer = csv.DictWriter(proc_file, fieldnames=fieldnames)
        writer.writeheader()
        if complex_struct is True:
            """ Complex tree writer """
            for topic_number in topics.keys():
                writer_dict.clear()
                writer_dict[fieldnames[0]] = topic_number
                writer_dict[fieldnames[1]] = get_text(unit_root, topic_number, mode='A')
                writer_dict[fieldnames[2]] = get_text(unit_root, topic_number, mode='N')
                n_tuples = list()
                get_n_tuples(unit_root, topic_number, n_tuples)
                n_tuples = sr.shorten_text2(n_tuples, 20, 0.5, topic_number)  # Short text function with two parameters
                if n_tuples is not None:
                    writer_dict[fieldnames[3]] = '\n'.join([item[1] for item in n_tuples])
                else:
                    writer_dict[fieldnames[3]] = ''
                writer.writerow(writer_dict)
        elif complex_struct is False:
            """ Simple tree writer """
            for topic_number in topics.keys():
                writer_dict.clear()
                writer_dict[fieldnames[0]] = topic_number
                writer_dict[fieldnames[1]] = topics[topic_number]
                writer_dict[fieldnames[2]] = 'Simple tree'
                writer.writerow(writer_dict)

def process_topic_file(file_path, dest_dir):
    print(bcolors.HEADER + 'Processing: {0}'.format(file_path) + bcolors.ENDC)
    # Read json file after topic classification
    parsed_json = json.loads(open(file_path, 'r').read())
    print(parsed_json)
    # Convert json to tree object structure
    root = node()
    root = convert_to_tree_object(parsed_json, root)
    update_tree_data(root)
    update_tree_complex_status(root)
    # test_node = find_node_id(root, 1, 3)

    if root.isComplex is False:
        """
        If the tree being processed is too small and cant create units
        """
        simple_tree_topic_number, simple_tree_text = small_tree(root)
        topic_stats.clear()
        topic_stats[simple_tree_topic_number] = simple_tree_text
        write_data_csv(None, topic_stats, file_path, dest_dir, complex_struct=False)
    else:
        # Create secondary tree structure of units connected
        unit_root = unit_connector(copy.deepcopy(root))
        create_unit_tree(unit_root, root)
        topic_stats.clear()
        write_topic_stats(unit_root)  # Update dictionary with which unit topics and how many
        # print('All text')
        # pp.pprint(get_text(unit_root, 0))
        # print('All nucleus')
        # pp.pprint(get_text(unit_root, 0, nucleus_flag=True))
        # print()
        # Write results to csv file
        write_data_csv(unit_root, topic_stats, file_path, dest_dir, complex_struct=True)


def loop_topic_data(fileID=None, model_number=None, dir_path='output/topic_class', dest_dir='output/final_stage'):
    global score_data
    if not os.path.exists(dest_dir):
        os.mkdir(dest_dir)
    # r=root, d=directories, f = files
    for r, d, f in os.walk(dir_path, topdown=True):
        if r.split(os.path.sep)[-1] == 'topic_class':
            continue
        if (model_number is not None and r.split(os.path.sep)[-1] == model_number) or (model_number is None):
            current_model = r.split(os.path.sep)[-1]
            output_dir_path = os.path.join(dest_dir, r.split(os.path.sep)[-1])
            if not os.path.exists(output_dir_path):
                os.mkdir(output_dir_path)
            print(r)
            if current_model == 'textData':
                continue
            for file in f:
                file_id = file.split('_')[0]
                if (fileID is not None and file.split('_')[0] == str(fileID)) or (fileID is None):
                    file_path_dir = os.path.join(output_dir_path, file_id)
                    if not os.path.exists(file_path_dir):
                        os.mkdir(file_path_dir)
                    print(os.path.join(r, file))
                    score_data = sr.load_data(file[:-10] + '.txt', current_model)
                    process_topic_file(os.path.join(r, file), file_path_dir)
                    create_json_repr(file_id, file_path_dir, r.split(os.path.sep)[-1])


def create_json_repr(file_id, data_dir, model_number):
    root = node_graph(file_id)
    for section in os.listdir(data_dir):
        section_name = re.sub('[0-9]', '', section[:-27]).replace('_', ' ').strip()
        print(section_name)
        section_node = node_graph(section_name, root.name, children=True)
        section_node.children = (read_processed_text(os.path.join(data_dir, section), section_name, model_number))
        root.add_children(section_node)

    with open(data_dir.replace('final_stage', 'final_stage_graph') + '.txt', mode='w') as graph_file:
        test_list = list()
        test_list.append(json.dumps(root, cls=nodeEncoder))
        test_list = str(test_list)
        graph_file.write(test_list.replace('\\\\n', '').replace('\'', ''))

def read_processed_text(file_path, parent_name, model_number):
    # TODO check if regular expression effects something
    children_list = list()
    with open(file_path, mode='r') as proc_file:
        csv_reader = csv.DictReader(proc_file)
        for row in csv_reader:
            print(row)
            topic_node = node_graph(row['topic_number'], parent_name, children=True)
            if model_number != '20':
                topic_node.name = topic_node.name + ' ' + topic_labels[model_number][int(topic_node.name)]
            # Text
            text_node = node_graph('Text', topic_node.name, children=True)
            text_str_node = node_graph(re.sub('[^a-zA-z0-9\s\.\\n]', '', pp.pformat(row['Text'])), text_node.name, children=False)
            text_node.add_children(text_str_node)
            topic_node.add_children(text_node)
            # Nucleus Text Nucleus_text
            nucleus_node = node_graph('Nucleus Text', topic_node.name, children=True)
            nucleus_str_node = node_graph(re.sub('[^a-zA-z0-9\s\.\\n]', '', pp.pformat(row['Nucleus_text'])), nucleus_node.parent, children=False)
            nucleus_node.add_children(nucleus_str_node)
            topic_node.add_children(nucleus_node)
            # Short Nucleus Text Nucleus_text
            if len(row) == 4 and row['Short_nucleus'] != '':
                nucleus_node = node_graph('Short nucleus', topic_node.name, children=True)
                nucleus_str_node = node_graph(re.sub('[^a-zA-z0-9\s\.]', '', pp.pformat(row['Short_nucleus'])),
                                              nucleus_node.parent, children=False)
                nucleus_node.add_children(nucleus_str_node)
                topic_node.add_children(nucleus_node)

            children_list.append(topic_node)
    return children_list
"""
file_path_topic = '/home/tzvi/PycharmProjects/HSdataprocessLinux/Classes/102_auditors_report_strip_output_topic.txt'
process_topic_file(file_path_topic)
"""

# process_topic_file('output/topic_class/10/5540_non_section_strip_output_topic.txt', '/home/tzvi/PycharmProjects/HSdataprocessLinux/output/final_stage/10')

# loop_topic_data()
