from neo4j.v1 import GraphDatabase, basic_auth
from pymongo import MongoClient

NATMED_CN = "mongodb://localhost:27017"
NATMED_DB = "natmed"
NATMED_COL = "references"

gdriver = GraphDatabase.driver("bolt://localhost:7687", auth=basic_auth("neo4j", "naturalmed"))
client = MongoClient(NATMED_CN)
col = client[NATMED_DB][NATMED_COL]

with gdriver.session() as session:
    docs = list(col.find())
    count = len(docs)
    i = 1

    print("Counting {} documents\n\n".format(count))

    for doc in docs:
        print("Inserting document #{}".format(i))
        print("Reference ID: #{}".format(doc['_id']))
        
        try:
            session.run("""MATCH (r:Reference {id: "%s"})
                        SET r.title = "%s", r.text = "%s";""" % (doc['_id'], doc.get('title'), doc.get('text')))
            
            print("Document inserted!\n")
        except Exception as e:
            print("Error inserting document!")
            print(e)
            print("\n")
        finally:
            i += 1
