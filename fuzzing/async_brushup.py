import asyncio


sem = asyncio.Semaphore(5)

async def CookToast(num):
    async with sem: 
        print(f"Making toast #{num}")
        await asyncio.sleep(5)
        print(f"Toast #{num} is completed!")

async def main():
    i = 1
    async with asyncio.TaskGroup() as tg:
        while i < 10:
            tg.create_task(CookToast(i))
            i += 1

if __name__ == "__main__":
    asyncio.run(main())