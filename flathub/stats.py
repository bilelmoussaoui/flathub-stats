from datetime import date, timedelta
from functools import namedtuple
import datetime
from pathlib import Path
import requests
import json
import os
import logging
import sys
import multiprocessing
import sqlite3

from config import START_DATE, MISSING_DATES, BASE_URI, CACHE_DIR, DATABASE_PATH, logger
from models import ApplicationHistory, Application


def iter_to_date(start_date: datetime.date, end_date: datetime.date):
    delta = datetime.timedelta(days=1)
    while start_date <= end_date:
        yield start_date
        start_date += delta


def get_cache_path(date: datetime.date) -> Path:
    cache_file = f'{date.year}-{date.month:02d}-{date.day:02d}.json'
    cache_path = CACHE_DIR.joinpath(cache_file)
    return cache_path


def cache_downloads_stats(date: datetime.date):
    cache_path = get_cache_path(date)
    if not cache_path.exists():
        endpoint = f'{BASE_URI}/{date.year}/{date.month:02d}/{date.day:02d}.json'
        res = requests.get(endpoint)

        if res.status_code == 200 and res.headers.get('Content-Type') == 'application/json':
            logger.debug(f"Fetching {endpoint}")

            data = res.json()

            with open(cache_path, 'w') as handle:
                json.dump(data, handle, indent=2)
        else:
            logger.error(f"Failed to download {endpoint}")


def download_cache(start_date: datetime.date, end_date: datetime.date):
    if not CACHE_DIR.exists():
        CACHE_DIR.mkdir()

    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    pool.map(cache_downloads_stats, iter_to_date(start_date, end_date))
    pool.close()


def parse_cache_of_date(date: datetime.date) -> [ApplicationHistory]:
    history = []
    cache_path = get_cache_path(date)

    with open(cache_path, 'r') as handle:
        refs = json.load(handle)['refs']

        for app_id, downloads_per_arch in refs.items():

            downloads = 0
            updates = 0
            for stats in downloads_per_arch.values():
                downloads += stats[0]
                updates += stats[1]

            history.append(ApplicationHistory(
                app_id, date, downloads, updates))

    return history


if __name__ == '__main__':

    today = datetime.date.today()
    end_date = datetime.date(today.year, today.month, today.day)

    applications = {}

    for date in iter_to_date(START_DATE, end_date):
        if date in MISSING_DATES:
            continue
        try:
            date_history = parse_cache_of_date(date)
            for app_history in date_history:
                app_id = app_history.app_id
                application = applications.get(app_id, Application(app_id))
                application.add_history(app_history)
                applications[app_history.app_id] = application
        except FileNotFoundError:
            logger.error(f'Failed to find cache file {date}')

    connection = sqlite3.connect(DATABASE_PATH)

    for app in applications.values():
        cursor = connection.cursor()
        app.save(cursor)
    connection.commit()
