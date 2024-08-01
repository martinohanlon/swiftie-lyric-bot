MATCH (l:Location)<-[:CONTAINS]-(ly:Lyrics)<-[:HAS_LYRICS]-(s:Song)
RETURN l.id, count(s.name) as songs 
order by songs desc