from pymongo import MongoClient
from neo4j.v1 import GraphDatabase, basic_auth
import hashlib
import time

NATMED_CN = "mongodb://localhost:27017"
NATMED_DB = "natmed"
NATMED_COL = "foods"

POSSIBLE_EFFECTIVES = [
    "LIKELY INEFFECTIVE",
    "INEFFECTIVE",
    "EFFECTIVE",
    "LIKELY EFFECTIVE",
    "POSSIBLY EFFECTIVE",
    "INSUFFICIENT RELIABLE EVIDENCE to RATE",
    "POSSIBLY INEFFECTIVE"
]

def new_scientific_name_node(tx, name):
    tx.run("""
        MERGE (sci_name:ScientificName {id: {name}})
            ON CREATE SET sci_name.id={name}
        """,
        name=name.title())

def new_scientific_name_rel(tx, name, medicine):
    tx.run("""
        MATCH (a:Medicine {id: {id}})
        MATCH (b:ScientificName {id: {name}})
        MERGE (a)-[:ALSO_KNOW_AS]->(b);
        """,
        id=medicine['_id'],
        name=name.title())

def new_synonymous_node(tx, name):
    tx.run("""
        MERGE (synonymous:Synonymous {id: {name}})
            ON CREATE SET synonymous.id={name}
        """,
        name=name.title())

def new_synonymous_rel(tx, name, medicine):
    tx.run("""
        MATCH (a:Medicine {id: {id}})
        MATCH (b:Synonymous {id: {name}})
        MERGE (a)-[:ALSO_KNOW_AS]->(b);
        """,
        id=medicine['_id'],
        name=name.title())

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

def new_safety_info_rel(tx, info, medicine):
    tx.run("""
        MATCH (a:Medicine {id: {id}})
        MATCH (b:SafetyInfo {id: {info}})
        MERGE (a)-[:IS_%s]->(b);
        """ % info['safety'].replace(" ", "_"),
        id=medicine['_id'],
        info=info['id'])

def new_context_node(tx, ctx):
    tx.run("""
        MERGE (ctx:Context {id: {id}})
            ON CREATE SET ctx.id={id}
        """,
        id=ctx.title())

def new_context_rel(tx, ctx, _cls, _id):
    tx.run("""
        MATCH (a:%s {id: {id}})
        MATCH (b:Context {id: {ctx}})
        MERGE (a)-[:IS_CONTEXTUALIZED_IN]->(b);
        """ % _cls,
        id=_id,
        ctx=ctx.title())

def new_effectiveness_node(tx, info):
    tx.run("""
        MERGE (info:EffectivenessInfo {id: {id}})
            ON CREATE SET info.id={id},
                info.text={text}
        """,
        id=info['id'],
        text=info['text'])    

def new_effectiveness_rel(tx, info, medicine):
    if not info['effectiveness'] in POSSIBLE_EFFECTIVES:
        info['effectiveness'] = "TO BE DEFINED"

    tx.run("""
        MATCH (a:Medicine {id: {id}})
        MATCH (b:EffectivenessInfo {id: {info}})
        MERGE (a)-[:IS_%s]->(b);
        """ % info['effectiveness'].replace(" ", "_"),
        id=medicine['_id'],
        info=info['id'])

def new_disease_node(tx, ds):
    tx.run("""
        MERGE (a:Disease {id: {id}})
            ON CREATE SET a.id={id}
        """,
        id=ds.title())    

def new_disease_rel(tx, ds, _cls, _id, _rel="IN_RELATION_TO"):
    tx.run("""
        MATCH (a:%s {id: {id}})
        MATCH (b:Disease {id: {ds}})
        MERGE (a)-[:%s]->(b);
        """ % (_cls, _rel),
        ds=ds.title(),
        id=_id)

def new_dosing_info_node(tx, info):
    tx.run("""
        MERGE (info:DosingInfo {id: {id}})
            ON CREATE SET info.id={id},
                info.text={text}
        """,
        id=info['id'],
        text=info['text'])

def new_dosing_info_rel(tx, info, medicine):
    tx.run("""
        MATCH (a:Medicine {id: {medicine}})
        MATCH (b:DosingInfo {id: {info}})
        MERGE (a)-[:IS_DOSED_WITH]->(b);
        """,
        medicine=medicine['_id'],
        info=info['id'])

def new_adverse_effect_node(tx, adv):
    tx.run("""
        MERGE (adv:AdverseEffect {id: {id}})
            ON CREATE SET adv.id={id},
                adv.text={text}
        """,
        id=adv['id'],
        text=adv['text'])

