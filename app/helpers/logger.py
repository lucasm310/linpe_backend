# coding: utf-8
import os
import sys
import logging


def get_logger():
    logger_handler = logging.StreamHandler(sys.stdout)
    date_format = "%Y-%m-%d %H:%M:%S"
    format_string = '%(asctime)s %(levelname)s %(message)s'
    logger_handler.setFormatter(logging.Formatter(format_string, date_format))
    logger = logging.getLogger("api")
    logger.setLevel("INFO")
    logger.addHandler(logger_handler)
    return logger

