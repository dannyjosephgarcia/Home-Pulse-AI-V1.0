class LoggingCFG:
    def __init__(self, cfg):
        self.cfg = cfg


cfg = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'backend.common.logging.home_pulse_handler.HomePulseHandler'
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console']
    },
    'loggers': {
        'gunicorn.access': {
            'propagate': True
        },
        'gunicorn.error': {
            'propagate': True
        },
        'werkzeug': {
            'level': 'WARNING',
            'propagate': False,
            'handlers': ['console'],
        },
        'waitress': {
            'level': 'WARNING',
            'propagate': False,
            'handlers': ['console'],
        },
    }
}

logging_cfg = LoggingCFG(cfg=cfg)
