print("category");
db.getCollection('full_health_care_meta').aggregate([
    { "$unwind": { "path": "$categories" } },
    { "$project": { "category": "$categories" } },
    { "$unwind": { "path": "$category" } },
    { "$group": { "_id": "$category" } }
]).forEach(function (doc) {
   print('"' + doc["_id"] + '"');
});