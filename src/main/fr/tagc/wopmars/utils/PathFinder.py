"""
Example of module documentation which can be
multiple-lined
"""


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
