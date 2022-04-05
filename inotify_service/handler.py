import logging
import os
import re

from dataclasses import dataclass
from functools import reduce
from operator import or_
from pathlib import Path
from typing import Generator, List, Pattern

import yaml
from asyncinotify import Mask

logger = logging.getLogger("inotify_service")
ENV_KEY: str = "INOTIFY_SERVICE_PATH"


def get_handler_config_path(path="/etc/inotify_service/conf.d") -> Path:
    """Return the path where the configuration files belong"""
    if ENV_KEY in os.environ:
        path = os.environ[ENV_KEY]
    path = Path(path).absolute()
    if not path.is_dir():
        raise Exception(f"Path {path} doesn't exist on disk or is not a directory")
    return path


@dataclass
class InotifyHandler:
    """
    In [2]: from inotify_service import config

    In [3]: c = config.InotifyHandler(script="echo", events=["MODIFY", "CREATE"], directory="/tmp")

    In [4]: c.inotify_events
    Out[4]: <Mask.CREATE|MODIFY: 258>
    """

    script: str
    events: List[str]
    directory: Path
    pattern: Pattern = None

    def __post_init__(self):
        if not isinstance(self.directory, Path):
            self.directory = Path(self.directory)

        if isinstance(self.pattern, (str, bytes)):
            self.pattern = re.compile(self.pattern)

    @property
    def inotify_events(self) -> Mask:
        res = []
        for event in self.events:
            mask = getattr(Mask, event)
            if mask is None:
                raise Exception(f"Configurtion Error unknown mask {event}")
            res.append(mask)
        return reduce(or_, res)

    def match(self, filepath: Path) -> bool:
        """
        Check if this config object should handle the given filepath
        """
        if self.directory != filepath.parent:
            return False

        if self.pattern is not None:
            if not self.pattern.match(filepath.name):
                return False
        return True


def load_handlers_configurations(path: str) -> Generator[dict, None, None]:
    """
    build a list with the handlers configurations found in the given path
    """
    filepath: Path
    for filepath in path.glob("*.yaml"):
        try:
            config_list = yaml.safe_load(filepath.read_bytes())
            if not isinstance(config_list, list):
                raise Exception(
                    "The file isn't in the right format (expected a list of dicts)"
                )
        except Exception:
            logger.exception(f"Error reading yaml file {filepath}")
        finally:
            for element in config_list:
                yield element


def build_handlers(config: list) -> Generator[InotifyHandler, None, None]:
    """
    Build Handlers based on the given configuration data
    """
    for element in config:
        yield InotifyHandler(**element)


def load_handlers() -> List[InotifyHandler]:
    """
    Load configuration and build the Handler objects
    """
    path: Path = get_handler_config_path()
    config = load_handlers_configurations(path)
    return build_handlers(config)
