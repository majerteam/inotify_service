import asyncio

from inotify_service.log import setup_logger


def run():
    setup_logger()

    from inotify_service.service import build_service

    service = build_service()
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(service.run())
    except KeyboardInterrupt:
        print("shutting down")
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()


if __name__ == "__main__":
    run()
