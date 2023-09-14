import datetime as dt
import os
import logging
import shutil
import sys

folder = dt.datetime.now().strftime("%y_%m_%d_%H_%M")
path = os.path.join(os.path.expanduser('~'), f"Preprocess_Logger/Log/{folder}")

if os.path.exists(path):
    shutil.rmtree(path)
os.makedirs(path)

logger = logging.getLogger('Preprocess_Logger')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(message)s')

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(formatter)
logger.addHandler(stdout_handler)
