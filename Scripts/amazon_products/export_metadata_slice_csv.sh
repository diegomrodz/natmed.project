mongoexport.exe --db=natural_med 
				--collection=full_health_care_meta 
				--limit=1000 
				--type=csv --fields asin,title,description,imUrl 
				--out=../../Dumps/natural_metadata.csv

mongo.exe --quiet natural_med export_metadata_also_bought.js > ../../Dumps/natural_metadata_also_bought.csv

mongo.exe --quiet natural_med export_metadata_also_viewed.js > ../../Dumps/natural_metadata_also_viewed.csv

mongo.exe --quiet natural_med export_metadata_categories.js > ../../Dumps/natural_metadata_categories.csv

mongo.exe --quiet natural_med export_metadata_product_categories.js > ../../Dumps/natural_metadata_product_categories.csv

mongo.exe --quiet natural_med export_metadata_sales_rank.js > ../../Dumps/natural_metadata_sales_rank.csv

mongo.exe --quiet natural_med export_reviews_users.js > ../../Dumps/natural_reviews_users.csv
