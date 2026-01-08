import asyncio
import time


async def blocking_task():
    """Simulates blocking IO in async context."""
    print("Starting blocking_task")
    await asyncio.sleep(0.1)
    print("Entering BLOCKING sleep")
    time.sleep(1.0)  # <-- Visible as long task duration
    await asyncio.sleep(0.1)
    print("Blocking task done")


async def quick_task():
    await asyncio.sleep(0.2)


async def main():
    print("Launching tasks")
    await asyncio.gather(blocking_task(), quick_task())


if __name__ == "__main__":
    asyncio.run(main())