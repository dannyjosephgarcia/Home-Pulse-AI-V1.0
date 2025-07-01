import json
import logging
import collections
from flask import request
from datetime import datetime


DEFAULT_DATE_FORMAT = "%Y-%m-%d %I:%M:%S %p"


class HomePulseFormatter(logging.Formatter):
    def __init__(self, fmt=None, date_fmt=None, extra=None, **kwargs):
        """
        Extension of the Formatter class from the logging library to customize my app logs
        :param format: The format the logs will take (level names, messages, etc...)
        :param date_fmt: The format of the date displayed in the logs
        :param extra: Any extra context fields
        :param kwargs: Co-arguments
        """
        super().__init__(fmt=fmt, datefmt=date_fmt or DEFAULT_DATE_FORMAT, **kwargs)
        self._extra = extra or dict()

    def _get_extra_fields(self, record):
        return {
            f: getattr(record, f) for f in self._extra if hasattr(record, f)
        }

    @staticmethod
    def _get_mdc_fields():
        """
        Used in tandem with the mdc decorator
        :return: python dictionary
        """
        result = collections.defaultdict()
        if getattr(logging, '_mdc'):
            for c in (vars(ctx) for ctx in vars(getattr(logging, '_mdc')).values()):
                result.update(c)
        return result

    def format(self, record):
        """
        Overrides the format method of the Formatter class to surface a custom log output
        :param record: The log record to be surfaces
        :return: json, the output
        """
        try:
            message = record.getMessage()
        except Exception:
            message = str(record.msg)
        log_record = {
            "timestamp": datetime.utcfromtimestamp(record.created).__format__(self.datefmt),
            "level": record.levelname,
            "location": f"{record.module}.{record.funcName}:{record.lineno}",
            "message": message
        }
        log_record.update(self._get_mdc_fields())
        log_record.update(self._get_extra_fields(record))
        if "flag" not in log_record.keys():
            log_record.update(flag="General Information")
        if record.exc_info:
            log_record.update(exception=dict(
                name=record.exc_info[0].__name__,
                stacktrace=self.formatException(record.exc_info)
            ))
        return json.dumps(log_record, default=str)
