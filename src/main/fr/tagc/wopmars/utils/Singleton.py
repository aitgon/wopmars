"""
Module containing the Singleton function.
"""


def singleton(cls):
    instances = {}

    def class_instanciation_or_not(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return class_instanciation_or_not
