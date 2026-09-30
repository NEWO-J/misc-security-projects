import requests
import subprocess
import re
import base64 
import json
from neo4j import GraphDatabase
import argparse


parser = argparse.ArgumentParser()

parser.add_argument("-c","--container",help="Target Container",required=True)

args = parser.parse_args()

# ghcr.io/newo-j/misc-security-projects/my-app@sha256:76f878691a821df66084646390f95a90d79030711ecab57145f069fdec920ed8

result = subprocess.run(["cosign", "verify-attestation",\
                 "--type", "https://slsa.dev/provenance/v1",\
                 "--certificate-identity", "https://github.com/NEWO-J/misc-security-projects/.github/workflows/container_attest.yml@refs/heads/main",\
                 "--certificate-oidc-issuer", "https://token.actions.githubusercontent.com",\
                args.container], capture_output=True)

if result.returncode != 0: 
    print("its 0")
    print(result.stdout)
    print(result.stderr)
    exit()

reg = re.compile(r'^{"payload".+}$')

results = json.loads(result.stdout.decode('utf-8'))

if re.match(reg, result.stdout.decode('utf-8')):
    decoded = base64.b64decode(results["payload"].encode('utf-8')).decode('utf-8')
    decoded_dict = json.loads(decoded)
    if {decoded_dict["predicate"]["buildDefinition"]["internalParameters"]["github"]["runner_environment"]} != "github-hosted":
        print("ALERT: The runner was not hosted on github infrastructure ")

    with GraphDatabase.driver("neo4j://localhost:7687", auth=("neo4j", "neo4jneo4j")) as driver:
        create_query = """
        MERGE (c:Container {digest: $digest})
        MERGE (w:Workflow {file: $file, runner: $runner, trigger: $trigger})
        MERGE (r:Repository {name: $repo, commit: $commit})
        MERGE (r)<-[:SOURCE]-(w)
        MERGE (w)<-[:BUILT_FROM]-(c)
        """

        driver.execute_query(
            create_query, 
            digest= decoded_dict["subject"][0]["digest"]["sha256"],
            file = decoded_dict["predicate"]["buildDefinition"]["externalParameters"]["workflow"]["path"],
            runner = decoded_dict["predicate"]["buildDefinition"]["internalParameters"]["github"]["runner_environment"],
            trigger = decoded_dict["predicate"]["buildDefinition"]["internalParameters"]["github"]["event_name"],
            repo = decoded_dict["predicate"]["buildDefinition"]["externalParameters"]["workflow"]["repository"],
            commit = decoded_dict["predicate"]["buildDefinition"]["resolvedDependencies"][0]["digest"]["gitCommit"],
            database_="neo4j")

    print(f"""
    ====== Container Attestation Results =========
    Container: {decoded_dict["subject"][0]["name"]}:sha256-{decoded_dict["subject"][0]["digest"]["sha256"]}
    .
    The following attributes were verified using OIDC vvvvvvvv
    .
    Source Repository: {decoded_dict["predicate"]["buildDefinition"]["externalParameters"]["workflow"]["repository"]} 
    Built from Worfklow: {decoded_dict["predicate"]["buildDefinition"]["externalParameters"]["workflow"]["path"]}
    .
    Workflow Details:
      - Triggered by: {decoded_dict["predicate"]["buildDefinition"]["internalParameters"]["github"]["event_name"]}
      - Runner Infrastructure: {decoded_dict["predicate"]["buildDefinition"]["internalParameters"]["github"]["runner_environment"]}
      - Source Git Commit: {decoded_dict["predicate"]["buildDefinition"]["resolvedDependencies"][0]["digest"]["gitCommit"]}
    
    """)
