"""
Module containing the Observable class
"""


class Observable:
    """
    class Observable
    """    
    def get_observers(self):
        """

        :return: set observers
        """
        raise NotImplementedError

    def subscribe(self, obs):
        raise NotImplementedError

    def fire_failure(self):
        raise NotImplementedError

    def fire_success(self):
        raise NotImplementedError