def new_adverse_effect_rel(tx, adv, medicine):
    tx.run("""
        MATCH (a:Medicine {id: {medicine}})
        MATCH (b:AdverseEffect {id: {adv}})
        MERGE (a)-[:MAY_CAUSE_ADVERSE_EFFECT]->(b);
        """,
        medicine=medicine['_id'],
        adv=adv['id'])

def new_drug_interaction_node(tx, drug):
    tx.run("""
        MERGE (di:DrugInteraction {id: {id}})
            ON CREATE SET di.id={id},
                di.text={text},
                di.rating={rating},
                di.severity={severity},
                di.occurence={occurence},
                di.evidence={evidence}
        """,
        id=drug['id'],
        text=drug['content'],
        rating=drug['interactionRating'],
        severity=drug['severityRating'],
        occurence=drug['occurenceRating'],
        evidence=drug['levelOfEvidence'])

def new_drug_interaction_rel(tx, di, medicine):
    tx.run("""
        MATCH (a:Medicine {id: {medicine}})
        MATCH (b:DrugInteraction {id: {di}})
        MERGE (a)-[:HAS_%s_INTERACTION]->(b);
        """ % di['interactionRating'].upper().replace(" ", "_"),
        medicine=medicine['_id'],
        di=di['id'])

def new_adverse_effect_rel(tx, adv, medicine):
    tx.run("""
        MATCH (a:Medicine {id: {medicine}})
        MATCH (b:AdverseEffect {id: {adv}})
        MERGE (a)-[:MAY_CAUSE_ADVERSE_EFFECT]->(b);
        """,
        medicine=medicine['_id'],
        adv=adv['id'])

def new_drug_node(tx, drug):
    tx.run("""
        MERGE (drug:Drug {id: {id}})
            ON CREATE SET drug.id={id}
        """,
        id=drug.title())

def new_drug_rel(tx, drug, _cls, _id, _rel="IN_RELATION_TO"):
    tx.run("""
        MATCH (a:%s {id: {id}})
        MATCH (b:Drug {id: {d}})
        MERGE (a)-[:%s]->(b);
        """ % (_cls, _rel),
        d=drug.title(),
        id=_id)

def new_hsi_node(tx, hsi):
    tx.run("""
        MERGE (hsi:HerbSuplementsInteraction {id: {id}})
            ON CREATE SET hsi.id={id},
                hsi.text={text}
        """,
        id=hsi['id'],
        text=hsi['text'])

def new_hsi_rel(tx, hsi, medicine):
    tx.run("""
        MATCH (a:Medicine {id: {medicine}})
        MATCH (b:HerbSuplementsInteraction {id: {hsi}})
        MERGE (a)-[:MAY_INTERACT]->(b);
        """,
        medicine=medicine['_id'],
        hsi=hsi['id'])

def new_hs_node(tx, hs):
    tx.run("""
        MERGE (hs:HerbSuplement {id: {id}})
            ON CREATE SET hs.id={id}
        """,
        id=hs.title())

def new_hs_rel(tx, hs, _cls, _id, _rel="IN_RELATION_TO"):
    tx.run("""
        MATCH (a:%s {id: {id}})
        MATCH (b:HerbSuplement {id: {hs}})
        MERGE (a)-[:%s]->(b);
        """ % (_cls, _rel),
        hs=hs.title(),
        id=_id)

def new_fi_node(tx, fi):
    tx.run("""
        MERGE (fi:FoodInteraction {id: {id}})
            ON CREATE SET fi.id={id},
                fi.text={text}
        """,
        id=fi['id'],
        text=fi['text'])

def new_fi_rel(tx, fi, medicine):
    tx.run("""
        MATCH (a:Medicine {id: {medicine}})
        MATCH (b:FoodInteraction {id: {fi}})
        MERGE (a)-[:MAY_INTERACT]->(b);
        """,
        medicine=medicine['_id'],
        fi=fi['id'])

def new_food_node(tx, food):
    tx.run("""
        MERGE (food:Food {id: {id}})
            ON CREATE SET food.id={id}
        """,
        id=food.title())

def new_food_rel(tx, food, _cls, _id, _rel="IN_RELATION_TO"):
    tx.run("""
        MATCH (a:%s {id: {id}})
        MATCH (b:Food {id: {food}})
        MERGE (a)-[:%s]->(b);
        """ % (_cls, _rel),
        food=food.title(),
        id=_id)

