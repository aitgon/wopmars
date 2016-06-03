"""
Module containing the Logger class.
"""
import logging
from logging.handlers import RotatingFileHandler

from fr.tagc.wopmars.utils.OptionManager import OptionManager
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
        file_handler = RotatingFileHandler('/home/giffon/wopmars.log', 'a', 1000000, 1)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter_file)

        # stream ------------------:

        # todo ask aitor afficher de la couleur dans la console? oui
        formatter_stream = logging.Formatter('%(levelname)s :: %(message)s')

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter_stream)

        verbosity = OptionManager()["-v"]

        if verbosity == 1:
            stream_handler.setLevel(logging.ERROR)
        elif verbosity == 2:
            stream_handler.setLevel(logging.WARNING)
        elif verbosity == 3 or stream_handler == 0:
            stream_handler.setLevel(logging.INFO)
        elif verbosity == 4:
            stream_handler.setLevel(logging.DEBUG)

        # configure logger -------------------:

        self.__logger = logging.getLogger()
        self.__logger.setLevel(logging.DEBUG)

        self.__logger.addHandler(file_handler)
        self.__logger.addHandler(stream_handler)

    def info(self, msg):
        self.__logger.info(msg)

    def debug(self, msg):
        self.__logger.debug(msg)

    def error(self, msg):
        self.__logger.error(msg)

    def warning(self, msg):
        self.__logger.warning(msg)

    def critical(self, msg):
        self.__logger.critical(msg)


if __name__ == "__main__":
    l = Logger()
    l.info("salut")
    l.debug("salut")
    l.error("salut")
    l.warning("salut")
    l.critical("salut")

