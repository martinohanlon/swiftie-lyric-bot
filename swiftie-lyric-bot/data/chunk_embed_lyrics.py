import os
import csv
from dotenv import load_dotenv
load_dotenv()

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import CharacterTextSplitter
from openai import OpenAI

DATA_PATH = "swiftie-lyric-bot/data"

# INPUT FILES
# TRACK_CSV = os.path.join(DATA_PATH, "taylor_swift_tracks.csv")
LYRICS_CSV = os.path.join(DATA_PATH, "lyrics.csv")
LYRICS_PATH = os.path.join(DATA_PATH, "lyrics")

# OUTPUT FILES
CHUNKS_CSV = os.path.join(DATA_PATH, "lyrics-chunks.csv")

CHUNK_SIZE = 400
CHUNK_OVERLAP = 50

def get_embedding(llm, text):
    response = llm.embeddings.create(
            input=text,
            model="text-embedding-ada-002"
        )
    return response.data[0].embedding

def chunk_lyrics():
    print("hi")

    llm = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    text_splitter = CharacterTextSplitter(
        separator="\n\n",
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )

    # CREATE CHUNKS CSV

    lyrics_csvfile = open(LYRICS_CSV, encoding="utf8", newline='')
    lyrics_csv = csv.DictReader(lyrics_csvfile)

    # chunks csv file
    chunks_csvfile = open(CHUNKS_CSV, "w", encoding="utf8", newline='')
    fieldnames = ['track_id', 'number', 'text', 'embedding']
    chunks_csv = csv.DictWriter(chunks_csvfile, fieldnames=fieldnames)
    chunks_csv.writeheader()

    # chunk and embed the lyrics
    for lyrics in lyrics_csv:
        print(lyrics["track_id"])
        loader = TextLoader(os.path.join(LYRICS_PATH, f"{lyrics['track_id']}.txt"), encoding="utf8")
        lyrics_text = loader.load()
        chunks = text_splitter.split_documents(lyrics_text)
        
        number = 0
        for chunk in chunks:
            chunk_data = {
                "track_id": lyrics["track_id"]
            }
            chunk_data["number"] = number
            chunk_data["text"] = chunk.page_content
            # test without creating embeddings
            # chunk_data["embedding"] = [0,0,0]
            chunk_data["embedding"] = get_embedding(llm, chunk.page_content)

            chunks_csv.writerow(chunk_data)

            number += 1

    lyrics_csvfile.close()
    chunks_csvfile.close()

if __name__ == "__main__":
    chunk_lyrics()