import logging
import sys

root = logging.getLogger("app")
root.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)

def disable_log():
    logging.getLogger("app").setLevel(logging.NOTSET)

def debug(msg):
    logging.getLogger("app").debug(msg)
def critical(msg):
    logging.getLogger("app").critical(msg)
def info(msg):
    logging.getLogger("app").info(msg)