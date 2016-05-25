"""
Module containing the DAG class
"""
import networkx as nx

from src.main.fr.tagc.wopmars.framework.rule.IOFilePut import IOFilePut
from src.main.fr.tagc.wopmars.framework.rule.ToolWrapper import ToolWrapper


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
        if set_tools:
            for tool1 in set_tools:
                for tool2 in set_tools.difference(set([tool1])):
                    if tool1.follows(tool2):
                        self.add_edge(tool2, tool1)

if __name__ == "__main__":
    toolwrapper_first = ToolWrapper({"input1": IOFilePut("input1", "file1.txt")},
                                           {"output1": IOFilePut("output1", "file2.txt")},
                                           {})

    toolwrapper_second = ToolWrapper({"input1": IOFilePut("input1", "file2.txt")},
                                        {"output1": IOFilePut("output1", "file3.txt")},
                                        {})
    my_dag = DAG(set([toolwrapper_first, toolwrapper_second]))