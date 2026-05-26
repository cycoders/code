import asyncio
import time

async def bad():
    time.sleep(1)  # detected

async def good():
    await asyncio.sleep(1)