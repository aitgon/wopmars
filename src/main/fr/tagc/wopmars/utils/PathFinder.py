"""
Example of module documentation which can be
multiple-lined
"""
import os


class PathFinder:
    """
    Static class for finding paths
    """
    @staticmethod
    def find_src(path):
        """
        Find the Src directory of a project

        :return: the path leading to the src file of the project
        """
        file_path_splitted = path.split('/')
        root_path = "/".join(file_path_splitted[:file_path_splitted.index("src") + 1]) + "/"
        return root_path

    @staticmethod
    def check_valid_path(path):
        """
        Check if the path given is correct on the system.

        If path is None, return None.

        :param path:
        :return:
        """
        if path is None or os.access(os.path.dirname(path), os.W_OK) or path[0] == "$":
            return path
        else:
            raise FileNotFoundError
