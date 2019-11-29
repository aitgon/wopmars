"""
Module containing the ToolWrapperObserver class
"""


class ToolWrapperObserver:
    """
    Observers of ToolWrappers should implement this interface.
    """

    def notify_success(self, toolwrapper):
        """
        Behavior of the Observer when the execution of tool_python_path has succeeded.
        :return:
        """
        raise NotImplementedError

    def notify_failure(self, toolwrapper):
        """
        Behavior of the Observer when the execution of tool_python_path has failed.
        :return:
        """
        raise NotImplementedError
