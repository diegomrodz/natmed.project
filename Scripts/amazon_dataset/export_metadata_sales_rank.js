print("productID,category,salesRank");
db.getCollection('full_health_care_meta').aggregate([
    { "$unwind": { "path": "$salesRank" } },
    { "$project": { "productID": "$asin", "salesRank": "$salesRank" } },
    { "$limit": 10000 }
]).forEach(function (doc) {
    var k = Object.keys(doc["salesRank"])[0];
	print(doc['productID'] + ",'" + k + "'," + doc["salesRank"][k]);
});