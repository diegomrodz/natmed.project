# Discovering Natural Medicine Products using Data

This project was started as a way to explore the interesting topic of Natural Medicines and its relation with diseases and other substances using many aspect of Data Science, from Data Mining to Machine Learning.

This repository contains all scripts used during this exploration, including the crawlers, docker containers, data treatment and importing scripts and notebooks used for testing concepts.

## Datasets

The main dataset was the website naturalmedicines.therapeuticresearch.com which contains more than 2.000 naural medicines and its interaction with diseases and other substances.

Also, its was used the pubmed.com for getting relevant data about the many articles that were referenced in the previous database.

I also has a brief look at the Amazon Product Reviews Dataset, however I couldn't find any information relevant for the domain that I was researching.

## Databases

### Natmed Graph Model on Neo4j

Since the most important thing at this exploration was the connections between the many substances and diseases, I thinked it would be a good opportunity for using a Graph Database. So, I created a crawler that would look at which one of the pages of the site and dump the data into a MongoDB database. Once executed, I would use an script which would import this data into the Neo4j in the model designed for best capture the relation between the many entities.

The first version of the model remembered a lot the structured found on the website crawled:

![alt tag](https://pbs.twimg.com/media/C8WNgY9XcAAD8rD.jpg:large)

Once I better understood the relations, the first step would be to refactor this model using the Cypher Language and the final result was the following:

![alt tag](https://pbs.twimg.com/media/C8WNiIVXYAAg9vb.jpg:large)
