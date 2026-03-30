import asyncio
import random
from aio_task_monitor import start_monitoring


async def worker(name: str):
    await asyncio.sleep(random.uniform(0.1, 1.0))
    print(f"{name} done")


async def main():
    # Spawn 20 workers
    tasks = [asyncio.create_task(worker(f"worker-{i}")) for i in range(20)]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    start_monitoring()  # TUI starts here
    asyncio.run(main())
