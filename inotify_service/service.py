from asyncio import Event
import logging
from typing import List
from asyncinotify import Inotify
from pathlib import Path
from inotify_service.handler import InotifyHandler, load_handlers
from inotify_service.command import Command, ActionRunner

logger = logging.getLogger(__name__)


class InotifyService:
    handlers: List[InotifyHandler] = []

    def register(self, obj: InotifyHandler):
        self.handlers.append(obj)

    async def handle_event(self, event: Event):
        logger.debug(f" + Handling event on path {event.path}")
        handler = self._find_handler_by_path(event.path)
        if handler is None:
            logger.debug("  -> File not handled")
            return
        command: Command = Command(handler.script)
        await ActionRunner(command).run(path=event.path, name=event.name)

    def _find_handler_by_path(self, path: Path) -> InotifyHandler:
        """Find a handler by its path on disk"""
        result = None
        logger.debug(f"Find handler by path {path}")
        for obj in self.handlers:
            if obj.match(path):
                result = obj
        return result

    async def run(self):
        # Context manager to close the inotify handle after use
        with Inotify() as inotify:
            # Adding the watch can also be done outside of the context manager.
            # __enter__ doesn't actually do anything except return self.
            # This returns an asyncinotify.inotify.Watch instance
            for obj in self.handlers:
                logger.info(f"Adding watch on {obj.directory}")
                inotify.add_watch(obj.directory, obj.inotify_events)
            # Iterate events forever, yielding them one at a time
            async for event in inotify:
                logger.debug("Event fired")
                # Events have a helpful __repr__.  They also have a reference to
                # their Watch instance.
                await self.handle_event(event)


def build_service() -> InotifyService:
    service = InotifyService()
    for handler_object in load_handlers():
        service.register(handler_object)
    return service
