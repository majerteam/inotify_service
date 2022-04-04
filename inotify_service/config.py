from asyncio import subprocess, create_subprocess_shell
from asyncinotify import Event
from typing import Generator
import logging
import os
from dataclasses import dataclass
from functools import reduce
from operator import or_
from pathlib import Path
from typing import List

import yaml
from asyncinotify import Mask

logger = logging.getLogger(__name__)
ENV_KEY: str = "INOTIFY_SERVICE_PATH"


async def subprocess_run(cmd: str):
    proc = await create_subprocess_shell(
        cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE
    )

    stdout, stderr = await proc.communicate()

    print(f"[{cmd!r} exited with {proc.returncode}]")
    if stdout:
        print(f"[stdout]\n{stdout.decode()}")
    if stderr:
        print(f"[stderr]\n{stderr.decode()}")


def get_config_path(path="/etc/inotify_service/conf.d") -> Path:
    """Return the path where the configuration files belong"""
    if ENV_KEY in os.environ:
        path = os.environ[ENV_KEY]

    if not os.path.isdir(path):
        raise Exception(f"Path {path} doesn't exist on disk")
    return Path(path)


@dataclass
class ConfigObject:
    """
    In [2]: from inotify_service import config

    In [3]: c = config.ConfigObject(script="echo", events=["MODIFY", "CREATE"], directory="/tmp")

    In [4]: c.inotify_events
    Out[4]: <Mask.CREATE|MODIFY: 258>
    """

    script: str
    events: List[str]
    directory: Path

    def __post_init__(self):
        if not isinstance(self.directory, Path):
            self.directory = Path(self.directory)

    @property
    def inotify_events(self) -> Mask:
        res = []
        for event in self.events:
            mask = getattr(Mask, event)
            if mask is None:
                raise Exception(f"Configurtion Error unknown mask {event}")
            res.append(mask)
        return reduce(or_, res)


@dataclass
class Command:
    """
    Command manager used to handle command line generation based on parameters
    """

    script: str

    def format_command(self, **options) -> str:
        return self.script.format(**options)


@dataclass
class ActionRunner:
    """
    Tools used to manage system commands
    """

    command: Command

    def __post_init(self):
        if not isinstance(self.command, Command):
            self.command = Command(script=self.command)

    async def run(self, **parameters):
        command_line = self.command.format_command(**parameters)
        print(f"Running {command_line}")
        out = await subprocess_run(command_line)
        print(out)


class InstanceRegistry:
    configs: List[ConfigObject] = []

    def add(self, obj: ConfigObject):
        self.configs.append(obj)

    async def handle_event(self, event: Event):
        print(f"Handling event on path {event.path}")
        config = self._find_config_by_path(event.path)
        if config is None:
            logger.debug("Unknown config path")
            return
        command: Command = Command(config.script)
        await ActionRunner(command).run(path=event.path, name=event.name)

    def _find_config_by_path(self, path: Path) -> ConfigObject:
        """Find a config by its path on disk"""
        result = None
        logger.debug(f"Find config by path {path}")
        for obj in self.configs:
            if obj.directory == path.parent:
                result = obj
        return result


def build_config_objects(config: list) -> Generator[ConfigObject, None, None]:
    """
    Build config objects based on the given configuration
    """
    for element in config:
        yield ConfigObject(**element)


def load_files(path: str) -> List[dict]:
    """
    Load configuration files from the given path and merge configuration objets
    """
    result = []
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
            result.extend(config_list)

        return result


def build_registry() -> List[ConfigObject]:
    registry = InstanceRegistry()
    path: Path = get_config_path()
    config = load_files(path)

    for config_object in build_config_objects(config):
        registry.add(config_object)
    return registry
