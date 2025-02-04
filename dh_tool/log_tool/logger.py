import logging


class Logger:
    def __init__(self, name="my_logger", level=logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.handlers = []

    def add_handler(self, handler):
        self.logger.addHandler(handler)
        self.handlers.append(handler)

    def log(self, level, message):
        self.logger.log(level, message)

    def debug(self, message):
        self.log(logging.DEBUG, message)

    def info(self, message):
        self.log(logging.INFO, message)

    def error(self, message):
        self.log(logging.ERROR, message)
