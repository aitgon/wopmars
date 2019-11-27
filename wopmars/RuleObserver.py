"""
Module containing the RuleObserver class
"""


class RuleObserver:
    """
    Observers of ToolWrappers should implement this interface.
    """

    def notify_success(self, toolwrapper):
        """
        Behavior of the Observer when the execution of toolwrapper has succeeded.
        :return:
        """
        raise NotImplementedError

    def notify_failure(self, toolwrapper):
        """
        Behavior of the Observer when the execution of toolwrapper has failed.
        :return:
        """
        raise NotImplementedError
