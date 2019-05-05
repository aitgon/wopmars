import time

import os

# get unix time in ms
time_unix_ms = lambda: time.time() * 1000  #  unix time in ms

# get path modification time in ms
os_path_getmtime_ms = lambda path: os.path.getmtime(path)*1000
