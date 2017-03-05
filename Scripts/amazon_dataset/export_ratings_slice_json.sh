mongoexport.exe --db=natural_med 
				--collection=full_health_care_reviews 
				--limit=10000 
				--out=../Dumps/ratings_dump.json --jsonArray
