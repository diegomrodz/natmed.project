var mongo = require('mongodb').MongoClient;
var neo4j = require('node-neo4j');

var neo_api = new neo4j("http://neo4j:natural_med@localhost:7474");

var count = 1047135; // get via mongo

mongo.connect("mongodb://localhost:27017/natural_med", function (err, db) {
	if (err) {
		console.error("Error while connecting to mongodb.");
		db.close();
	} else {
		var collection = db.collection('full_health_care_meta');

		var insertedCount = 0;
		var tCount = 0;
		var tID = "";

		neo_api.beginTransaction(function (err, result) {
			if (err) { throw err; }

			tID = result["_id"];
		});

		collection.aggregate([
		    { "$unwind": { "path": "$categories" } },
		    { "$project": { "productID": "$asin", "category": "$categories" } },
		    { "$unwind": { "path": "$category" } },
		    { "$project": { "productID": 1, "category": 1 } },
		    { "$skip": 15200 }
		]).each(function (err, doc) {
			if (err || !doc) { return; }

			neo_api.addStatementsToTransaction(tID, `
				MATCH (a:Product {productID: "${doc['productID']}" })
				MATCH (b:Category {name: "${doc['category']}"})
				MERGE (a)-[:BELONGS_TO]->(b);`, function (err, result) {

				if (++tCount >= 100) {
					neo_api.commitTransaction(tID, function (err, result) {
						if (err) {
							console.log("Error while commiting transaction");
						}

						insertedCount += 1;
						tCount = 0;

						console.log(`Inserted ~${insertedCount * 100} docs of a total ${count}`);

						neo_api.beginTransaction(function (err, result) {
							if (err) { throw err; }

							tID = result["_id"];
						});
					});
				}
			});
		});
	}
});
