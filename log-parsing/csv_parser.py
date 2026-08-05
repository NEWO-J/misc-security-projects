import pandas
import re

def main():

    with open('mylogs.csv') as f:
        result = pandas.read_csv(f)
        r = re.compile(".+19:12Z$")

        for timestamp in result['timestamp']:
            if re.search(r, timestamp):
                print(timestamp)

        lowest_ms = float('inf')
        for ms in result['response_time_ms']:
            if ms < lowest_ms:
                lowest_ms = ms
        print(f"Lowest ms speed: {ms}")

main()