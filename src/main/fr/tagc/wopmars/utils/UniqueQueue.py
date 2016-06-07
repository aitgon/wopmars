"""
Module containing the UniqueQueue class.
"""
from queue import Queue


class UniqueQueue(Queue):
    """
    The UniqueQueue re-implement Queue, modificating its _put method to ensure that each element is unique.
    """

    def _put(self, item):
        """
        Check if item is already in queue. If not, append the queue and return True, else, return False.

        :param item: an item that has to be added to the Queue
        :return: bool for the success of the put method
        """
        if item not in self.queue:
            # Todo ask lionel il vaut peut etre mieux enlever l'élement déjà présent et le mettre à la fin de la queue
            self.queue.append(item)
