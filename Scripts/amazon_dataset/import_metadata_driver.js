var mongo = require('mongodb').MongoClient;
var neo4j = require('node-neo4j');

var neo_api = new neo4j("http://neo4j:natural_med@localhost:7474");

mongo.connect("mongodb://localhost:27017/natural_med", function (err, db) {
	if (err) {
		console.error("Error while connecting to mongodb.");
		db.close();
	} else {
		var collection = db.collection('full_health_care_meta');

		collection.count(function (err, count) {
			if (err) {
				return db.close();
			}

			var insertedCount = 0;

			collection.find().each(function (err, doc) {
				if (err || !doc) { return; }

				neo_api.cypherQuery(`
MERGE (product:Product {productID: "${doc['asin']}"}) 
ON CREATE SET product.title = "${doc['title']}",
			  product.description = "${doc['description']}",
			  product.imageUrl = "${doc['imUrl']}";`, function (err, result) {
			  	
			  	if (++insertedCount % 100 == 0) {
			  		console.log(`Inserted ~${insertedCount} docs of a total ${count}`);
			  	}
			  });
			});

			console.log(count);
		});
	}
});
