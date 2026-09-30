import collections
import re
import datetime

window = []
tsre = re.compile(r"[0-9]+-[0-9]+-[0-9]+T[0-9]+:[0-9]+:[0-9]+\.[0-9]+Z")
ipre = re.compile(r"[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+")
message = re.compile(r"status=4[0-9]+")

ipmap = collections.defaultdict(collections.deque)

with open("log.txt") as f:
    for line in f:
        ts = re.search(tsre, line)
        ip = re.search(ipre, line)
        status = re.search(message, line)
        if status and ts and ip:
                timestamp = datetime.datetime.fromisoformat(ts.group(0))
                ip = ip.group(0)
                
                while ipmap[ip] and (timestamp - ipmap[ip][0]).total_seconds() > 10:
                    ipmap[ip].popleft()
                    
                ipmap[ip].append(timestamp)
                if len(ipmap[ip]) >= 3:
                    print(f"Brute force detected: {ip}")
            
        

    

