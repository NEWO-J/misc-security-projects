import asyncio

sem = asyncio.Semaphore(3)

async def testfunc(batchnum):

    async with sem:
        print(f"Starting batch {batchnum}")
        await asyncio.sleep(10)

        print("Completed!")


async def main():

    async with asyncio.TaskGroup() as tg:
        for i in range(0, 10):
            tg.create_task(testfunc(i))
        print("hello")

asyncio.run(main())