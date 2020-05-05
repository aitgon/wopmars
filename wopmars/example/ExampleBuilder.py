import os
import shutil
import errno

from wopmars.utils.OptionManager import OptionManager
from wopmars.utils.WopMarsException import WopMarsException


class ExampleBuilder:
    """
    This class is used to build the examples for the tutorials.

    Each method is supposed to build one distinct example.
    """

    def build(self):
        # self.build_file_architecture()
        """
        This builds the car example.
        """
        src_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "wopexample")
        dst_path = os.path.join(OptionManager.instance()["--directory"], "wopexample")

        shutil.rmtree(dst_path, ignore_errors=True)
        shutil.copytree(src_path, dst_path)

        # empty.txt is an empty text file used in order to take into account the output directory
        os.remove(os.path.join(dst_path, "output/empty.txt"))

    # def build_file_architecture(self):
    #     """
    #     This builds the car example.
    #     """
    #     __cwd = os.path.join(OptionManager.instance()["--directory"], "wopmars_example")
    #     example_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), "wopmars_example")
    #
    #     # copy the folder wopmars_example in __cwd
    #     ExampleBuilder.copy(example_directory, __cwd)
    #
    #     # empty.txt is an empty text file used in order to take into account the output directory
    #     os.remove(os.path.join(__cwd, "output/empty.txt"))

    # def build_snp(self):
    #     self.build_file_architecture_snp()
    #
    # def build_file_architecture_snp(self):
    #     """
    #     This builds the snp example.
    #     """
    #     __cwd = os.path.join(OptionManager.instance()["--directory"], "wopmars_example_snp")
    #     example_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), "wopmars_example_snp")
    #
    #     # copy the folder wopmars_example in __cwd
    #     ExampleBuilder.copy(example_directory, __cwd)
    #
    #     # empty.txt is an empty text file used in order to take into account the output directory
    #     os.remove(os.path.join(__cwd, "output/empty.txt"))

    @staticmethod
    # http://pythoncentral.io/how-to-recursively-copy-a-directory-folder-in-python/
    def copy(src, dest):
        try:
            shutil.copytree(src, dest, ignore=shutil.ignore_patterns('__pycache__'))
        except OSError as e:
            # If the error was caused because the source wasn't a directory
            if e.errno == errno.ENOTDIR:
                shutil.copy(src, dest)
            else:
                raise WopMarsException("Error while building the example", 'Directory not copied. Error: %s' % e)
