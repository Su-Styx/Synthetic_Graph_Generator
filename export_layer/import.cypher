CREATE CONSTRAINT node_id IF NOT EXISTS
FOR (n:Node) REQUIRE n.id IS UNIQUE;

LOAD CSV WITH HEADERS FROM 'file:///nodes.csv' AS row
MERGE (n:Node {id: row.id});

LOAD CSV WITH HEADERS FROM 'file:///relationships.csv' AS row
MATCH (s:Node {id: row.source})
MATCH (t:Node {id: row.target})
MERGE (s)-[:CONNECTS]->(t);