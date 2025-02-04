import logging

from .log_levels import get_log_level


class Logger:
    def __init__(self, name="my_logger", level="INFO"):
        self.logger = logging.getLogger(name)
        self.set_level(level)
        self.handlers = []

    def set_level(self, level):
        self.logger.setLevel(get_log_level(level))

    def add_handler(self, handler):
        self.logger.addHandler(handler)
        self.handlers.append(handler)

    def log(self, level, message):
        self.logger.log(get_log_level(level), message)

    def debug(self, message):
        self.log("DEBUG", message)

    def info(self, message):
        self.log("INFO", message)

    def warning(self, message):
        self.log("WARNING", message)

    def error(self, message):
        self.log("ERROR", message)

    def critical(self, message):
        self.log("CRITICAL", message)
