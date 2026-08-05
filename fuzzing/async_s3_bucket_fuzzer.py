import asyncio
import httpx
import argparse
import re
import sys

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

sem = asyncio.Semaphore(10)
regex = re.compile(r'^(?!(^xn--|.+-s3alias$))^[a-z0-9][a-z0-9-.]{1,61}[a-z0-9]$')
regex2 = re.compile(r'<Message>.+?</Message>')

async def test_bucket(client, queue):
    while True:
        word = await queue.get()
        try:
            if re.match(regex, word):
                url = "https://"+word+".s3.amazonaws.com"
                async with sem:
                    try:
                        r = await client.get(url, timeout=3)
                        if "<Code>AccessDenied</Code" not in r.text and \
                        "location constraint is incompatible for the region specific endpoint this request was sent to.</Message>" not in r.text and \
                        "The specified bucket does not exist" not in r.text:
                            msg_match = re.search(regex2, r.text)
                            if msg_match:
                                msg = msg_match.group(0).replace("<Message>", "").replace("</Message>", "")
                            else:
                                msg = "N/A"
                            print(f"[+] Success: {word} | Message: {msg}")
                    except (httpx.RequestError, httpx.TimeoutException):
                        pass
        finally:
             queue.task_done()
        

            

async def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-w','--wordlist',help="wordlist for fuzzing",required=True)
    args = parser.parse_args()
    wordlist = args.wordlist

    queue = asyncio.Queue()

    with open(wordlist) as w:
            lines = [line.strip() for line in w if line.strip()]

 
    for line in lines:
        if not line.replace("/", " ").isalnum():
                continue
        await queue.put(line)

    limits = httpx.Limits(max_keepalive_connections=20, max_connections=50)

    async with httpx.AsyncClient(limits=limits) as client:          
        workers = [asyncio.create_task(test_bucket(client, queue)) for _ in range(50)]

        await queue.join()

        for w in workers:
             w.cancel()



asyncio.run(main())

