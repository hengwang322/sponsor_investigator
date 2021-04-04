import logging
import os

def get_logger(log_name, log_file):
    log_dir = os.path.join('.', 'log')
    if not os.path.isdir(log_dir):
        os.makedirs(log_dir)
    log_handler = logging.FileHandler(os.path.join(
        log_dir, log_file))
    log_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)-8s %(message)s', '%m-%d %H:%M:%S'))
    logger = logging.getLogger(log_name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(log_handler)

    return logger

def get_console_log():
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter('%(levelname)-8s %(message)s'))
    logging.getLogger('').addHandler(console)
    return console