def new_lti_node(tx, lti):
    tx.run("""
        MERGE (lti:LaboratoryInteraction {id: {id}})
            ON CREATE SET lti.id={id},
                lti.text={text}
        """,
        id=lti['id'],
        text=lti['text'])

def new_lti_rel(tx, lti, medicine):
    tx.run("""
        MATCH (a:Medicine {id: {medicine}})
        MATCH (b:LaboratoryInteraction {id: {lti}})
        MERGE (a)-[:MAY_INTERACT]->(b);
        """,
        medicine=medicine['_id'],
        lti=lti['id'])

def new_lt_node(tx, lt):
    tx.run("""
        MERGE (lt:LaboratoryTest {id: {id}})
            ON CREATE SET lt.id={id}
        """,
        id=lt.title())

def new_lt_rel(tx, lt, _cls, _id, _rel="IN_RELATION_TO"):
    tx.run("""
        MATCH (a:%s {id: {id}})
        MATCH (b:LaboratoryTest {id: {lt}})
        MERGE (a)-[:%s]->(b);
        """ % (_cls, _rel),
        lt=lt.title(),
        id=_id)

def new_di_node(tx, di):
    tx.run("""
        MERGE (di:DiseaseInteraction {id: {id}})
            ON CREATE SET di.id={id},
                di.text={text}
        """,
        id=di['id'],
        text=di['text'])

def new_di_rel(tx, di, medicine):
    tx.run("""
        MATCH (a:Medicine {id: {medicine}})
        MATCH (b:DiseaseInteraction {id: {di}})
        MERGE (a)-[:MAY_INTERACT]->(b);
        """,
        medicine=medicine['_id'],
        di=di['id'])

def new_mai_node(tx, mai):
    tx.run("""
        MERGE (mai:MechanismOfActionInteraction {id: {id}})
            ON CREATE SET mai.id={id},
                mai.text={text}
        """,
        id=mai['id'],
        text=mai['text'])

def new_mai_rel(tx, mai, medicine):
    tx.run("""
        MATCH (a:Medicine {id: {medicine}})
        MATCH (b:MechanismOfActionInteraction {id: {mai}})
        MERGE (a)-[:MAY_INTERACT]->(b);
        """,
        medicine=medicine['_id'],
        mai=mai['id'])

def new_ma_node(tx, ma):
    tx.run("""
        MERGE (ma:MechanismOfAction {id: {id}})
            ON CREATE SET ma.id={id}
        """,
        id=ma.title())

def new_ma_rel(tx, ma, _cls, _id, _rel="IN_RELATION_TO"):
    tx.run("""
        MATCH (a:%s {id: {id}})
        MATCH (b:MechanismOfAction {id: {ma}})
        MERGE (a)-[:%s]->(b);
        """ % (_cls, _rel),
        ma=ma.title(),
        id=_id)

def new_pki_node(tx, pki):
    tx.run("""
        MERGE (pki:PharmacokineticsInteraction {id: {id}})
            ON CREATE SET pki.id={id},
                pki.text={text}
        """,
        id=pki['id'],
        text=pki['text'])

def new_pki_rel(tx, pki, medicine):
    tx.run("""
        MATCH (a:Medicine {id: {medicine}})
        MATCH (b:PharmacokineticsInteraction {id: {pki}})
        MERGE (a)-[:MAY_INTERACT]->(b);
        """,
        medicine=medicine['_id'],
        pki=pki['id'])

def new_pk_node(tx, pk):
    tx.run("""
        MERGE (pk:Pharmacokinetics {id: {id}})
            ON CREATE SET pk.id={id}
        """,
        id=pk.title())

def new_pk_rel(tx, pk, _cls, _id, _rel="IN_RELATION_TO"):
    tx.run("""
        MATCH (a:%s {id: {id}})
        MATCH (b:Pharmacokinetics {id: {pk}})
        MERGE (a)-[:%s]->(b);
        """ % (_cls, _rel),
        pk=pk.title(),
        id=_id)

def new_medicine_node(tx, medicine):
    tx.run("""
        MERGE (medicine:Medicine {id: {id}})
        ON CREATE SET medicine.id = {id},
            medicine.name = {name},
            medicine.url = {url},
            medicine.family_name = {family_name},
            medicine.description = {description},
            medicine.history = {history},
            medicine.used_for = {used_for}
        """,
        id=medicine.get('_id'),
        name=medicine.get('name').title(),
        url=medicine.get('url'),
        family_name=medicine.get('familyName'),
        description=medicine.get('description'),
        history=medicine.get('history'),
        used_for=medicine.get('peopleUseThisFor'))

