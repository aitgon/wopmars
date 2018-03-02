"""
Module containing the Logger class.
"""
import logging
from logging.handlers import RotatingFileHandler

from wopmars.utils.OptionManager import OptionManager
from wopmars.utils.Singleton import SingletonMixin
from wopmars.utils.ColorPrint import ColorPrint


class Logger(SingletonMixin):
    """
    The logger class allows to write in standard output and rotating files the log of executions

    There is 4 logging handler:
      - stream_handler: the logger which will be called to write in std out.
      - stream_handler_err: the logger which will be called to write errors in std out.
      - file_handler: the logger which will be called to write in the .log rotating file.
      - file_handler_err: the logger logger which will write everything in the .err rotating file.

    The file_handler_err should be used for debuging purposes.
    """

    def __init__(self):
        # the top level logger which will distribute messages to different handlers
        self.__logger = logging.getLogger("wopmars")
        self.__logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')

        # the loger for std out
        self.__stream_handler = logging.StreamHandler()

        # the loger which will write errors in stdout anyway
        self.__stream_handler_err = logging.StreamHandler()
        self.__stream_handler_err.setLevel(logging.WARNING)

        s_path_log_file = OptionManager.instance()["--log"].rsplit(".", 1)[0]
        # log file in append mode of size 1 Mo and 1 backup
        # handler equivalent to stream_handler in term of logging level but write in .log file
        self.__file_handler = RotatingFileHandler(s_path_log_file + ".log", 'a', 1000000, 1)
        formatter_file = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
        self.__file_handler.setFormatter(formatter_file)

        # err file in append mode of size 1 Mo and 1 backup
        # this handler will write everything in the .err file.
        self.__err_handler = RotatingFileHandler(s_path_log_file + ".err", 'a', 1000000, 1)
        formatter_err = logging.Formatter('%(asctime)s :: %(message)s')
        self.__err_handler.setFormatter(formatter_err)
        self.__err_handler.setLevel(logging.DEBUG)

        verbosity = int(OptionManager.instance()["-v"])

        # set the verbosity of the stream handler and file handler depending of the needs of the user.
        if verbosity <= 0:
            self.__stream_handler.setLevel(logging.WARNING)
            self.__file_handler.setLevel(logging.WARNING)
        elif verbosity == 1:
            self.__stream_handler.setLevel(logging.INFO)
            self.__file_handler.setLevel(logging.INFO)
        elif verbosity >= 2:
            self.__stream_handler.setLevel(logging.DEBUG)
            self.__file_handler.setLevel(logging.DEBUG)

        # if printtools is demanded, things about execution will be printed out in std out
        if OptionManager.instance()["--printtools"]:
            self.__logger.addHandler(self.__stream_handler)
        else:
            self.__logger.addHandler(self.__stream_handler_err)
        self.__logger.addHandler(self.__file_handler)
        self.__logger.addHandler(self.__err_handler)

        self.__tw_logger = logging.getLogger("tw")
        self.__tw_streamhandler = logging.StreamHandler()
        self.__tw_logger.addHandler(self.__tw_streamhandler)
        self.__tw_logger.setLevel(logging.DEBUG)

    def info(self, msg):
        formatter_stream = logging.Formatter(ColorPrint.blue('%(levelname)s :: %(asctime)s :: %(message)s'))
        self.__stream_handler.setFormatter(formatter_stream)
        self.__stream_handler_err.setFormatter(formatter_stream)

        self.__logger.info(msg)

    def debug(self, msg):
        formatter_stream = logging.Formatter(ColorPrint.yellow('%(levelname)s :: %(asctime)s :: %(message)s'))
        self.__stream_handler.setFormatter(formatter_stream)
        self.__stream_handler_err.setFormatter(formatter_stream)

        self.__logger.debug(msg)

    def error(self, msg):
        formatter_stream = logging.Formatter(ColorPrint.red('%(levelname)s :: %(asctime)s :: %(message)s'))
        self.__stream_handler.setFormatter(formatter_stream)
        self.__stream_handler_err.setFormatter(formatter_stream)

        self.__logger.error(msg)

    def warning(self, msg):
        formatter_stream = logging.Formatter(ColorPrint.magenta('%(levelname)s :: %(asctime)s :: %(message)s'))
        self.__stream_handler.setFormatter(formatter_stream)
        self.__stream_handler_err.setFormatter(formatter_stream)

        self.__logger.warning(msg)

    def critical(self, msg):
        formatter_stream = logging.Formatter(ColorPrint.red('%(levelname)s :: %(asctime)s :: %(message)s'))
        self.__stream_handler.setFormatter(formatter_stream)

        self.__logger.critical(msg)

    def toolwrapper_debug(self, msg, tw_name):
        if OptionManager.instance()["--toolwrapper-log"]:
            self.__tw_streamhandler.setFormatter(
                logging.Formatter(ColorPrint.green(tw_name + ' ::  %(levelname)s :: %(asctime)s :: %(message)s')))
            self.__tw_logger.debug(msg)

    def toolwrapper_info(self, msg, tw_name):
        if OptionManager.instance()["--toolwrapper-log"]:
            self.__tw_streamhandler.setFormatter(
                logging.Formatter(ColorPrint.green(tw_name + ' :: %(levelname)s :: %(asctime)s :: %(message)s')))
            self.__tw_logger.info(msg)

    def toolwrapper_warning(self, msg, tw_name):
        if OptionManager.instance()["--toolwrapper-log"]:
            self.__tw_streamhandler.setFormatter(
                logging.Formatter(ColorPrint.green(tw_name + ' :: %(levelname)s :: %(asctime)s :: %(message)s')))
            self.__tw_logger.warning(msg)

    def toolwrapper_error(self, msg, tw_name):
        if OptionManager.instance()["--toolwrapper-log"]:
            self.__tw_streamhandler.setFormatter(logging.Formatter(ColorPrint.green(tw_name + ' :: %(asctime)s :: %(levelname)s :: %(message)s')))
            self.__tw_logger.error(msg)

