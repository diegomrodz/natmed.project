print("productID,relatedTo");
db.getCollection('full_health_care_meta').aggregate([
    { "$unwind": { "path": "$related.also_viewed" } },
    { "$project": { "productID": "$asin", "relatedTo": "$related.also_viewed" } },
    { "$limit": 10000 }
]).forEach(function (doc) {
   print(doc["productID"] + "," + doc["relatedTo"]);
})