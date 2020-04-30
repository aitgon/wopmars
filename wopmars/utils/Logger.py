"""
Module containing the Logger class.
"""
import logging
import sys
from logging.handlers import RotatingFileHandler

from wopmars.utils.OptionManager import OptionManager
from wopmars.utils.Singleton import SingletonMixin
from wopmars.utils.ColorPrint import ColorPrint


class LessThanFilter(logging.Filter):
    def __init__(self, exclusive_maximum, name=""):
        super(LessThanFilter, self).__init__(name)
        self.max_level = exclusive_maximum

    def filter(self, record):
        #non-zero return means we log this message
        return 1 if record.levelno < self.max_level else 0


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

        self.__logger = logging.getLogger('wopmars')
        self.formatter_str = '%(asctime)s :: %(levelname)s :: %(name)s :: %(message)s'
        formatter = logging.Formatter(self.formatter_str)
        self.__logger.setLevel(logging.DEBUG)  # set root's level

        verbosity = int(OptionManager.instance()["-v"])

        ################################################################################################################
        #
        # Stream stderr
        #
        ################################################################################################################

        self.stream_handler_stderr = logging.StreamHandler(stream=sys.stderr)
        self.stream_handler_stderr.setFormatter(formatter)
        self.stream_handler_stderr.setLevel(logging.WARNING)
        self.__logger.addHandler(self.stream_handler_stderr)

        ################################################################################################################
        #
        # Stream stdout
        #
        ################################################################################################################

        self.stream_handler_stdout = logging.StreamHandler(stream=sys.stdout)
        self.stream_handler_stdout.setFormatter(formatter)
        if verbosity <= 0:
            self.stream_handler_stdout.setLevel(logging.WARNING)
        if verbosity == 1:
            self.stream_handler_stdout.setLevel(logging.INFO)
        elif verbosity >= 2:
            self.stream_handler_stdout.setLevel(logging.DEBUG)
        self.stream_handler_stdout.addFilter(LessThanFilter(logging.WARNING)) # Does not print in stdout higher/equal than warning
        self.__logger.addHandler(self.stream_handler_stdout)

        ################################################################################################################
        #
        # File stderr
        #
        ################################################################################################################

        if "--log" in OptionManager.instance():

            if not OptionManager.instance()["--log"] is None:

                log_stdout_path = OptionManager.instance()["--log"].rsplit(".", 1)[0]

                # log file in append mode of size 1 Mo and 1 backup
                # handler equivalent to stream_handler in term of logging level but write in .log file
                self.__file_handler_stdout = RotatingFileHandler(log_stdout_path + ".log", 'a', 1000000, 1)
                self.__file_handler_stdout.setFormatter(formatter)
                if verbosity <= 0:
                    self.__file_handler_stdout.setLevel(logging.WARNING)
                if verbosity == 1:
                    self.__file_handler_stdout.setLevel(logging.INFO)
                elif verbosity >= 2:
                    self.__file_handler_stdout.setLevel(logging.DEBUG)
                self.__file_handler_stdout.addFilter(LessThanFilter(logging.WARNING)) # Does not print in stdout higher/equal than warning
                self.__logger.addHandler(self.__file_handler_stdout)

                # err file in append mode of size 1 Mo and 1 backup
                # this handler will write everything in the .err file.
                self.__file_handler_stderr = RotatingFileHandler(log_stdout_path + ".err", 'a', 1000000, 1)
                self.__file_handler_stderr.setFormatter(formatter)
                self.__file_handler_stderr.setLevel(logging.WARNING)
                self.__logger.addHandler(self.__file_handler_stderr)

    def debug(self, msg):
        formatter_stream = logging.Formatter(ColorPrint.blue(self.formatter_str))
        self.stream_handler_stderr.setFormatter(formatter_stream)
        self.stream_handler_stdout.setFormatter(formatter_stream)
        self.__logger.debug(msg)

    def info(self, msg):
        formatter_stream = logging.Formatter(ColorPrint.green(self.formatter_str))
        self.stream_handler_stderr.setFormatter(formatter_stream)
        self.stream_handler_stdout.setFormatter(formatter_stream)
        self.__logger.info(msg)

    def warning(self, msg):
        formatter_stream = logging.Formatter(ColorPrint.yellow(self.formatter_str))
        self.stream_handler_stderr.setFormatter(formatter_stream)
        self.stream_handler_stdout.setFormatter(formatter_stream)
        self.__logger.warning(msg)

    def error(self, msg):
        formatter_stream = logging.Formatter(ColorPrint.red(self.formatter_str))
        self.stream_handler_stderr.setFormatter(formatter_stream)
        self.stream_handler_stdout.setFormatter(formatter_stream)
        self.__logger.error(msg)

    def critical(self, msg):
        formatter_stream = logging.Formatter(ColorPrint.red(self.formatter_str))
        self.stream_handler_stderr.setFormatter(formatter_stream)
        self.stream_handler_stdout.setFormatter(formatter_stream)
        self.__logger.critical(msg)
