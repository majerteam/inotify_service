import os
from pathlib import Path

from asyncinotify import Inotify
import asyncio

from inotify_service.config import InstanceRegistry, build_registry


async def main_task(registry: InstanceRegistry):
    # Context manager to close the inotify handle after use
    with Inotify() as inotify:
        # Adding the watch can also be done outside of the context manager.
        # __enter__ doesn't actually do anything except return self.
        # This returns an asyncinotify.inotify.Watch instance
        for obj in registry.configs:
            print(f"Adding watch on {obj.directory}")
            inotify.add_watch(obj.directory, obj.inotify_events)
        # Iterate events forever, yielding them one at a time
        async for event in inotify:
            print("Event fired")
            # Events have a helpful __repr__.  They also have a reference to
            # their Watch instance.
            await registry.handle_event(event)


def run():
    registry = build_registry()
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main_task(registry))
    except KeyboardInterrupt:
        print("shutting down")
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()


if __name__ == "__main__":
    run()
