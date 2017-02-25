import json
import gzip

def parse(path):
	g = gzip.open(path, 'r')
	for l in g:
		yield json.dumps(eval(l))

f = open("meta_Health_and_Personal_Care.strict.json", 'w')
for l in parse("meta_Health_and_Personal_Care.json.gz"):
	f.write(l + '\n')

f.close()