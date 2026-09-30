from neo4j import GraphDatabase

URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "neo4j")

with open("auth_logs.txt") as f:
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        for line in f:
            create_query = """
            MERGE (p:Person {name: $person_name})
            MERGE (h:Host {ip })

            """