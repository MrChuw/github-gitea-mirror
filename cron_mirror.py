#!/usr/bin/env python3
import os
import time
from datetime import datetime, timedelta

from loguru import logger

from __init__ import main

DELTA = timedelta(hours=6)
HOME_DIR = "./"
LOG_DIR = os.path.join(HOME_DIR, "mirrorLogs")
LOG_FILE = os.path.join(LOG_DIR, time.strftime("%Y-%m-%d-%H-%M-%S") + ".log")
logger.add(LOG_FILE, compression="xz", rotation="00:00")

while True:
    os.makedirs(LOG_DIR, exist_ok=True)
    logger.info(f"Starting: {datetime.now()}")
    main()
    logger.info(f"Next Cycle: {datetime.now() + DELTA}")
    time.sleep(DELTA.total_seconds())
