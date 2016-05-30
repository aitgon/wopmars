"""
Module containing the Observable class
"""


class Observable:
    """
    class Observable
    """    
    def __init__(self):
        self.__set_observer = set([])

    def get_observers(self):
        """

        :return: set observers
        """
        return self.__set_observer

    def subscribe(self, obs):
        self.__set_observer.add(obs)

    def unsubscribe(self, obs):
        self.__set_observer.discard(obs)
