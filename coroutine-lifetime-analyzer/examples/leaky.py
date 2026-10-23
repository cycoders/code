import asyncio

async def background():
    await asyncio.sleep(10)

async def main():
    asyncio.create_task(background())  # leaked
    await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())