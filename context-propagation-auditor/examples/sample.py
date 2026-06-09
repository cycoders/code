import asyncio

async def worker():
    await asyncio.sleep(1)

asyncio.create_task(worker())  # flagged