from mdc import MDCHandler
from common.logging.home_pulse_formatter import HomePulseFormatter
CONTEXT_FIELDS = ['domain', 'subdomain', 'flag', 'information', 'timing', 'methodOutput', 'request']


class HomePulseHandler(MDCHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        formatter = HomePulseFormatter(extra=CONTEXT_FIELDS)
        self.setFormatter(formatter)
