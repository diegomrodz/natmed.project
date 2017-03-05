print("productID,category");
db.getCollection('full_health_care_meta').aggregate([
    { "$unwind": { "path": "$categories" } },
    { "$project": { "productID": "$asin", "category": "$categories" } },
    { "$unwind": { "path": "$category" } },
    { "$project": { "productID": 1, "category": 1 } },
    { "$limit": 10000 }
]).forEach(function (doc) {
   print(doc["productID"] + ",'" + doc["category"] + "'");
})