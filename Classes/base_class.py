import enum


class Position(enum.Enum):
    right = 0.3
    left = 0


class base_node:
    def __init__(self, node_text=None, node_class=None, rel2par=None, parent=None):
        self.node_class = node_class  # N - nucleus / S - satellite
        self.rel2par = rel2par
        self.parent = parent
        self.node_number_L = 0
        self.node_number_R = 0
        self.tree_depth = 0
        if node_text is not None:
            self.strip_name(node_text)
        else:
            self.text_description = node_text  # Node pure text from the topic RST tree

    def strip_name(self, input_name):
        self.text_description = input_name
        name = input_name.replace('(', '').replace(')', '').split()  # Remove ( ) and split by space
        node_type = name[0].split('ENDNODENUM')[1]  # Nucleus or Satellite
        if node_type == 'Nucleus':
            self.node_class = 'N'
        elif node_type == 'Satellite':
            self.node_class = 'S'
        if len(name) == 6:
            node_edge = name[1]  # leaf or other
            self.node_number_L = int(name[2])  # leaf number left
            self.node_number_R = int(name[3])
            self.rel2par = name[5]  # rel2par

    def set_depth(self, depth):
        self.tree_depth = depth

    def get_L_node_number(self):
        return self.node_number_L
