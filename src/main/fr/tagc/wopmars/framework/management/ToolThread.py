"""
Module containing the ToolThread class.
"""
import threading

from src.main.fr.tagc.wopmars.framework.bdd.SQLManager import SQLManager
from src.main.fr.tagc.wopmars.framework.management.Observable import Observable
from src.main.fr.tagc.wopmars.utils.Logger import Logger


class ToolThread(threading.Thread, Observable):
    """
    class ToolThread
    """

    def __init__(self, toolwrapper):
        """
        

        :return:
        """
        threading.Thread.__init__(self)
        self.__set_observer = set([])
        self.__toolwrapper = toolwrapper
        self.__dry = False

    def get_toolwrapper(self):
        return self.__toolwrapper

    def set_dry(self, dry):
        self.__dry = dry

    def run(self):
        """
        Run the tool and fire events.
        :return:
        """
        Logger.instance().info(self.__toolwrapper.__class__.__name__ + " started.")
        session_tw = SQLManager.instance().get_session()
        try:
            self.__toolwrapper.set_session(session_tw)
            if not self.__dry:
                self.__toolwrapper.run()
            session_tw.commit()
        except Exception as e:
            session_tw.rollback()
            raise e
        finally:
            # todo twthread , fermer session
            # session_tw.close()
            pass
        self.fire_success()

    def get_observers(self):
        """
        Return the set of observers.

        :return: set observers
        """
        return self.__set_observer

    def subscribe(self, obs):
        """
        An observer subscribes to the obervable.

        :param obs:
        :return:
        """
        self.__set_observer.add(obs)

    def fire_failure(self):
        """
        Notify all ToolWrapperObservers that the execution has failed.

        :return:
        """
        for obs in self.get_observers():
            obs.notify_failure(self)

    def fire_success(self):
        """
        Notify all ToolWrapperObservers that the run has suceeded

        :return:
        """
        for obs in self.get_observers():
            obs.notify_success(self)

    def __eq__(self, other):
        assert isinstance(other, self.__class__)
        return self.__toolwrapper == other.get_toolwrapper()

    def __hash__(self):
        return id(self)