from langchain.chains import GraphCypherQAChain
from langchain.prompts.prompt import PromptTemplate

from llm import llm
from graph import graph

CYPHER_GENERATION_TEMPLATE = """
You are an expert Neo4j Developer translating user questions into Cypher to answer get album, song and lyric information from the graph.
Convert the user's question based on the schema.

Use only the provided relationship types and properties in the schema.
Do not use any other relationship types or properties that are not provided.

Do not return entire nodes or embedding properties.

Example Cypher Statements:

1. To find the songs and albums:
```
MATCH (s:Song)-[:IS_ON]->(a:Album)
WHERE a.name = "Album Name"
RETURN a.name, s.name
```

2. To find the lyrics for a song:
```
MATCH (s:Song)-[:HAS_LYRICS]->(l:Lyrics)
WHERE s.name = "Blank Space"
RETURN s.name, l.text
```

Schema:
{schema}

Question:
{question}
"""

cypher_prompt = PromptTemplate(
    input_variables=["schema", "question", "name"], template=CYPHER_GENERATION_TEMPLATE
)

song_data_qa = GraphCypherQAChain.from_llm(
    llm,
    graph=graph,
    cypher_prompt=cypher_prompt,
    include_types=["Album", "Song", "Lyrics", "RELEASED_ON", "IS_ON", "HAS_LYRICS"]
)

def get_song_data(input):
    return song_data_qa.invoke({"query": input})

# print(song_data_qa.input_keys)

# print(get_song_data("What album is blank space on?"))