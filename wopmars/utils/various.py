import codecs
from datetime import datetime
import os
import time


def get_current_time():
    timestamp = time.time()  # epoch mtime_epoch_millis in ms
    timestamp_epoch_millis = timestamp * 1000  # epoch mtime_epoch_millis in ms
    timestamp_human = datetime.fromtimestamp(timestamp)  # human readable local mtime_epoch_millis
    return timestamp_epoch_millis, timestamp_human


def get_mtime(path):
    mtime_epoch = os.path.getmtime(path)  # epoch mtime_epoch_millis in ms
    mtime_epoch_millis = mtime_epoch * 1000  # epoch mtime_epoch_millis in ms
    mtime_human = datetime.fromtimestamp(mtime_epoch)  # mtime in human readable local mtime_epoch_millis
    return mtime_epoch_millis, mtime_human
