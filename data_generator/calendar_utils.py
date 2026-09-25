"""Workday helpers shared by the generators (SK/CZ holidays from config)."""
from datetime import date, timedelta

import config


def is_workday(d: date, country: str) -> bool:
    """True for Monday-Friday dates that are not public holidays."""
    return d.weekday() < 5 and d not in config.HOLIDAYS[country]


def next_workday(d: date, country: str) -> date:
    """Return d itself if it is a workday, otherwise the next workday."""
    while not is_workday(d, country):
        d += timedelta(days=1)
    return d


def add_workdays(d: date, n: int, country: str) -> date:
    """Move n workdays forward from d (n=0 returns d unchanged)."""
    while n > 0:
        d += timedelta(days=1)
        if is_workday(d, country):
            n -= 1
    return d


def workdays(start: date, end: date, country: str) -> list[date]:
    """All workdays in [start, end]."""
    days, d = [], start
    while d <= end:
        if is_workday(d, country):
            days.append(d)
        d += timedelta(days=1)
    return days
