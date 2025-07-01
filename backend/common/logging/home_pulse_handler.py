import sys
import logging
from home_pulse_formatter import HomePulseFormatter
CONTEXT_FIELDS = ['domain', 'subdomain', 'flag', 'information', 'timing', 'methodOutput', 'request']


class HomePulseHandler(logging.StreamHandler):
    def __init__(self, stream=None, extra_fields=None):
        stream = stream or sys.stdout
        super().__init__(stream=stream)

        formatter = HomePulseFormatter(extra=extra_fields or {})
        self.setFormatter(formatter)
