"""
Example of module documentation which can be
multiple-lined
"""
import importlib
import os


class PathFinder:
    """
    Static class for finding paths
    """
    @staticmethod
    def find_src(path):
        """
        Find the Src directory of the project

        :return: the path leading to the src file of the project
        """
        file_path_splitted = path.split('/')
        root_path = "/".join(file_path_splitted[:file_path_splitted.index('wopmars') + 1]) + "/"
        return root_path

    @staticmethod
    def check_valid_path(path):
        """
        Check if the path given is correct on the system.

        If path is None, return None.

        :param path:
        :return:
        """
        if path is None or os.access(os.path.dirname(os.path.abspath(os.path.expanduser(path))), os.W_OK) or path[0] == "$":
            return path
        else:
            raise FileNotFoundError

    @staticmethod
    def silentremove(path):
        """
        Remove a file that may not exist.
        :param path:
        :return:
        """
        try:
            os.remove(path)
        except OSError:
            pass

    @staticmethod
    def dir_content_remove(path):
        for f in os.listdir(path):
            if not f.startswith("."):
                PathFinder.silentremove(os.path.join(path, f))

    @staticmethod
    def is_in_python_path(name):
        importlib.import_module(name)