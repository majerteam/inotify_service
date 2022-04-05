import logging
from dataclasses import dataclass
from asyncio import subprocess, create_subprocess_shell


logger = logging.getLogger(__name__)


async def subprocess_run(cmd: str):
    proc = await create_subprocess_shell(
        cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE
    )

    stdout, stderr = await proc.communicate()

    logger.debug(f"[{cmd!r} exited with {proc.returncode}]")

    return stdout, stderr


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
        logger.info(f"Running {command_line}")
        stdout, stderr = await subprocess_run(command_line)

        if stdout:
            logger.debug(f"[stdout]\n{stdout.decode()}")
        if stderr:
            logger.warn(f"Error running command {command_line}")
            logger.warn(f"[STDERR]\n{stderr.decode()}")
