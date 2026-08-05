import re
import collections

def parse_log():
    hmap = {}
    x = re.compile(r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)")
    y = re.compile(r"[0-9][0-9]:[0-9][0-9]:[0-9][0-9] ")
    z = re.compile(r"401 [0-9][0-9][0-9]$")

    with open('access.log') as f:
        for line in f:
            ip_match = re.search(x, line)
            ts_match = re.search(y, line)
            sc_match = re.search(z, line)
            if ip_match and ts_match and sc_match:
                ip = ip_match.group()
                ts = ts_match.group().strip()

                ts = ts.split(":")
                ts_seconds = ((int(ts[0]) * 3600) + (int(ts[1]) * 60) + int(ts[2]))

                if ip in hmap:
                    hmap[ip][0].append(ts_seconds)
                else:
                    hmap[ip] = [collections.deque([ts_seconds]), 0]

                while ts_seconds - hmap[ip][0][0] > 600:
                    hmap[ip][0].popleft()

                hmap[ip][1] = max(hmap[ip][1], len(hmap[ip][0]))

    for ip,seen in hmap.items():
        print(f"IP {ip} was seen with a 401 error a maximum of {seen[1]} time(s) in a 10 minute window.")

parse_log()