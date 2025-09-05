#!/usr/bin/env python3
# coding=utf-8
###############################################################################
"""
__author__ = "sunhn"

Description:
    time zone
"""

import logging

logger = logging.getLogger(__name__)

from zoneinfo import ZoneInfo
from datetime import datetime, timedelta
from config import CONFIG

DATETIME_FORMAT = CONFIG.datetime.format
DATETIME_TIMEZONE = CONFIG.datetime.timezone


class TimeZone:
    def __init__(self, tz: str = DATETIME_TIMEZONE):
        self.tz_info = ZoneInfo(tz)

    def now(self) -> datetime:
        """
        获取时区时间

        :return:
        """
        return datetime.now(self.tz_info)

    def now_str(self, format_str: str = DATETIME_FORMAT) -> str:
        """
        获取时区时间字符串

        :param format_str:
        :return:
        """
        return datetime.now(self.tz_info).strftime(format_str)

    def f_dt_str(self, dt: datetime, format_str: str = DATETIME_FORMAT) -> str:
        """
        datetime 时间转时区时间字符串
        :param dt:
        :param format_str:
        :return:
        """
        return dt.astimezone(self.tz_info).strftime(format_str)

    def f_str(self, date_str: str, format_str: str = DATETIME_FORMAT) -> datetime:
        """
        时间字符串转时区时间

        :param date_str:
        :param format_str:
        :return:
        """
        return datetime.strptime(date_str, format_str).replace(tzinfo=self.tz_info)

    def convert_datetime_timezone(date: datetime = None, from_tz: str = "UTC", to_tz: str = "Asia/Shanghai") -> datetime:
        """
        转换时区
        """
        if date is None:
            logger.info("Don't specify date, use current datetime")
            date = datetime.now(ZoneInfo("UTC"))
        else:
            logger.info(f"Use specify date: {date}")
        from_zone = ZoneInfo(from_tz)
        date = date.replace(tzinfo=from_zone)
        to_zone = ZoneInfo(to_tz)
        return date.astimezone(to_zone)

    def get_date(self, days: int = -1, format_str: str = DATETIME_FORMAT) -> str:
        target_date = datetime.now() + timedelta(days=days)
        return target_date.strftime(format_str)

    def get_current_date(self, ret: str = None):
        current_date = datetime.now().date()
        if ret == "str":
            return current_date.strftime(DATETIME_FORMAT.split(" ")[0])
        else:
            return current_date

    def get_current_time(self, ret: str = None):
        current_time = datetime.now().time()
        if ret == "str":
            return current_time.strftime(DATETIME_FORMAT.split(" ")[1])
        else:
            return current_time

    def get_current_datetime(self, ret: str = None):
        current_datetime = datetime.now()
        if ret == "str":
            return current_datetime.strftime(DATETIME_FORMAT)
        else:
            return current_datetime


timezone = TimeZone()
