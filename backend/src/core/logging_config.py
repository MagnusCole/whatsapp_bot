import logging.config
import yaml
from pathlib import Path
from typing import Dict, Any

def setup_logging(config_path: Path = None, default_level: int = logging.INFO) -> None:
    """Setup logging configuration

    Args:
        config_path (Path): Path to the logging configuration file
        default_level (int): Default logging level if config file is not found
    """
    if config_path and config_path.exists():
        with open(config_path, 'rt') as f:
            try:
                config = yaml.safe_load(f.read())
                logging.config.dictConfig(config)
            except Exception as e:
                print(f'Error loading logging configuration: {e}')
                setup_default_logging(default_level)
    else:
        setup_default_logging(default_level)

def setup_default_logging(level: int = logging.INFO) -> None:
    """Setup default logging configuration

    Args:
        level (int): Logging level
    """
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'json': {
                'format': '%(asctime)s %(levelname)s %(name)s %(message)s',
                'class': 'pythonjsonlogger.jsonlogger.JsonFormatter',
                'json_ensure_ascii': False
            },
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            },
            'detailed': {
                'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'INFO',
                'formatter': 'standard',
                'stream': 'ext://sys.stdout'
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'DEBUG',
                'formatter': 'detailed',
                'filename': 'logs/app.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5
            },
            'error_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'ERROR',
                'formatter': 'detailed',
                'filename': 'logs/error.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5
            }
        },
        'loggers': {
            '': {  # root logger
                'handlers': ['console', 'file', 'error_file'],
                'level': level,
                'propagate': True
            }
        }
    }
    logging.config.dictConfig(config)

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name

    Args:
        name (str): Logger name

    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(name)