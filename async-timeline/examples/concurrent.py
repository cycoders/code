import asyncio
import random


async def worker(i: int):
    """Short worker tasks to demo concurrency peak."""
    await asyncio.sleep(random.uniform(0.01, 0.1))
    return i


async def main():
    """Spawn 50 concurrent workers."""
    tasks = [asyncio.create_task(worker(i)) for i in range(50)]
    results = await asyncio.gather(*tasks)
    print(f"Completed {len(results)} workers")


if __name__ == "__main__":
    asyncio.run(main())
