"""
Module containing the Logger class.
"""
import logging
import os
from logging.handlers import RotatingFileHandler

from src.main.fr.tagc.wopmars.utils.Singleton import SingletonMixin
from src.main.fr.tagc.wopmars.utils.ColorPrint import ColorPrint
from src.main.fr.tagc.wopmars.utils.OptionManager import OptionManager
from src.main.fr.tagc.wopmars.utils.PathFinder import PathFinder
from src.main.fr.tagc.wopmars.utils.Singleton import singleton


class Logger(SingletonMixin):
    """
    class Logger
    """

    def __init__(self):
        """
        

        :return:
        """
        self.__logger = logging.getLogger()
        self.__logger.setLevel(logging.DEBUG)

        self.__stream_handler = logging.StreamHandler()
        s_path_log_file = OptionManager.instance()["--log"].rsplit(".", 1)[0]
        # log file in append mode of size 1 Mo and 1 backup
        self.__file_handler = RotatingFileHandler(s_path_log_file + ".log", 'a', 1000000, 1)
        formatter_file = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
        self.__file_handler.setFormatter(formatter_file)
        # err file in append mode of size 1 Mo and 1 backup
        self.__err_handler = RotatingFileHandler(s_path_log_file + ".err", 'a', 1000000, 1)
        formatter_err = logging.Formatter('%(asctime)s :: %(message)s')
        self.__err_handler.setFormatter(formatter_err)
        self.__err_handler.setLevel(logging.WARNING)

        verbosity = OptionManager.instance()["-v"]

        if verbosity == 1:
            self.__stream_handler.setLevel(logging.ERROR)
            self.__file_handler.setLevel(logging.ERROR)
        elif verbosity == 2 or verbosity <= 0:
            self.__stream_handler.setLevel(logging.WARNING)
            self.__file_handler.setLevel(logging.WARNING)
        elif verbosity == 3:
            self.__stream_handler.setLevel(logging.INFO)
            self.__file_handler.setLevel(logging.INFO)
        elif verbosity >= 4:
            self.__stream_handler.setLevel(logging.DEBUG)
            self.__file_handler.setLevel(logging.DEBUG)

        if OptionManager.instance()["--noisy"]:
            self.__logger.addHandler(self.__stream_handler)
        self.__logger.addHandler(self.__file_handler)
        self.__logger.addHandler(self.__err_handler)

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

