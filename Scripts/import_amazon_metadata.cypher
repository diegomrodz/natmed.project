USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM "file:\\natural_metadata_also_bought.csv" AS row
MATCH (a:Product {productID: row.productID})
MATCH (b:Product {productID: row.relatedTo})
MERGE (a)-[:HAS_ALSO_BOUGHT]->(b);