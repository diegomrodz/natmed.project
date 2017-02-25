# You will need to convert the metadata gzip into a strict.json file
mongoimport.exe meta_Health_and_Personal_Care.strict.json 
				--db=natural_med 
				--collection=full_health_care_meta 
				
mongoimport.exe reviews_Health_and_Personal_Care.json 
				--db=natural_med 
				--collection=full_health_care_reviews

mongoimport.exe Health_and_Personal_Care_5.json 
				--db=natural_med 
				--collection=partial_health_care_reviews
