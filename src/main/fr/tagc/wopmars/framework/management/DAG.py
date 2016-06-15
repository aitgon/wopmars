"""
Module containing the DAG class
"""
import subprocess

import networkx as nx
from networkx.drawing.nx_pydot import write_dot

from src.main.fr.tagc.wopmars.utils.Logger import Logger
from src.main.fr.tagc.wopmars.utils.SetUtils import SetUtils


class DAG(nx.DiGraph):
    """
    This class inherits from DiGraph class from NetworkX and allows
    to represent a DAG of tool nodes
    """    
    def __init__(self, set_tools=None):
        """
        The DAG can be build from a set of tools, analyzing the successors
        of each.

        ToolWrappers has a method "follows()" wich allow to know if one tool has a dependency for one other. The tools
        of the set_tools are compared each other to extract the dependencies.
        
        :param set_tools: A set of tools
        :return: None
        """
        super().__init__()
        Logger.instance().info("Building the execution DAG...")
        if set_tools:
            # for each tool
            for tool1 in set_tools:
                self.add_node(tool1)
                # for each other tool
                for tool2 in set_tools.difference(set([tool1])):
                    # is there a dependency between tool1 and tool2?
                    # todo mettre a jour childrule pour les entrées dans la table
                    if tool1.follows(tool2):
                        self.add_edge(tool2, tool1)
        Logger.instance().info("DAG built.")

    def write_dot(self, path):
        """
        Build the dot file.

        The .ps can be built from the dot file with the command line: "dot -Tps {filename}.dot - o {filename}.ps"

        :return: void
        """
        # To build .ps : dot -Tps {filename}.dot - o {filename}.ps
        nx.draw(self)
        write_dot(self, path)
        # building the openable file:
        list_popen = ["dot", "-Tps", path, "-o", path.rsplit("/", 1)[0] + "/" + path.rsplit("/", 1)[1].split(".")[-2] + ".ps"]
        Logger.instance().debug("SubProcess command line for .ps file: " + str(list_popen))
        p = subprocess.Popen(list_popen)
        p.wait()

    def successors(self, node):
        """
        Get the successors of a node.

        The method is overwhelmed because if a node is None, then, the root nodes are returned

        :param node: an object that is used as Node in the DAG or None.
        :return: [node]:  the successors of the given node or the node at the root of the DAG.
        """
        if not node:
            # in_degree is the number of incoming edges to a node. If the degree is 0, then the node is at the root
            # of the DAG.
            return [n for n, d in self.in_degree().items() if d == 0]
        else:
            return super().successors(node)

    def __eq__(self, other):
        """
        Test if self equals other.

        Check the number of nodes and the set of edges of each graphs.

        :param other: A DAG
        :return: True if self == other
        """
        assert isinstance(other, self.__class__)
        int_nodes_self = len(self.nodes())
        int_nodes_other = len(other.nodes())

        set_edges_self = set(self.edges())
        set_edges_other = set(other.edges())

        return (
            int_nodes_self == int_nodes_other and
            SetUtils.all_elm_of_one_set_in_one_other(set_edges_self, set_edges_other) and
            SetUtils.all_elm_of_one_set_in_one_other(set_edges_other, set_edges_self)
        )