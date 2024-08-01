import os
from langchain_community.graphs import Neo4jGraph
from create_kg import create_knowledge_graph

from dotenv import load_dotenv
load_dotenv()

DATA_PATH = "swiftie-lyric-bot/data"
IMPORT_CYPHER = os.path.join(DATA_PATH, "build_graph.cypher")

# CALLED BY THE DOCKER BUILD PROCESS TO CREATE THE GRAPH

# Import the structured data from the csv files
graph = Neo4jGraph(
    url=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD")
)

# Does the data already exist?
result = graph.query("MATCH (n) WHERE n:Artist RETURN count(n) as count")

if result[0]['count'] > 0:
    print("Knowledge graph already exists")
else:

    print("Importing structured data")

    with open(IMPORT_CYPHER, "r") as file:
        import_queries = file.read().split(";")

    for query in import_queries:
        graph.query(query)

    print("Creating lyrics knowledge graph")

    create_knowledge_graph()

    print("Knowledge graph created")
