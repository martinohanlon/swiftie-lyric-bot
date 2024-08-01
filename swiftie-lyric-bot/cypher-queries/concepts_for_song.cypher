MATCH (s:Song{name: "Fortnight"})-[:HAS_LYRICS]->(l:Lyrics)
MATCH p = (l)-[*1..2]->(concepts)
UNWIND relationships(p) as rels
WITH rels WHERE type(rels) <> "CONTAINS"
RETURN labels(startNode(rels)), startNode(rels).id, type(rels), labels(endNode(rels)), endNode(rels).id