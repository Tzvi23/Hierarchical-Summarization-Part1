import copy
import math
import os
import pickle
from Classes.leaf_class import leaf

unit_counter = 0
file_name = ' '


def find_max(c_dict, value):
    for k, v in c_dict.items():
        if v == value:
            return k


class unit:
    def __init__(self, u_size=None, u_topic=None, u_top_node=None):
        global unit_counter
        unit_counter += 1
        # Unit info
        self.unit_id = unit_counter
        self.unit_size = u_size
        self.unit_topic = u_topic
        self.unit_topic_score = 0
        self.unit_topic_vector = list()
        self.unit_top_node = u_top_node
        self.unit_tree_depth = 0
        # Unit data
        self.leaf_nodes = dict()  # Contains all the leaf nodes
        # Unit text
        self.text = list()  # Pure text representation of the unit
        self.nucleus_text = list()
        self.pure_text = ''
        self.nucleus_pure_text = ''
        # sentence rank
        self.short_nucleus_text = ''
        self.nucleus_tuples = list()

    # Functions
    def update_leafs(self):
        """
        Adds the leafs object to unit dict -> leaf_nodes
        ** Not recursive **
        """
        if self.unit_top_node.right_child is not None and isinstance(self.unit_top_node.right_child, leaf):
            self.leaf_nodes[self.unit_top_node.right_child.get_L_node_number()] = self.unit_top_node.right_child
            self.update_unit_tree_depth(self.unit_top_node.right_child.tree_depth)
        if self.unit_top_node.left_child is not None and isinstance(self.unit_top_node.left_child, leaf):
            self.leaf_nodes[self.unit_top_node.left_child.get_L_node_number()] = self.unit_top_node.left_child
            self.update_unit_tree_depth(self.unit_top_node.left_child.tree_depth)
        self.update_text()

    def update_text(self):
        """
        Updates the text in the leaf order in the leafs units dict
        """
        self.text.clear()
        self.nucleus_text.clear()
        if len(self.leaf_nodes):
            for k, v in sorted(self.leaf_nodes.items(), key=lambda item: item[0]):
                self.text.append(v.text)
                if v.node_class == 'N':
                    self.nucleus_text.append(v.text)

    def decide_topic(self):  # TODO: need to refine conditions
        """
        Decides the unit overall topic number
        """
        nucleus_weight = 1
        satellite_weight = 0.6

        choose_dict = None  # declaration
        N_topic = dict()
        S_topic = dict()
        if len(self.leaf_nodes):
            for leaf_node in self.leaf_nodes.values():
                leaf_factor = self.unit_tree_depth - leaf_node.tree_depth + 1 + leaf_node.position.value  # factor the height of the leaf in the tree and position
                if leaf_node.node_class == 'N':
                    leaf_factor += nucleus_weight  # Nucleus has more weight | was 0.5
                    choose_dict = N_topic
                elif leaf_node.node_class == 'S':
                    leaf_factor *= satellite_weight
                    choose_dict = S_topic
                if leaf_node.topic_class not in choose_dict:
                    choose_dict[leaf_node.topic_class] = 1 * leaf_factor
                else:
                    choose_dict[leaf_node.topic_class] += (1 * leaf_factor)
            total_topic = {**N_topic, **S_topic}  # Merge the Nucleus and Satellite dictionaries
            N_max = max(N_topic.values())
            N_max = find_max(N_topic, N_max)
            if len(S_topic):
                S_max = max(S_topic.values())
                S_max = find_max(S_topic, S_max)

            self.unit_topic = N_max

    def decide_topic_2(self, tree_height, mode='V'):
        """
        Decides the unit overall topic number
        Mode:
            NS - Nucleus Importance maximum approach
            V - vector approach mode
        """

        def mul_vector(val, vector):
            return [(item[0], val * item[1]) for item in vector]

        unit_topics = dict()
        # Weights
        W_HEIGHT = 0.5
        W_POSITION = 0.3
        W_NS = 0.2
        if len(self.leaf_nodes):
            for leaf_node in self.leaf_nodes.values():
                # F1 - height
                F1 = (tree_height + 1 - leaf_node.tree_depth) / (tree_height + 1)
                # F2 - position
                F2 = 1 if leaf_node.position.right else 0
                # F3 - nucleus / satellite
                F3 = 1 if leaf_node.node_class == 'N' else 0
                # NS
                NS = W_HEIGHT * F1 + W_POSITION * F2 + W_NS * F3
                leaf_node.ni_score = NS
                if mode is 'V':
                    self.unit_topic_vector = mul_vector(NS, self.unit_topic_vector if len(
                        self.unit_topic_vector) else leaf_node.topic_vector)
                    unit_vector_topic_class = max(self.unit_topic_vector, key=lambda t: t[1])
                if leaf_node.topic_class not in unit_topics:
                    unit_topics[leaf_node.topic_class] = NS
                else:
                    unit_topics[leaf_node.topic_class] += NS

                # region Write data to pickle file
                if not os.path.exists(file_name):
                    with open(file_name, mode='wb') as dataFile:
                        cur_tup = [(leaf_node.node_number_L,
                                    leaf_node.node_number_R,
                                    leaf_node.text,
                                    leaf_node.topic_class,
                                    leaf_node.ni_score,
                                    leaf_node.node_class,
                                    leaf_node.topic_vector)]
                        pickle.dump(cur_tup, dataFile)
                else:
                    # Read the pickle file, append data and write again
                    with open(file_name, mode='rb') as dataFile:
                        cur_tup = pickle.load(dataFile)
                    with open(file_name, mode='wb') as dataFile:
                        new_tup = (leaf_node.node_number_L,
                                        leaf_node.node_number_R,
                                        leaf_node.text,
                                        leaf_node.topic_class,
                                        leaf_node.ni_score,
                                        leaf_node.node_class,
                                        leaf_node.topic_vector)
                        if new_tup not in cur_tup:
                            cur_tup.append((leaf_node.node_number_L,
                                            leaf_node.node_number_R,
                                            leaf_node.text,
                                            leaf_node.topic_class,
                                            leaf_node.ni_score,
                                            leaf_node.node_class,
                                            leaf_node.topic_vector))
                        pickle.dump(cur_tup, dataFile)
                # endregion

            N_max = max(unit_topics.values())
            topic_max = find_max(unit_topics, N_max)
            if mode == 'V':
                # Mode V
                self.unit_topic = unit_vector_topic_class[0]
                self.unit_topic_score = unit_vector_topic_class[1]
            else:
                # Mode NS
                self.unit_topic = topic_max
                self.unit_topic_score = N_max

    def add_new_node(self, node, tree_height):
        if isinstance(node, leaf):
            self.leaf_nodes[node.node_number_L] = node
            self.update_unit_tree_depth(node.tree_depth)
            self.decide_topic_2(tree_height)
            self.update_text()
            self.update_pure_text()
            self.set_unit_top_node(node.parent)
            if self.unit_top_node != 'root':
                self.set_unit_size(self.unit_top_node.get_complexity() + 1)

    def update_pure_text(self):
        if len(self.text):
            self.pure_text = ' '.join(self.text)
        if len(self.nucleus_text):
            self.nucleus_pure_text = ' '.join(self.nucleus_text)

    def update_unit_tree_depth(self, node_depth):
        if node_depth > self.unit_tree_depth:
            self.unit_tree_depth = node_depth

    # region Nucleus Sent Ranking
    def rank_nucleus_text(self, min_length=None, factor=None):
        """
        Currently not used but working function
        :param min_length:
        :param factor:
        :return:
        """
        # Get the nucleus leafs
        n_leafs = [self.leaf_nodes[l] for l in self.leaf_nodes.keys() if self.leaf_nodes[l].node_class == 'N']
        if len(n_leafs) >= min_length:  # checks if the nucleus text is long enough
            cData = [(l.node_number_L, l.text, l.score, l.topic_class) for l in n_leafs]
            for _ in range(len(cData)):  # checks if nucleus is in the same topic as the unit if not sets the score to 0
                if cData[_][3] != self.unit_topic:
                    cData[_][2] = 0
            cData.sort(key=lambda sent: sent[2], reverse=True)  # Sort by score
            cData = cData[:int(math.ceil(len(cData) * factor))]  # short the list by the factor
            cData.sort(key=lambda sent: sent[0], reverse=False)  # Sort by order
            self.short_nucleus_text = ' '.join([item[1] for item in cData])

    def update_n_tuples(self):
        n_leafs = [self.leaf_nodes[l] for l in self.leaf_nodes.keys() if self.leaf_nodes[l].node_class == 'N']
        self.nucleus_tuples = [(l.node_number_L, l.text, l.score, l.topic_class) for l in n_leafs]

    # endregion

    # region Setters
    def set_unit_top_node(self, node):
        self.unit_top_node = node

    def set_unit_size(self, size):
        self.unit_size = size
    # endregion


class one_leaf_unit(unit):
    def __init__(self):
        super().__init__()

    def set_unit_topic(self, topic_class):
        self.unit_topic = topic_class

    def update_leafs(self):
        if self.unit_top_node is not None:
            self.leaf_nodes[self.unit_top_node.get_L_node_number()] = self.unit_top_node
            self.update_text()

    def decide_topic(self):
        if self.unit_top_node is not None:
            self.unit_topic = self.unit_top_node.topic_class


class unit_connector:
    def __init__(self, node=None):
        global unit_counter
        unit_counter += 1
        self.unit_id = unit_counter
        self.right_child = None
        self.left_child = None
        self.node_object = node

    def set_node(self, node):
        self.node_object = copy.deepcopy(node)

    def set_right_child(self, unit_node):
        self.right_child = copy.deepcopy(unit_node)

    def set_left_child(self, unit_node):
        self.left_child = copy.deepcopy(unit_node)
