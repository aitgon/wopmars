"""
Module containing the DAG class
"""
import os
import subprocess

import networkx as nx
from networkx.drawing.nx_pydot import write_dot


from fr.tagc.wopmars.framework.rule.IOFilePut import IOFilePut
from fr.tagc.wopmars.framework.rule.ToolWrapper import ToolWrapper


class DAG(nx.DiGraph):
    """
    This class inherits from DiGraph class from NetworkX and allows
    to represent a DAG of tool nodes
    """    
    def __init__(self, set_tools=None):
        """
        The DAG can be build from a set of tools, analyzing the successors
        of each.
        
        :param set_tools: A set of tools
        :return: None
        """
        super().__init__()
        #todo loging
        print("Building the execution DAG...", end="")
        if set_tools:
            # pour chaque outil 1
            for tool1 in set_tools:
                # pour chaque autre outil 2
                for tool2 in set_tools.difference(set([tool1])):
                    # est-ce-que l'outil 1 est après l'outil 2?
                    if tool1.follows(tool2):
                        # dépendance entre outil 2 et outil 1
                        self.add_edge(tool2, tool1)
        print(" -> done.")

    def write_dot(self, path):
        """
        Build the dot file.

        :return: void
        """

        # To build .ps : dot -Tps {filename}.dot - o {filename}.ps
        nx.draw(self)
        write_dot(self, path)

    def successors(self, node=None):
        if not node:
            return [n for n, d in self.in_degree().items() if d == 0]
        else:
            return super().successors(node)


if __name__ == "__main__":
    toolwrapper_first = ToolWrapper({"input1": IOFilePut("input1", "file1.txt")},
                                           {"output1": IOFilePut("output1", "file2.txt")},
                                           {})

    toolwrapper_second = ToolWrapper({"input1": IOFilePut("input1", "file2.txt")},
                                        {"output1": IOFilePut("output1", "file3.txt")},
                                        {})
    my_dag = DAG(set([toolwrapper_first, toolwrapper_second]))