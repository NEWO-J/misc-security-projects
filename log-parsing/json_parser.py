import json
import re

def main():
    with open("mylogs.json") as f:
        for line in f:
            jsonified = json.loads(line)
            print(jsonified['timestamp'])
            rx = re.compile(r".+40.18.102$")
            if re.search(rx, jsonified['timestamp']):
                print(jsonified['message'])


main()