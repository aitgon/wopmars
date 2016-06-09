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

        # stream ------------------:
        self.__stream_handler = logging.StreamHandler()

        verbosity = OptionManager()["-v"]

        if verbosity <= 1:
            self.__stream_handler.setLevel(logging.ERROR)
        elif verbosity == 2:
            self.__stream_handler.setLevel(logging.WARNING)
        elif verbosity == 3 or verbosity == 0:
            self.__stream_handler.setLevel(logging.INFO)
        elif verbosity >= 4:
            self.__stream_handler.setLevel(logging.DEBUG)

        # configure logger -------------------:

        self.__logger = logging.getLogger()
        self.__logger.setLevel(logging.DEBUG)
        self.__logger.addHandler(self.__stream_handler)

        # Rotating file -------------------:

        formatter_file = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')

        # file in append mode of size 1 Mo and 1 backup
        # todo ask lionel le fichier de log doit-il TOUJOURS etre ecris? ou je le met en option?
        s_path_log_file = OptionManager()["--log"]
        if s_path_log_file:
            file_handler = RotatingFileHandler(s_path_log_file, 'a', 1000000, 1)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter_file)

            # adding the handler if user want logfile
            self.__logger.addHandler(file_handler)

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

