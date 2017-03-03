
// Nodes
//

// Products

USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM "file:\\natural_metadata.csv" AS row
CREATE (:Product {productID: row.asin, title: row.title, description: row.description, imageUrl: row.imUrl});

// or

USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM "file:\\natural_metadata.csv" AS row
MERGE (product:Product {productID: row.asin})
ON CREATE SET product.title = row.title,
			  product.description = row.description,
			  product.imageUrl = row.imUrl;

CREATE INDEX ON :Product(productID);
CREATE INDEX ON :Product(title);

// Categories

USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM "file:\\natural_metadata_categories.csv" AS row
CREATE (:Category {name: row.category});

// or 

USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM "file:\\natural_metadata_categories.csv" AS row
MERGE (category:Category {name: row.category})
ON CREATE SET category.name = row.category

CREATE INDEX ON :Category(name);

// Users

USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM "file:\\natural_reviews_users.csv" AS row
MERGE (user:User {userID: row.id})
ON CREATE SET user.name = row.user;

CREATE INDEX ON :User(userID);

// Edges
//

// Product -[has been bought toghether with]-> Product

USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM "file:\\natural_metadata_also_bought.csv" AS row
MATCH (a:Product {productID: row.productID})
MATCH (b:Product {productID: row.relatedTo})
MERGE (a)-[:HAS_ALSO_BOUGHT]->(b);

// Product -[has been viewed toghether with]-> Product

USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM "file:\\natural_metadata_also_viewed.csv" AS row
MATCH (a:Product {productID: row.productID})
MATCH (b:Product {productID: row.relatedTo})
MERGE (a)-[:HAS_ALSO_VIEWED]->(b);

// Product -[belongs to]-> Category

USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM "file:\\natural_metadata_product_categories.csv" AS row
MATCH (a:Product {productID: row.productID})
MATCH (b:Category {name: row.category})
MERGE (a)-[:BELONGS_TO]->(b);

// Product -[is ranked on sales at]-> Category

USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM "file:\\natural_metadata_sales_rank.csv" AS row
MATCH (a:Product {productID: row.productID})
MATCH (b:Category {name: row.category})
MERGE (a)-[:IS_SALES_RANKED_ON {position: row.salesRank}]->(b);
