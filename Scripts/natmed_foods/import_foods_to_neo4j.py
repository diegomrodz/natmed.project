from pymongo import MongoClient
from neo4j.v1 import GraphDatabase, basic_auth

NATMED_CN = "mongodb://localhost:27017"
NATMED_DB = "natmed"
NATMED_COL = "foods"

def new_scientific_name_node(tx, name):
    tx.run("""
        MERGE (sci_name:ScientificName {id: {name}})
            ON CREATE SET sci_name.id={name}
        """,
        name=name)

def new_scientific_name_rel(tx, name, food):
    tx.run("""
        MATCH (a:Food {id: {id}})
        MATCH (b:ScientificName {id: {name}})
        MERGE (a)-[:ALSO_KNOW_AS]->(b);
        """,
        id=food['_id'],
        name=name)

def new_food_node(tx, food):
    tx.run("""
        MERGE (food:Food {id: {id}})
        ON CREATE SET food.id = {id},
            food.name = {name},
            food.url = {url},
            food.family_name = {family_name},
            food.description = {description},
            food.history = {history},
            food.used_for = {used_for}
        """,
        id=food.get('_id'),
        name=food.get('name'),
        url=food.get('url'),
        family_name=food.get('familyName'),
        description=food.get('description'),
        history=food.get('history'),
        used_for=food.get('peopleUseThisFor'))

def insert_food(tx, food):
    print("Inserting the Food: {0} (#{1})".format(food['name'], food['_id']))
    new_food_node(tx, food)

    if food.get('scientficNames'):
        for sci_name in food.get('scientficNames'):
            new_scientific_name_node(tx, sci_name)
            new_scientific_name_rel(tx, sci_name, food)

if __name__ == '__main__':
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=basic_auth("neo4j", "naturalmed"))
    client = MongoClient(NATMED_CN)
    col = client[NATMED_DB][NATMED_COL]

    print("Beggining Neo4j Session\n")
    session = driver.session() 
    
    try:
        tx_count = 0
        for food in col.find().limit(5):
            with session.begin_transaction() as tx:
                tx_count += 1
                print("Beggining Neo4j Transaction: {0}".format(tx_count))
                insert_food(tx, food)
                print("Ending Neo4j Transaction\n")
    finally:
        print("Ending Neo4j Session")
        session.close()
        print("Ending Script")
