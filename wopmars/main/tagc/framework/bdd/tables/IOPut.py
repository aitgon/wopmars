"""
Module containing the IOPut class
"""


class IOPut:
    """
    This class will never be instantiated, it will be extended.
    """    
    def is_ready(self):
        """
        Check if the resource contained by self exists on the hard drive.
        This method will be written in subclasses
        :return: boolean: True if ready, False if not
        """
        raise NotImplementedError