WITH genai.vector.encode(
    "love and heartbreak",
    "OpenAI",
    { token: "sk-..." }) AS userEmbedding
CALL db.index.vector.queryNodes('lyrics', 6, userEmbedding)
YIELD node, score

MATCH (node)-[:PART_OF]->(l:Lyrics)<-[:HAS_LYRICS]-(s:Song)
WITH node, score, s
MATCH (node)-[:HAS_ENTITY]-(e)
WHERE NOT (e.id IN ["Taylor Swift", "I", "You", "Pre-Chorus", "Chorus", "Bridge", "Outro", "Intro"])
WITH node, score, s, collect(e) as nodeslist
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