import os
import csv
import pickle

from langchain_core.documents import Document
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_openai import ChatOpenAI
from langchain_community.graphs import Neo4jGraph

from langchain_community.graphs.graph_document import Node, Relationship

from dotenv import load_dotenv
load_dotenv()

DATA_PATH = "swiftie-lyric-bot/data"
CHUNKS_CSV = os.path.join(DATA_PATH, "lyrics-chunks.csv")
GRAPH_DOCS_PATH = os.path.join(DATA_PATH, "knowledge-graph-cache")

# CREATES THE LYRICS KNOWLEDGE GRAPH

def get_graph_docs(lyrics_transformer, track_docs):

    track_id = track_docs[0].metadata["track_id"]
    
    # do the graph docs already exist?
    pkl_path = os.path.join(GRAPH_DOCS_PATH, f"{track_id}.pkl")

    if os.path.isfile(pkl_path):
        print("- using cache")
        # unpickle the graph docs
        with open(pkl_path, "rb") as pkl_file:
            return pickle.load(pkl_file)
    else:
        print("- creating graph docs")
        # create the graph docs
        graph_docs = lyrics_transformer.convert_to_graph_documents(track_docs)
        # pickle the graph docs
        with open(pkl_path, "wb") as pkl_file:
            pickle.dump(graph_docs, pkl_file)
        
        return graph_docs

def map_graph_docs(track_docs):
    # insert nodes and relationship to map LLM generated nodes to lyrics
    for track_chunk in track_docs:
        
        lyrics_chunk_node = Node(
            id=track_chunk.source.metadata["track_id"] + "." + track_chunk.source.metadata["number"],
            type="LyricsChunk"
        )

        for node in track_chunk.nodes:

            track_chunk.relationships.append(
                Relationship(
                    source=lyrics_chunk_node,
                    target=node, 
                    type="HAS_ENTITY"
                    )
                )
        
        track_chunk.nodes.append(lyrics_chunk_node)

    return track_docs

def create_knowledge_graph():

    os.makedirs(GRAPH_DOCS_PATH, exist_ok=True)

    llm = ChatOpenAI(
        openai_api_key=os.getenv('OPENAI_API_KEY'), 
        # temperature=0, 
        # model_name="gpt-4-turbo"
        model_name="gpt-3.5-turbo"
        )

    # defined nodes and undefined relationships
    lyrics_transformer = LLMGraphTransformer(
        llm=llm,
        allowed_nodes=["Person", "Action", "Emotion", "Location", "Outcome", "Opinion", "Time"],
        )

    # undefined nodes and relationships
    # lyrics_transformer = LLMGraphTransformer(
    #     llm=llm,
    #     )

    # defined nodes and relationships
    # lyrics_transformer = LLMGraphTransformer(
    #     llm=llm,
    #     allowed_nodes=["Person", "Action", "Emotion", "Location", "Outcome", "Opinion", "Time"],
    #     allowed_relationships=["COMMITTED", "FELT", "AT", "RESULTED_IN", "THOUGHT", "SAID", "OCCURED_ON"],
    #     )

    graph = Neo4jGraph(
        url=os.getenv("NEO4J_URI"),
        username=os.getenv("NEO4J_USERNAME"),
        password=os.getenv("NEO4J_PASSWORD")
    )

    # load chunks
    chunks_csvfile = open(CHUNKS_CSV, encoding="utf8", newline='')
    chunks_csv = csv.DictReader(chunks_csvfile)

    BATCH_LIMIT = 1000
    batch = 0

    # process the chunks for each track
    track_docs = []
    last_track_id = None

    for chunk in chunks_csv:
        track_id = chunk["track_id"]

        if track_id != last_track_id:
            if len(track_docs) > 0:
                print(f"Processing track - {track_id}")
                graph_docs = map_graph_docs(
                    get_graph_docs(lyrics_transformer, track_docs)
                    )
                graph.add_graph_documents(graph_docs)

            batch += 1
            track_docs = []
            last_track_id = track_id

        track_docs.append(
            Document(
                page_content=chunk["text"], 
                metadata={"track_id": chunk["track_id"], "number": chunk["number"]}
                )
            )
        
        if batch >= BATCH_LIMIT:
            break

if __name__ == "__main__":

    create_knowledge_graph()