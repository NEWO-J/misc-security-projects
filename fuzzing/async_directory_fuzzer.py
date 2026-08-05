import asyncio
import time
import httpx
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-u','--url',help="Target URL", required=True)
parser.add_argument('-w','--wordlist',help="Wordlist", required=True)

args = parser.parse_args()
url = args.url
wordlist = args.wordlist

semaphore = asyncio.Semaphore(10)

async def dfuzz(client, url, directory):
    async with semaphore:
        req = await client.get(url + '/' + directory, timeout=50)
        if req.status_code == 200:
            print(f"[+] Directory found! {directory}") 

           

async def main():
    with open(wordlist) as w:
        lines = [line.strip() for line in w if line.strip()]


    async with httpx.AsyncClient() as client:
        async with asyncio.TaskGroup() as tg:
            for line in lines:
                tg.create_task(dfuzz(client, url, line))
try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Stopping..")
    exit()