def insert_medicine(tx, medicine):
    print("Inserting the medicine: {0} (#{1})".format(medicine['name'], medicine['_id']))
    new_medicine_node(tx, medicine)

    if medicine.get('scientficNames'):
        for sci_name in medicine.get('scientficNames'):
            new_scientific_name_node(tx, sci_name)
            new_scientific_name_rel(tx, sci_name, medicine)

    if medicine.get('alsoKnowAs'):
        for synonymous in medicine.get('alsoKnowAs'):
            new_synonymous_node(tx, synonymous)
            new_synonymous_rel(tx, synonymous, medicine)
    
    if medicine.get('references'):
        for reference in medicine.get('references'):
            new_reference_node(tx, reference)
            new_reference_rel(tx, reference, "medicine", medicine['_id'])
    
    if medicine.get('safetyInfo'):
        for info in [x for x in medicine.get('safetyInfo') if x.get('safety') != None]: # Fix
            info['id'] = hashlib.md5(info['text'].encode()).hexdigest()
            
            new_safety_info_node(tx, info)
            new_safety_info_rel(tx, info, medicine)

            if info.get('context'):
                new_context_node(tx, info.get('context'))
                new_context_rel(tx, info.get('context'), "SafetyInfo", info['id'])
            
            for ref in info.get('references'):
                new_reference_node(tx, ref)
                new_reference_rel(tx, ref, "SafetyInfo", info['id'])
    
    if medicine.get('effectivenessInfo'):
        for info in medicine.get('effectivenessInfo'):
            info['id'] = hashlib.md5(info['text'].encode()).hexdigest()
            
            new_effectiveness_node(tx, info)
            new_effectiveness_rel(tx, info, medicine)
            
            new_disease_node(tx, info['disease'])
            new_disease_rel(tx, info['disease'], "EffectivenessInfo", info['id'])

            for ref in info.get('references'):
                new_reference_node(tx, ref)
                new_reference_rel(tx, ref, "EffectivenessInfo", info['id'])

    if medicine.get('dosingInfo'):
        for info in medicine.get('dosingInfo'):
            info['id'] = hashlib.md5(info['text'].encode()).hexdigest()
            
            new_dosing_info_node(tx, info)
            new_dosing_info_rel(tx, info, medicine)

            if info.get('disease'):
                new_disease_node(tx, info['disease'])
                new_disease_rel(tx, info['disease'], "DosingInfo", info['id'], "IS_DOSED_FOR")

            if info.get('for'):            
                new_context_node(tx, info['for'])
                new_context_rel(tx, info['for'], 'DosingInfo', info['id'])

            for ref in info.get('references'):
                new_reference_node(tx, ref)
                new_reference_rel(tx, ref, "DosingInfo", info['id'])
    
    if medicine.get('adverseEffects'):
        adv = medicine.get('adverseEffects')

        if adv.get('text'):
            for text in adv.get('text'):
                text['id'] = hashlib.md5(text['text'].encode()).hexdigest()

                new_adverse_effect_node(tx, text)
                new_adverse_effect_rel(tx, text, medicine)

                for ref in text.get('references'):
                    new_reference_node(tx, ref)
                    new_reference_rel(tx, ref, "AdverseEffect", text['id'])
        
        if adv.get('domains'):
            for domain in adv.get('domains'):
                domain['id'] = hashlib.md5(domain['text'].encode()).hexdigest()

                new_adverse_effect_node(tx, domain)
                new_adverse_effect_rel(tx, domain, medicine)

                new_context_node(tx, domain['title'])
                new_context_rel(tx, domain['title'], "AdverseEffect", domain['id'])

                for ref in domain.get('references'):
                    new_reference_node(tx, ref)
                    new_reference_rel(tx, ref, "AdverseEffect", domain['id'])
    
    if medicine.get('drugInteractions'):
        for drug in medicine.get('drugInteractions'):
            drug['id'] = hashlib.md5(drug['content'].encode()).hexdigest()

            new_drug_interaction_node(tx, drug)
            new_drug_interaction_rel(tx, drug, medicine)

            new_drug_node(tx, drug['title'])
            new_drug_rel(tx, drug['title'], "DrugInteraction", drug['id'], "WHEN_USED_WITH")

            for ref in drug.get('references'):
                new_reference_node(tx, ref)
                new_reference_rel(tx, ref, "DrugInteraction", drug['id'])
    
    if medicine.get('herbsAndSuplementsInteractions'):
        for hsi in medicine.get('herbsAndSuplementsInteractions'):
            hsi['id'] = hashlib.md5(hsi['text'].encode()).hexdigest()

            new_hsi_node(tx, hsi)
            new_hsi_rel(tx, hsi, medicine)

            new_hs_node(tx, hsi['title'])
            new_hs_rel(tx, hsi['title'], "HerbSuplementInteraction", hsi['id'], "WHEN_USED_WITH")

            for ref in hsi.get('references'):
                new_reference_node(tx, ref)
                new_reference_rel(tx, ref, "HerbSuplementInteraction", hsi['id'])
    
    if medicine.get('foodInteractions'):
        for fi in medicine.get('foodInteractions'):
            fi['id'] = hashlib.md5(fi['text'].encode()).hexdigest()

            new_fi_node(tx, fi)
            new_fi_rel(tx, fi, medicine)

            new_food_node(tx, fi['title'])
            new_food_rel(tx, fi['title'], "FoodInteraction", fi['id'], "WHEN_CONSUMED_WITH")

            for ref in fi.get('references'):
                new_reference_node(tx, ref)
                new_reference_rel(tx, ref, "FoodInteraction", fi['id'])
    
    if medicine.get('labTestsInteractions'):
        for lti in medicine.get('labTestsInteractions'):
            lti['id'] = hashlib.md5(lti['text'].encode()).hexdigest()

            new_lti_node(tx, lti)
            new_lti_rel(tx, lti, medicine)

            new_lt_node(tx, lti['title'])
            new_lt_rel(tx, lti['title'], "LaboratoryInteraction", lti['id'], "WHEN_TESTED_AGAINST")

            for ref in lti.get('references'):
                new_reference_node(tx, ref)
                new_reference_rel(tx, ref, "LaboratoryInteraction", lti['id'])

    if medicine.get('diseaseInteractions'):
        for disease in medicine.get('diseaseInteractions'):
            disease['id'] = hashlib.md5(disease['text'].encode()).hexdigest()

            new_di_node(tx, disease)
            new_di_rel(tx, disease, medicine)

            new_disease_node(tx, disease['title'])
            new_disease_rel(tx, disease['title'], "DiseaseInteraction", disease['id'], _rel="MAY_CORRELATES")

            for ref in disease.get('references'):
                new_reference_node(tx, ref)
                new_reference_rel(tx, ref, "DiseaseInteraction", disease['id'])
    
    if medicine.get('mechanismOfAction'):
        for ma in medicine.get('mechanismOfAction'):
            ma['id'] = hashlib.md5(ma['text'].encode()).hexdigest() 

            new_mai_node(tx, ma)
            new_mai_rel(tx, ma, medicine)

            new_ma_node(tx, ma['title'])
            new_ma_rel(tx, ma['title'], "MechanismOfActionInteraction", ma['id'], _rel="MAY_CAUSE")

            for ref in ma.get('references'):
                new_reference_node(tx, ref)
                new_reference_rel(tx, ref, "MechanismOfActionInteraction", ma['id'])
    
    if medicine.get('pharmacokinetics'):
        for pk in medicine.get('pharmacokinetics'):
            pk['id'] = hashlib.md5(pk['text'].encode()).hexdigest() 

            new_pki_node(tx, pk)
            new_pki_rel(tx, pk, medicine)

            new_pk_node(tx, pk['title'])
            new_pk_rel(tx, pk['title'], "PharmacokineticsInteraction", pk['id'], _rel="MAY_HAVE_SOME_IMPACT")

            for ref in ma.get('references'):
                new_reference_node(tx, ref)
                new_reference_rel(tx, ref, "PharmacokineticsInteraction", pk['id'])

if __name__ == '__main__':
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=basic_auth("neo4j", "naturalmed"))
    client = MongoClient(NATMED_CN)
    col = client[NATMED_DB][NATMED_COL]

    print("Beggining Neo4j Session\n")
    session = driver.session() 
    
    session_start = time.time()

    try:
        tx_count = 0
        
        for medicine in list(col.find()):
            tx_start = time.time()

            try:
                with session.begin_transaction() as tx:
                    tx_count += 1
                    print("Beggining Neo4j Transaction: {0}".format(tx_count))
                    insert_medicine(tx, medicine)
            except Exception:
                print("There has been an error!!")
            finally:
                print("Ending Neo4j Transaction\n")

                tx_end = time.time()

                print("This transaction has elapsed in {0} seconds\n".format(tx_end - tx_start))
    finally:
        print("Ending Neo4j Session")
        session.close()
        print("Ending Script\n")

        session_end = time.time()

        print("The entire session has elapsed in {0} seconds".format(session_end - session_start))
