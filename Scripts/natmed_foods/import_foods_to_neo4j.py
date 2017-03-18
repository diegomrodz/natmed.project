from pymongo import MongoClient
from neo4j.v1 import GraphDatabase, basic_auth
import hashlib

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

def new_synonymous_node(tx, name):
    tx.run("""
        MERGE (synonymous:Synonymous {id: {name}})
            ON CREATE SET synonymous.id={name}
        """,
        name=name)

def new_synonymous_rel(tx, name, food):
    tx.run("""
        MATCH (a:Food {id: {id}})
        MATCH (b:Synonymous {id: {name}})
        MERGE (a)-[:ALSO_KNOW_AS]->(b);
        """,
        id=food['_id'],
        name=name)

def new_reference_node(tx, ref):
    tx.run("""
        MERGE (ref:Reference {id: {id}})
            ON CREATE SET ref.id={id},
                          ref.url={url}
        """,
        id=ref['id'],
        url=ref['url'])

def new_reference_rel(tx, ref, _cls, _id):
    tx.run("""
        MATCH (a:Reference {id: {ref}})
        MATCH (b:%s {id: {id}})
        MERGE (a)-[:REFERENCES]->(b);
        """ % _cls,
        id=_id,
        ref=ref['id'])

def new_safety_info_node(tx, info):
    tx.run("""
        MERGE (info:SafetyInfo {id: {id}})
        ON CREATE SET info.id = {id},
            info.text = {text}
        """,
        id=info['id'],
        text=info['text'])

def new_safety_info_rel(tx, info, food):
    tx.run("""
        MATCH (a:Food {id: {id}})
        MATCH (b:SafetyInfo {id: {info}})
        MERGE (a)-[:IS_%s]->(b);
        """ % info['safety'].replace(" ", "_"),
        id=food['_id'],
        info=info['id'])

def new_context_node(tx, ctx):
    tx.run("""
        MERGE (ctx:Context {id: {id}})
            ON CREATE SET ctx.id={id}
        """,
        id=ctx)

def new_context_rel(tx, ctx, _cls, _id):
    tx.run("""
        MATCH (a:%s {id: {id}})
        MATCH (b:Context {id: {ctx}})
        MERGE (a)-[:IS_CONTEXTUALIZED_IN]->(b);
        """ % _cls,
        id=_id,
        ctx=ctx)

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

    if food.get('alsoKnowAs'):
        for synonymous in food.get('alsoKnowAs'):
            new_synonymous_node(tx, synonymous)
            new_synonymous_rel(tx, synonymous, food)
    
    if food.get('references'):
        for reference in food.get('references'):
            new_reference_node(tx, reference)
            new_reference_rel(tx, reference, "Food", food['_id'])
    
    if food.get('safetyInfo'):
        for info in [x for x in food.get('safetyInfo') if x.get('safety') != None]: # Fix
            info['id'] = hashlib.md5(info['text'].encode()).hexdigest()
            new_safety_info_node(tx, info)
            new_safety_info_rel(tx, info, food)

            if info.get('context'):
                new_context_node(tx, info.get('context'))
                new_context_rel(tx, info.get('context'), "SafetyInfo", info['id'])

if __name__ == '__main__':
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=basic_auth("neo4j", "naturalmed"))
    client = MongoClient(NATMED_CN)
    col = client[NATMED_DB][NATMED_COL]

    print("Beggining Neo4j Session\n")
    session = driver.session() 
    
    try:
        tx_count = 0
        for food in col.find().limit(15):
            with session.begin_transaction() as tx:
                tx_count += 1
                print("Beggining Neo4j Transaction: {0}".format(tx_count))
                insert_food(tx, food)
                print("Ending Neo4j Transaction\n")
    finally:
        print("Ending Neo4j Session")
        session.close()
        print("Ending Script")
