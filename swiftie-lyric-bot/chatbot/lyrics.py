import os
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Neo4jVector
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate

from llm import llm
from graph import graph

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
embedding_provider = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

lyrics_vector = Neo4jVector.from_existing_index(
    embedding_provider,
    graph=graph,
    index_name="lyrics",
    embedding_node_property="embeddings",
    text_node_property="text",
    retrieval_query="""
// get the song
MATCH (node)-[:PART_OF]->(l:Lyrics)<-[:HAS_LYRICS]-(s:Song)
WITH node, score, s
// get the entities, excluding noise
MATCH (node)-[:HAS_ENTITY]-(e)
WHERE NOT (e.id IN ["Taylor Swift", "I", "You", "Pre-Chorus", "Chorus", "Bridge", "Outro", "Intro"])
WITH node, score, s, collect(e) as nodeslist
// find the relationships between the entities related to the song
MATCH p = (e)-[r]-(e2)
WHERE e in nodeslist and e2 in nodeslist
UNWIND relationships(p) as rels
WITH 
    node, 
    score, 
    s, 
    collect(apoc.text.join(
        [labels(startNode(rels))[0], startNode(rels).id, type(rels), labels(endNode(rels))[0], endNode(rels).id]
        ," ")) as kg
RETURN
    node.text as text, score,
    { 
        song: s.name,
        released: s.released,
        entities: kg
    } AS metadata
"""
)

instructions = (
    "Use the given context to answer the question."
    "Reply with an answer that includes the name of the song and other relevant information from the lyrics."
    "If you don't know the answer, say you don't know."
    "Context: {context}"
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", instructions),
        ("human", "{input}"),
    ]
)

lyrics_retriever = lyrics_vector.as_retriever()
lyrics_chain = create_stuff_documents_chain(llm, prompt)
lyrics_retriever = create_retrieval_chain(
    lyrics_retriever, 
    lyrics_chain
)

def get_lyrics(input):
    return lyrics_retriever.invoke({"input": input})
