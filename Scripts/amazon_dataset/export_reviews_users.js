print("id,name");
db.getCollection('full_health_care_reviews').aggregate([
    { "$project": { "_id": "$reviewerID", "name": "$reviewerName" } }
]).forEach(function (doc) {
   print("'" + doc['_id'] + "','" + escape(doc['name']) + "'");
});