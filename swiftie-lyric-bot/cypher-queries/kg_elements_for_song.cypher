MATCH (s:Song{name: "Love Story"})-[:HAS_LYRICS]->(l:Lyrics)<-[:PART_OF]-(lc:LyricsChunk)-[:HAS_ENTITY]-(e)
WHERE NOT (e.id IN ["Taylor Swift", "I", "You", "Pre-Chorus", "Chorus", "Bridge", "Outro", "Intro"])
WITH collect(e) as nodeslist
MATCH p = (e)-[r]-(e2)
WHERE e in nodeslist and e2 in nodeslist
UNWIND relationships(p) as rels
RETURN DISTINCT apoc.text.join([labels(startNode(rels))[0], startNode(rels).id, type(rels), labels(endNode(rels))[0], endNode(rels).id]," ")
