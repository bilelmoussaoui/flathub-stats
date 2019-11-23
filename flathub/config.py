from datetime import date, timedelta
from pathlib import Path
import os
import logging
import logzero
# We don't have any date before
DEBUG = True
DATABASE_PATH = 'flathub.db'

START_DATE = date(2018, 4, 29)
# Dates that are not available somehow
MISSING_DATES = [
    date(2018, 6, 19),
    date(2018, 11, 20),
    date(2018, 11, 21),
    date(2018, 11, 22),
    date(2018, 11, 23),
    date(2018, 11, 24),
    date(2018, 11, 25),
    date(2018, 11, 26),
    date(2018, 11, 27),
    date(2018, 12, 9),
    date(2018, 12, 10),
]
BASE_URI = 'https://flathub.org/stats'
CACHE_DIR = Path(os.environ.get('FLATHUB_STATS_CACHE',
                                os.path.join(os.path.dirname(
                                    os.path.realpath(__file__)), 'cache')
                                ))


log_format = '%(color)s[%(levelname)1.1s %(asctime)s %(module)s:%(lineno)d]%(end_color)s %(message)s'
formatter = logzero.LogFormatter(fmt=log_format)
logger = logzero.setup_logger(name="flathub", level=logging.DEBUG,
                              formatter=formatter)
