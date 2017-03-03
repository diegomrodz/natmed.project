mongoexport.exe --db=natural_med --collection=full_health_care_meta --limit=1000 --type=csv --fields asin,title,description,imUrl --out=../Dumps/natural_metadata.csv

mongo.exe --quiet natural_med export_amazon_metadata_also_bought_slice.js > ../Dumps/natural_metadata_also_bought.csv

mongo.exe --quiet natural_med export_amazon_metadata_also_viewed_slice.js > ../Dumps/natural_metadata_also_viewed.csv

mongo.exe --quiet natural_med export_amazon_metadata_categories_slice.js > ../Dumps/natural_metadata_categories.csv

mongo.exe --quiet natural_med export_amazon_metadata_product_categories.js > ../Dumps/natural_metadata_product_categories.csv
