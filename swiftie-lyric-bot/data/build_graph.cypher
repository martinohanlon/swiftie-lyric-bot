MERGE (ts:Artist{name:"Taylor Swift"})
WITH ts

LOAD CSV WITH HEADERS from 'file:///taylor_swift_tracks.csv' as row

MERGE (a:Album{id: row.album_id})
SET 
    a.name = row.album_name, 
    a.released = date(row.album_release_date),
    a.coverImage = row.album_cover_image

MERGE (s:Song{id: row.track_id})
SET 
    s.name = row.track_name, 
    s.released = date(row.track_release_date),
    s.lyricsFilename = row.lyrics_filename

MERGE (ts)-[:RELEASED]->(a)
MERGE (a)<-[r:IS_ON]-(s);

LOAD CSV WITH HEADERS from "file:///lyrics.csv" as row

MATCH (t:Song{id: row.track_id})

MERGE (l:Lyrics{id: row.track_id})
SET
    l.text = row.lyrics

MERGE (t)-[:HAS_LYRICS]->(l);

LOAD CSV WITH HEADERS from "file:///lyrics-chunks.csv" as row

MATCH (l:Lyrics{id: row.track_id})
MERGE (lc:LyricsChunk{id: row.track_id + '.' + row.number})
MERGE (l)<-[:PART_OF]-(lc)
SET 
    lc.text = row.text,
    lc.track_id = row.track_id,
    lc.number = toInteger(row.number)

WITH lc, row
CALL db.create.setNodeVectorProperty(lc, 'embedding', apoc.convert.fromJsonList(row.embedding));

CREATE VECTOR INDEX lyrics IF NOT EXISTS
FOR (lc:LyricsChunk)
ON lc.embedding
OPTIONS {indexConfig: {
 `vector.dimensions`: 1536,
 `vector.similarity_function`: 'cosine'
}}