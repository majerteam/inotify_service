"""
Logging management in inotify_service
"""
import logging.config
import os
from pathlib import Path

ENV_KEY: str = "INOTIFY_SERVICE_LOG_CONFIG"


def get_log_config_path(path: str = None) -> Path:
    """Return the path where the configuration files belong"""
    if ENV_KEY in os.environ:
        path = os.environ[ENV_KEY]
    elif path is None:
        raise Exception("get_log_config_path should be called with a path argument")
    path = Path(path).absolute()
    if not path.is_file():
        raise Exception(f"Path {path} doesn't exist on disk")
    return path


def get_logger():
    return logging.getLogger("inotify_service")


def setup_logger(path: str = "/etc/inotify_service/log.conf"):
    config_file = get_log_config_path(path)
    logging.config.fileConfig(config_file)
