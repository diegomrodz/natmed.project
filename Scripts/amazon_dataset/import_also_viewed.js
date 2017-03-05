var mongo = require('mongodb').MongoClient;
var neo4j = require('node-neo4j');
var async = require('async');
var _ = require('underscore');
var json2csv = require('json2csv');
var fs = require('fs');

var neo4j = require('neo4j-driver').v1;
var driver = neo4j.driver("bolt://localhost", neo4j.auth.basic("neo4j", "natural_med"));

var BATCH_SIZE = 10000;
var GDB_FILEPATH = "C:\\Users\\diego\\NaturalMedicineProject\\Datasets\\graphdb\\import\\import_data.csv";

var FIELDS = ["productID", "relatedTo"];

var STATEMENT = `
USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM "file:\\\\import_data.csv" AS row
MATCH (a:Product {productID: row.productID})
MATCH (b:Product {productID: row.relatedTo})
MERGE (a)-[:HAS_ALSO_VIEWED]->(b);
`;

function getDocuments(collection, step) {
	return function (callback) {
		collection.aggregate([
			{ "$unwind": { "path": "$related.also_viewed" } },
    		{ "$project": { "productID": "$asin", "relatedTo": "$related.also_viewed" } },
			{ "$skip": step },
			{ "$limit": BATCH_SIZE }
		])
		.toArray(function (err, items) {
			if (err) {
				callback(err);
			} else {
				console.log(`${items.length} staged for commit.`);
				callback(null, items);
			}
		});
	}
}

function getCount(collection, callback) {
	collection.aggregate([
		{ "$unwind": { "path": "$related.also_viewed" } },
    	{ "$project": { "productID": "$asin", "relatedTo": "$related.also_viewed" } },
	    { "$count": "count" }
	], function(err, result) {
		callback(null, result[0]["count"]);
	});
}

function connect(callback) {
	mongo.connect("mongodb://localhost:27017/natural_med", function (err, db) {
		if (err) {
			console.error("Error while connecting to mongodb.");
			db.close();
		} else {
			var collection = db.collection('full_health_care_meta');
			callback(db, collection);
		}
	});
}

function importDocuments(collection, step, count, endAll) {
	async.waterfall([
		getDocuments(collection, step),
		function (array, callback) {
			callback(null, array, driver.session());
		},
		function (array, session, callback) {
			json2csv({data: array, fields: FIELDS}, function (err, csv) {
				if (err) {
					return callback(err);
				}

				callback(null, session, csv);
			});
		},
		function (session, csv, callback) {
			fs.writeFile(GDB_FILEPATH, csv, function (err) {
				if (err) {
					return callback(err);
				}

				callback(null, session);
			});
		},
		function (session, callback) {
			session.run(STATEMENT)
			.subscribe({
			  	onCompleted: function () {
			  		session.close();
			  		callback(null);
			  	},
			  	onError: function (err) {
			  		session.close();
			  		callback(err);
			  	}
			});
		},
		function (callback) {
			fs.unlink(GDB_FILEPATH, function (err) {
				callback(null);
			});
		}
	], function (err, result) {
		if (err) {
			console.log(`Batch #${step} com erro.`);
			console.log(err);			
		} else {
			console.log(`Batch #${step} completa de ${count} restantes.`);
		}

		endAll(null);
	});
}

connect(function (db, collection) {
	async.waterfall([
		function (callback) {
			getCount(collection, callback);
		},
		function (count, callback) {
			var steps = _.range(0, count, BATCH_SIZE);

			async.waterfall(
				_.map(steps, function (step) {
					return function(callback2) {
						importDocuments(collection, step, count, callback2);
					};
				}),
				function (err, result) {
					callback(null);
				}
			);
		}
	], function (err, results) {
		db.close();
	});
});
