import json

class nodeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, node_graph):
            if o.children is not None:
                return {'name': o.name, 'parent': o.parent, 'children': [child for child in o.children]}
            else:
                return {'name': o.name, 'parent': o.parent}
        return json.JSONEncoder.default(self, o)

class node_type:
    leaf = 0
    node = 1

class node_graph:
    def __init__(self, name=None, parent='null', children=True):
        self.name = name
        self.parent = parent
        if children is True:
            self.node_class = node_type.node
            self.children = list()
        else:
            self.node_class = node_type.leaf
            self.children = None

    def set_name(self, name):
        self.name = name

    def set_parent(self, parent):
        self.parent = parent

    def add_children(self, child):
        if self.node_class == node_type.node:
            self.children.append(child)
        else:
            print('Leaf node - no children')

    def __str__(self):
        return '%name: {0}, parent: {1}&'.format(self.name, self.parent)