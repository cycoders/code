from graceful_shutdown import ShutdownManager
import asyncio

async def main():
    mgr = ShutdownManager(timeout=5.0)
    with mgr():
        while not mgr.cancelled:
            await asyncio.sleep(0.5)

if __name__ == "__main__":
    asyncio.run(main())