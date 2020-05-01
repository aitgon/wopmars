from termcolor import colored


class ColorPrint:
    """
    Static class which allow to return colored text in order to be printed
    """

    @staticmethod
    def yellow(text):
        return colored(text, 'yellow', attrs=['bold'])

    @staticmethod
    def green(text):
        return colored(text, 'green', attrs=['dark'])

    @staticmethod
    def red(text):
        return colored(text, 'red', attrs=[])

    @staticmethod
    def blue(text):
        return colored(text, 'blue', attrs=['bold'])
