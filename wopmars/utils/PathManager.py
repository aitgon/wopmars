"""
Example of module documentation which can be
multiple-lined
"""
import errno
import importlib
import os
import pathlib


class PathManager:
    """
    Static class for finding paths
    """
    @staticmethod
    def get_package_path():
        """
        Find the root directory of the package

        :return: the path leading to the src file of the project
        """

        package_path = os.path.join(os.path.dirname(__file__), "../..")
        return package_path

    @staticmethod
    def get_test_path():
        """
        Find the tests output of the project

        :return: the output leading to the tests output of the project
        """

        test_dir_path = os.path.join(os.path.dirname(__file__), "../tests")
        pathlib.Path(test_dir_path).mkdir(parents=True, exist_ok=True)
        return test_dir_path

    @staticmethod
    def check_pygraphviz(path):
        importlib.import_module("pygraphviz")

    # @staticmethod
    # def create_workingdir(path):
    #     try:
    #         os.makedirs(path)
    #         return True
    #     except OSError as exception:
    #         if exception.errno != errno.EEXIST:
    #             raise
    #             return True

    @staticmethod
    def check_database_valid_url(url):
        """
        Check if the path given is correct on the system.

        If path is None, return None.

        :param path:
        :return:
        """
        db_connection = url.split("://")[0]
        if db_connection == "sqlite":
            sqlite_db_path = url.replace("sqlite:///", "")
            if not os.path.isabs(sqlite_db_path):
                sqlite_db_path = os.path.join(os.getcwd(), sqlite_db_path)
            try:
                os.makedirs(os.path.dirname(sqlite_db_path))
            except OSError as exception:
                if exception.errno != errno.EEXIST:
                    raise
            if sqlite_db_path is None or os.access(os.path.dirname(os.path.abspath(os.path.expanduser(sqlite_db_path))), os.W_OK) or sqlite_db_path[0] == "$":
                return sqlite_db_path
            else:
                raise FileNotFoundError

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
    def unlink(path):
        """
        Remove a file that may not exist.

        Parameters
        ----------
        path

        Returns
        -------

        """
        try:
            pathlib.Path(path).unlink()
        except FileNotFoundError:
            pass

    @staticmethod
    def dir_content_remove(path):
        for f in os.listdir(path):
            if not f.startswith("."):
                PathManager.unlink(os.path.join(path, f))

    @staticmethod
    def is_in_python_path(name):
        importlib.import_module(name)
