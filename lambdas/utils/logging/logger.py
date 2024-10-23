"""Logging utilities"""

from os import path

LOG_BASE = path.join(path.dirname(path.realpath(__file__)), "./config/logbase.cfg")


class Logger:
    """Logger - Singleton - using the log object to write logs"""

    _instance = None

    @classmethod
    def instance(cls) -> "Logger":
        """Get the instance of the logger.
        Initialise it if it does not exist.

        Returns:
            Logger: singleton instance of the logger
        """
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
        return cls._instance

    @classmethod
    def add_log_object(cls, log_object) -> None:
        """Add the log object

        Args:
            log_object: the log object from the LambdaApplication
        """
        cls._log_object = log_object

    @classmethod
    def write_log(cls, log_reference: str, log_dict: dict = None, exc_info=None):
        """Write the log"""
        log_dict = log_dict or {}
        cls._log_object.write_log(log_reference, exc_info, log_dict)


LOGGER = Logger.instance()


def initialise_logger(log_object):
    """Initialise the logger"""
    LOGGER.add_log_object(log_object)


def write_log(log_reference: str, log_dict: dict = None, exc_info=None):
    """_summary_

    Args:
        log_reference (str): The log reference from logbase.cfg
        log_dict (dict, optional): Dictionary to populate the log_reference. Defaults to None.
        exc_info (_type_, optional): Unsure. Defaults to None.
    """
    # """Write the log"""
    LOGGER.write_log(log_reference, log_dict, exc_info)
