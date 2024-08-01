WITH genai.vector.encode(
    "love and heartbreak",
    "OpenAI",
    { token: "sk-..." }) AS userEmbedding
CALL db.index.vector.queryNodes('lyrics', 6, userEmbedding)
YIELD node, score
MATCH (node)-[:PART_OF]->(l:Lyrics)<-[:HAS_LYRICS]-(s:Song)
RETURN  
    node.text as text, score,
    { 
        song: s.name,
        released: s.released
    } AS metadata