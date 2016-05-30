"""
Module containing the ToolWrapperObserver class
"""


class ToolWrapperObserver:
    """
    Observers of ToolWrappers should implement this interface.
    """

    def notify_success(self, toolwrapper):
        """
        Behavior of the Observer when the execution of toolwrapper has succeeded.
        :return:
        """
        raise NotImplementedError
