import logging
import logging.config
import yaml
from pathlib import Path
from .config import get_settings

def setup_logging():
    settings = get_settings()
    
    # Default logging configuration
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            },
            'json': {
                'format': '%(asctime)s %(levelname)s %(name)s %(message)s',
                'class': 'pythonjsonlogger.jsonlogger.JsonFormatter'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'standard',
                'level': 'INFO'
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': 'logs/app.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
                'formatter': 'json',
                'level': 'INFO'
            }
        },
        'loggers': {
            '': {  # Root logger
                'handlers': ['console', 'file'],
                'level': 'INFO',
                'propagate': True
            },
            'uvicorn': {
                'handlers': ['console', 'file'],
                'level': 'INFO',
                'propagate': False
            },
            'fastapi': {
                'handlers': ['console', 'file'],
                'level': 'INFO',
                'propagate': False
            }
        }
    }

    # Create logs directory if it doesn't exist
    Path('logs').mkdir(exist_ok=True)

    # Try to load custom logging config from file
    config_path = Path('config/logging.yaml')
    if config_path.exists():
        with open(config_path) as f:
            try:
                logging_config = yaml.safe_load(f)
            except Exception as e:
                print(f"Error loading logging config: {e}")

    # Apply configuration
    logging.config.dictConfig(logging_config)

    # Return root logger
    return logging.getLogger()