from kafka import KafkaConsumer, KafkaProducer
import json
import sys
import time
import collections
from datetime import datetime
import requests

consumer = KafkaConsumer(
    "auth-logs",
    bootstrap_servers=['kafka:9092'],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    api_version=(2, 8, 0),
    group_id='neo4j_connector_authlogs',
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    key_deserializer=lambda k: k.decode('utf-8') if k else None
)

producer = KafkaProducer(
    bootstrap_servers=['kafka:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    key_serializer=lambda k: k.encode('utf-8'),
    request_timeout_ms=30000
)

window = collections.deque()
WINDOW_DURATION = 60
SPRAY_THRESHOLD = 2
frequency = {}
checkedips = {}
sprayalerted = set()

for message in consumer:

    while window and (datetime.now() - datetime.strptime(window[0][0], "%Y-%m-%dT%H:%M:%S")).total_seconds() > WINDOW_DURATION:
        removed = window.popleft()
        user = removed[1]
        status_code = removed[2]
        if status_code not in frequency[user]:
            continue
        elif frequency[user][status_code] - 1 == 0:
            del frequency[user][status_code]
        else:
            frequency[user][status_code] -= 1

    window.append((message.value["ts"], message.key, message.value["status"]))
    if message.key not in frequency:
        frequency[message.key] = {message.value["status"]: 1}
    elif message.value["status"] not in frequency[message.key]:
        frequency[message.key][message.value["status"]] = 1
    else:
        frequency[message.key][message.value["status"]] += 1

    if "5512" in frequency[message.key]:
        if frequency[message.key]["5512"] >= 5:
            print("Brute force detected: Error code #5512 exceeded 5 tries in 60 seconds.")

            freq = frequency[message.key]["5512"]
            del frequency[message.key]["5512"]

            print(freq)
            producer.send("incident-logs", 
                        key=message.key, 
                        value=
                        {"incident_id": 1010,
                            "ip": message.value["ip"],
                            "service": message.value["service"], 
                            "incident_date": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"), 
                            "login_attempts": freq})

    if message.value["ip"] not in checkedips:
        checkedips[message.value["ip"]] = collections.defaultdict(int)
    if message.key not in checkedips[message.value["ip"]]:
        r = requests.get(f'https://api.globus.studio/v2/tor?ip={message.value["ip"]}')
        result = json.loads(r.text)
        if result["is_tor"]:
            producer.send("incident-logs",
                        key=message.key,
                        value=
                        {"incident_id": 1011,
                            "ip": message.value["ip"],
                            "service": message.value["service"],
                            "incident_date": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                            "tor_exit": True,
                        })

        # set to 0 if failed login
        if message.value["status"] == "5512":
            checkedips[message.value["ip"]][message.key] = 0


    sprayed = checkedips[message.value["ip"]]
    if message.value["status"] == "5513":
        checkedips[message.value["ip"]][message.key] += 1
    if len(sprayed) > SPRAY_THRESHOLD and message.value["ip"] not in sprayalerted:
        sprayalerted.add(message.value["ip"])
        print(f"Password spray detected: {message.value['ip']} failed against {len(sprayed)} accounts.", flush=True)

        ip_key = message.value["ip"]

        total_successful_logins = sum(checkedips.get(ip_key, {}).values())

        producer.send("incident-logs",
                        key=message.value["ip"],
                        value=
                        {"incident_id": 1012,
                        "ip": message.value["ip"],
                        "service": message.value["service"],
                        "incident_date": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                        "affected_users": ", ".join(sorted(sprayed)),
                        "affected_users_count": len(sprayed),
                        "successful_logins": total_successful_logins,
                        })
        

        


            