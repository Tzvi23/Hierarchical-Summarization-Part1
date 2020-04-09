from Classes.base_class import base_node
from Classes.leaf_class import leaf


def compute_complexity(comp, child=None):
    """
    Returns the number of nodes under the specific node provided
    :param comp: INT
    :param child: Node
    :return: number of nodes under the child node provided
    """
    if isinstance(child, node):
        comp += 1
    if isinstance(child, leaf):
        comp += 1
        return comp
    if child.right_child is not None:
        comp = compute_complexity(comp, child.right_child)
    if child.left_child is not None:
        comp = compute_complexity(comp, child.left_child)
    return comp


def compute_depth(c_node, max_depth):
    """
    Computes the number of levels under the node provided
    :param c_node: Node provided
    :param max_depth: The value returned INT
    :return: number of levels under the node provided
    """
    if c_node.tree_depth > max_depth:
        max_depth = c_node.tree_depth
    if isinstance(c_node, leaf):
        return max_depth
    if c_node.right_child is not None:
        max_depth = compute_depth(c_node.right_child, max_depth)
    if c_node.left_child is not None:
        max_depth = compute_depth(c_node.left_child, max_depth)
    return max_depth


def update_IsComplex(test_node, complex_status):
    if isinstance(test_node, node) and test_node.isComplex is True:
        return True
    if isinstance(test_node, leaf):
        return complex_status
    if test_node.right_child is not None:
        complex_status = update_IsComplex(test_node.right_child, complex_status)
    if test_node.left_child is not None:
        complex_status = update_IsComplex(test_node.left_child, complex_status)
    return complex_status


class node(base_node):
    def __init__(self, node_text=None, node_class=None, rel2par=None, parent=None, right_child=None, left_child=None):
        super().__init__(node_text, node_class, rel2par, parent)
        self.right_child = right_child
        self.left_child = left_child
        self.complexity = 0  # Complexity - counts how many nodes under this node
        self.depth = 0
        self.isComplex = False  # True - complex False - simple (at least one of children is a leaf)

    def set_complexity(self):
        self.complexity = compute_complexity(0, self) - 1

    def set_depth_complex(self):
        max_depth = compute_depth(self, 0)
        self.depth = max_depth - self.tree_depth

    def set_IsComplex(self):
        if (self.right_child is not None and isinstance(self.right_child, leaf)) or (self.left_child is not None and isinstance(self.left_child, leaf)):
            self.isComplex = False  # At lest of one of the children is a leaf
        else:
            self.isComplex = True

    def update_IsComplex(self):
        self.isComplex = update_IsComplex(self, self.isComplex)

    def get_complexity(self):
        if self.complexity == 0:
            self.set_complexity()
        return self.complexity
