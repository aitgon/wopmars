"""
Module containing the Singleton function.
"""
import threading


def singleton(cls):
    instances = {}

    def class_instanciation_or_not(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return class_instanciation_or_not


# Based on tornado.ioloop.IOLoop.instance() approach.
# See https://github.com/facebook/tornado
class SingletonMixin(object):
    __singleton_lock = threading.Lock()
    __singleton_instance = None

    @classmethod
    def instance(cls):
        if not cls.__singleton_instance:
            with cls.__singleton_lock:
                if not cls.__singleton_instance:
                    cls.__singleton_instance = cls()
        return cls.__singleton_instance

    @classmethod
    def _drop(cls):
        """Drop the instance (for testing purposes)."""
        if cls.__singleton_instance:
            with cls.__singleton_lock:
                if cls.__singleton_instance:
                    cls.__singleton_instance = None