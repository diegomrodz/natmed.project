
// Deleting all ScientificNames that are equal to its medicine
MATCH (a:Medicine)-[r]->(b:ScientificName {id: a.name})
DETACH DELETE b

// Deleting all Synonymous that are equal to its medicine
MATCH (a:Medicine)-[r]->(b:Synonymous {id: a.name})
DETACH DELETE b

// Fixing foods that have the smame name of medicines
MATCH (a:Medicine)
MATCH (i)-[r:WHEN_CONSUMED_WITH]->(b:Food {id: a.name})
CREATE (i)-[:WHEN_CONSUMED_WITH]->(a)
DETACH DELETE b

// Fixing drugs that have the smame name of medicines
MATCH (a:Medicine)
MATCH (i)-[r:WHEN_USED_WITH]->(b:Drug {id: a.name})
CREATE (i)-[:WHEN_USED_WITH]->(a)
DETACH DELETE b

// Fixing the effectiveness relationship, using a property 
// to hold the effectiveness level
MATCH (a:Medicine)-[r]->(n:EffectivenessInfo)
CREATE (a)-[:IS_EFFECTIVE {level: type(r)}]->(n)
DELETE r

// Fixing the safety relationship, using a property 
// to hold the safety level
MATCH (a:Medicine)-[r]->(n:SafetyInfo)
CREATE (a)-[:IS_SAFE {level: type(r)}]->(n)
DELETE r

// Fixing the drugInteraction relationship, using a property 
// to hold the drugInteraction level
MATCH (a:Medicine)-[r]->(n:DrugInteraction)
CREATE (a)-[:HAS_INTERACTION {level: type(r)}]->(n)
DELETE r

// FIXING DOSING INFO
MATCH (a:Medicine)-[r1]->(n:DosingInfo)-[r2]->(b:Disease)
MATCH (n)<-[]-(ref:Reference)
MATCH (n)-[]->(ctx:Context)
CREATE (a)-[:HAS_INTERACTION]->(m:Information {text: n.text, id: n.id, type: labels(n)[0]})-[:IN_RELATION_TO]->(b)
CREATE (m)<-[:REFERENCES]-(ref)
CREATE (m)-[:WHEN_CONTEXTUALIZED_IN]->(ctx)

MATCH (n:DosingInfo)
DETACH DELETE n

// FIXING EFFECTIVENESS INFO
MATCH (a:Medicine)-[r1]->(n:EffectivenessInfo)-[r2]->(b:Disease)
MATCH (n)<-[]-(ref:Reference)
CREATE (a)-[:HAS_INTERACTION]->(m:Information {text: n.text, id: n.id, type: labels(n)[0], level: r1.level})-[:IN_RELATION_TO]->(b)
CREATE (m)<-[:REFERENCES]-(ref)

MATCH (n:EffectivenessInfo)
DETACH DELETE n

// FIXING SAFETY INFO
MATCH (a:Medicine)-[r1]->(n:SafetyInfo)
MATCH (n)<-[]-(ref:Reference)
CREATE (a)-[:HAS_INTERACTION]->(m:Information {text: n.text, id: n.id, type: labels(n)[0], level: r1.level})-[:IN_RELATION_TO]->(b)
CREATE (m)<-[:REFERENCES]-(ref)

MATCH (n:SafetyInfo)
DETACH DELETE n

// fix the name of the relationship between info and its targeted entities
MATCH (a)-[r1:HAS_INTERACTION]->(i)-[r2:IN_RELATION_TO]->(b)
CREATE (a)-[:IS_MENTIONED_IN]->(i)-[:IN_RELATION_TO]->(b)
DELETE r1
DELETE r2

// Fix Disease Interaction
MATCH (a:Medicine)-[r1]->(n:DiseaseInteraction)-[r2]->(b:Disease)
MATCH (n)<-[]-(ref:Reference)
CREATE (a)-[:HAS_INTERACTION]->(m:Interaction {id: n.id, text: n.text, type: labels(n)[0]})-[:IN_RELATION_TO]->(b)
CREATE (m)<-[:REFERENCES]-(ref)

MATCH (n:DiseaseInteraction)
DETACH DELETE n

// Fix Drug Interaction
MATCH (a:Medicine)-[r1]->(n:DrugInteraction)-[r2]->(b:Drug)
MATCH (n)<-[]-(ref:Reference)
CREATE (a)-[:HAS_INTERACTION]->(m:Interaction {id: n.id, text: n.text, type: labels(n)[0], level: r1.level})-[:IN_RELATION_TO]->(b)
CREATE (m)<-[:REFERENCES]-(ref)

MATCH (n:DrugInteraction)
DETACH DELETE n

//
MATCH (a:Medicine)-[r1]->(n:FoodInteraction)-[r2]->(b:Food)
MATCH (n)<-[]-(ref:Reference)
CREATE (a)-[:HAS_INTERACTION]->(m:Interaction {id: n.id, text: n.text, type: labels(n)[0]})-[:IN_RELATION_TO]->(b)
CREATE (m)<-[:REFERENCES]-(ref)

MATCH (n:FoodInteraction)
DETACH DELETE n


//
MATCH (a:Medicine)-[r1]->(n:HerbSuplementsInteraction)
CREATE (a)-[:HAS_INTERACTION]->(m:Interaction {id: n.id, text: n.text, type: labels(n)[0]})

MATCH (n:HerbSuplementsInteraction)
DETACH DELETE n

//
MATCH (a:Medicine)-[r1]->(n:LaboratoryInteraction)-[r2]->(b:LaboratoryTest)
MATCH (n)<-[]-(ref:Reference)
CREATE (a)-[:HAS_INTERACTION]->(m:Interaction {id: n.id, text: n.text, type: labels(n)[0]})-[:IN_RELATION_TO]->(b)
CREATE (m)<-[:REFERENCES]-(ref)

//
MATCH (n:Information)
MATCH (n)<-[]-(r:Reference)
WITH n.id as id, count(n.id) as cnt, collect(r) as refs
UNWIND refs as ref
MATCH (m:Information {id: id})
CREATE (m)<-[:REFERENCES]-(ref)

MATCH (n:Information) 
WITH n.id as id, count(n.id) as count, collect(n) as lst
WHERE size(lst) > 1
UNWIND range(1, size(lst) - 1) as i
DETACH DELETE lst[i]