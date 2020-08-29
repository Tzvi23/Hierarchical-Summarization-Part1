from Classes.base_class import base_node, Position


class leaf(base_node):
    def __init__(self, node_text=None, node_class=None, rel2par=None, parent=None):
        super().__init__(node_text, node_class, rel2par, parent)
        self.topic_class = -9
        self.score = 0
        self.text = ''
        self.position = 0
        self.ni_score = 0
        self.topic_vector = list()

    def set_position(self, leaf_pos):
        self.position = leaf_pos
