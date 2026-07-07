import json
import os
from datetime import datetime

def findTime(logfile, target_ts):
    with open(logfile, "rb") as f:
        l = 0
        hops = 0
        f.seek(0, os.SEEK_END)
        file_size = f.tell()
        r = file_size - 1
        while l <= r:
            midpoint = (l + r) // 2
            f.seek(midpoint)
            # backtrack to our previous newline to find start of line.
            while f.tell() > 0:
                f.seek(-1, 1)
                current_byte = f.read(1)
                f.seek(-1, 1)
                if current_byte == b'\n':
                    print("Newline found")
                    f.seek(1, 1)
                    break

            line_start = f.tell()
            leftline = f.readline()

            if not leftline:
                break

            try:
                jsonline = json.loads(leftline.decode('utf-8').strip())
            except json.JSONDecodeError as e:
                print(e)

            date_ts = datetime.fromisoformat(jsonline["timestamp"])
            print(date_ts)
            if date_ts == target_ts:
                return line_start, hops
            elif date_ts > target_ts:
                r = midpoint - 1
            else:
                l = line_start + len(leftline)
            
            hops += 1
            

if __name__ == "__main__":
    date_str = input("Please enter desired timestamp: ")
    try: 
        target_ts = datetime.fromisoformat(date_str)
    except ValueError:
        print(f"Invalid date! please follow ISO format")
        exit()

    result, hops = findTime("mylogs.json", target_ts)
    print(f"Desired log starts at byte: {result}, found in {hops} hops.")