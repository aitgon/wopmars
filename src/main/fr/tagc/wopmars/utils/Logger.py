"""
Module containing the Logger class.
"""
import logging
import os
from logging.handlers import RotatingFileHandler

from fr.tagc.wopmars.utils.ColorPrint import ColorPrint
from fr.tagc.wopmars.utils.OptionManager import OptionManager
from fr.tagc.wopmars.utils.PathFinder import PathFinder
from fr.tagc.wopmars.utils.Singleton import singleton


@singleton
class Logger:
    """
    class Logger
    """

    def __init__(self):
        """
        

        :return:
        """

        # Rotating file -------------------:

        formatter_file = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')

        # file in append mode of size 1 Mo and 1 backup
        file_handler = RotatingFileHandler(PathFinder.find_src(os.path.dirname(os.path.realpath(__file__))) + '../log/wopmars.log', 'a', 1000000, 1)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter_file)

        # stream ------------------:
        self.__stream_handler = logging.StreamHandler()

        verbosity = OptionManager()["-v"]

        if verbosity == 1:
            self.__stream_handler.setLevel(logging.ERROR)
        elif verbosity == 2:
            self.__stream_handler.setLevel(logging.WARNING)
        elif verbosity == 3 or verbosity == 0:
            self.__stream_handler.setLevel(logging.INFO)
        elif verbosity == 4:
            self.__stream_handler.setLevel(logging.DEBUG)

        # configure loggers -------------------:

        self.__logger = logging.getLogger()
        self.__logger.setLevel(logging.DEBUG)
        self.__logger.addHandler(file_handler)
        self.__logger.addHandler(self.__stream_handler)

    def info(self, msg):
        formatter_stream = logging.Formatter(ColorPrint.blue('%(levelname)s :: %(message)s'))
        self.__stream_handler.setFormatter(formatter_stream)

        self.__logger.info(msg)

    def debug(self, msg):
        formatter_stream = logging.Formatter(ColorPrint.yellow('%(levelname)s :: %(message)s'))
        self.__stream_handler.setFormatter(formatter_stream)

        self.__logger.debug(msg)

    def error(self, msg):
        formatter_stream = logging.Formatter(ColorPrint.red('%(levelname)s :: %(message)s'))
        self.__stream_handler.setFormatter(formatter_stream)

        self.__logger.error(msg)

    def warning(self, msg):
        formatter_stream = logging.Formatter(ColorPrint.red('%(levelname)s :: %(message)s'))
        self.__stream_handler.setFormatter(formatter_stream)

        self.__logger.warning(msg)

    def critical(self, msg):
        formatter_stream = logging.Formatter(ColorPrint.red('%(levelname)s :: %(message)s'))
        self.__stream_handler.setFormatter(formatter_stream)

        self.__logger.critical(msg)


if __name__ == "__main__":
    OptionManager()["-v"] = 4
    l = Logger()
    l.info("salut")
    l.debug("salut")
    l.error("salut")
    l.warning("salut")
    l.critical("salut")

