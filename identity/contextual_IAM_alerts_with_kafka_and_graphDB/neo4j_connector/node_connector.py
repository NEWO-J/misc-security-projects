from kafka import KafkaConsumer
import json
from neo4j import GraphDatabase
import sys
import time
import collections
import datetime

consumer = KafkaConsumer(
    "incident-logs",
    bootstrap_servers=['kafka:9092'],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    api_version=(2, 8, 0),
    group_id='neo4j_connectorv6',
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    key_deserializer=lambda k: k.decode('utf-8') if k else None
)

query = """
        MERGE (i:Incident {incident_id: $id, incident_date: $ts})
        SET i += $details
        MERGE (u:User {username: $username})
        MERGE (s:Service {service: $service})
        MERGE (h:Host {ip: $ip})
        MERGE (i)-[:INCIDENT]->(u)
        MERGE (h)-[:FROM_HOST]->(u)
        MERGE (u)-[:ACCESSING_SERVICE]->(s)
        """

spray_query = """
        MERGE (i:Incident {incident_id: $id, incident_date: $ts})
        SET i += $details
        MERGE (h:Host {ip: $ip})
        MERGE (s:Service {service: $service})
        WITH i, h, s
        UNWIND $usernames AS username
        MERGE (u:User {username: username})
        MERGE (i)-[:INCIDENT]->(u)
        MERGE (h)-[:FROM_HOST]->(u)
        MERGE (u)-[:ACCESSING_SERVICE]->(s)
        """

time.sleep(50)

while True:
    try:
        driver = GraphDatabase.driver("neo4j://neo-4j:7687", auth=('neo4j', 'neo4jneo4j'))
        driver.verify_connectivity()
        print("Successfully connected to NEO4J")
        break
    except:
        print("NEO4J is unresponsive, retrying..")
        time.sleep(3)


for message in consumer:
    print(f"Received -> Key: {message.key} | Value: {message.value}", flush=True)
    sys.stdout.flush()

    details = {"source_ip": message.value["ip"]}
    if "login_attempts" in message.value:
        details["login_attempts"] = message.value["login_attempts"]
    if "affected_users" in message.value:
        details["affected_users"] = message.value["affected_users"]
    if "affected_users_count" in message.value:
        details["affected_users_count"] = message.value["affected_users_count"]
    if "successful_logins" in message.value:
        details["successful_logins"] = message.value["successful_logins"]
    if message.value.get("tor_exit"):
        details["tor_exit"] = True

    usernames = [name.strip() for name in message.value.get("affected_users", "").split(",") if name.strip()]

    try:
        if usernames:
            driver.execute_query(
                spray_query,
                usernames=usernames,
                service=message.value["service"],
                ip=message.value["ip"],
                ts=message.value["incident_date"],
                id=message.value["incident_id"],
                details=details,
                database_="neo4j")
        else:
            driver.execute_query(
                query,
                username=message.key,
                service=message.value["service"],
                ip=message.value["ip"],
                ts=message.value["incident_date"],
                id=message.value["incident_id"],
                details=details,
                database_="neo4j")

        print(f"Successfully wrote! Nodes created")
    except Exception as error:
        print(f"Neo4j error: {error}")



