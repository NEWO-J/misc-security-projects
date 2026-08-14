import os
from contextlib import asynccontextmanager
from typing import Any, Optional

from fastapi import FastAPI, HTTPException, Query
from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError, ServiceUnavailable

NEO4J_URI = os.getenv("NEO4J_URI", "neo4j://neo-4j:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "neo4jneo4j")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

MIN_DEPTH = 1
MAX_DEPTH = 4

driver = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global driver
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    try:
        yield
    finally:
        driver.close()


app = FastAPI(title="Contextual IAM incident graph", lifespan=lifespan)


def run(query: str, **params: Any):
    try:
        records, _, _ = driver.execute_query(query, database_=NEO4J_DATABASE, **params)
        return records
    except ServiceUnavailable as error:
        raise HTTPException(status_code=503, detail=f"Neo4j unavailable: {error}")
    except Neo4jError as error:
        raise HTTPException(status_code=502, detail=f"Neo4j query failed: {error}")


def clean(entity) -> dict:
    out = {}
    for key, value in dict(entity).items():
        out[key] = value if isinstance(value, (str, int, float, bool, type(None))) else str(value)
    return out


def as_node(node) -> dict:
    return {
        "id": node.element_id,
        "labels": sorted(node.labels),
        "properties": clean(node),
    }


def as_edge(rel) -> Optional[dict]:
    if rel.start_node is None or rel.end_node is None:
        return None
    return {
        "id": rel.element_id,
        "type": rel.type,
        "source": rel.start_node.element_id,
        "target": rel.end_node.element_id,
        "properties": clean(rel),
    }


@app.get("/incidents")
def list_incidents(
    user: Optional[str] = Query(None, max_length=50),
    service: Optional[str] = Query(None, max_length=50),
    limit: int = Query(50, ge=1, le=200),


):
    query = """
        MATCH (i:Incident)
        OPTIONAL MATCH (i)-[:INCIDENT]->(u:User)
        OPTIONAL MATCH (u)-[:ACCESSING_SERVICE]->(s:Service)
        OPTIONAL MATCH (h:Host)-[:FROM_HOST]->(u)
        WITH i,
             collect(DISTINCT u.username) AS users,
             collect(DISTINCT s.service) AS services,
             collect(DISTINCT h.ip) AS hosts
        WHERE ($user IS NULL OR $user IN users)
          AND ($service IS NULL OR $service IN services)
        RETURN toString(i.incident_id) AS incident_id,
               i.incident_date         AS incident_date,
               i.login_attempts        AS login_attempts,
               i.affected_users        AS affected_users,
               i.affected_users_count  AS affected_users_count,
               i.successful_logins     AS successful_logins,
               coalesce(i.tor_exit, false) AS tor,
               users, services, hosts
        ORDER BY incident_date DESC
        LIMIT $limit
    """
    records = run(query, user=user, service=service, limit=limit)
    return {"status": "success", "data": [dict(record) for record in records]}


@app.get("/incidents/{incident_id}")
def get_incident_graph(
    incident_id: str,
    depth: int = Query(2, ge=MIN_DEPTH, le=MAX_DEPTH),
):
    incident_query = """
        MATCH (i:Incident)
        WHERE toString(i.incident_id) = $incident_id
        RETURN i
        ORDER BY i.incident_date DESC
    """
    incidents = run(incident_query, incident_id=incident_id)
    if not incidents:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")

    graph_query = f"""
        MATCH (i:Incident)-[:INCIDENT]->(involved:User)
        WHERE toString(i.incident_id) = $incident_id
        WITH collect(DISTINCT involved) AS seeds
        UNWIND seeds AS seed
        OPTIONAL MATCH path = (seed)-[*{MIN_DEPTH}..{depth}]-(m)
        WHERE none(n IN nodes(path) WHERE n:Incident)
          AND all(n IN nodes(path) WHERE NOT n:User OR n IN seeds)
        RETURN seed, collect(path) AS paths
    """
    records = run(graph_query, incident_id=incident_id)

    nodes: dict[str, dict] = {}
    edges: dict[str, dict] = {}
    seeds: list[str] = []

    for record in records:
        seed = record["seed"]
        nodes[seed.element_id] = as_node(seed)
        seeds.append(seed.element_id)

        for path in record["paths"] or []:
            for node in path.nodes:
                nodes[node.element_id] = as_node(node)
            for rel in path.relationships:
                edge = as_edge(rel)
                if edge:
                    edges[edge["id"]] = edge

    return {
        "status": "success",
        "incident": as_node(incidents[0]["i"])["properties"],
        "seeds": seeds,
        "incident_id": incident_id,
        "data": {"nodes": list(nodes.values()), "edges": list(edges.values())},
    }


@app.get("/health")
def health():
    try:
        driver.verify_connectivity()
        return {"status": "success", "neo4j": "reachable"}
    except Exception as error:
        raise HTTPException(status_code=503, detail=str(error))
