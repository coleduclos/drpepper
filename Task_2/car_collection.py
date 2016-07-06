import json, urllib

print "Beginning Script..."

url = "http://www.carqueryapi.com/api/0.3/?cmd=getMakes"

print "Fetching data from %s" % url

# Fetch the json data from the url
data = urllib.urlopen(url)
json_data = json.load(data)

out_json = {}
out_file = "cars.json"

# Loop through the data and add to our out_jsonput JSON
for car in json_data['Makes']:
	make_country =  car['make_country']
	make_display = car['make_display']

	# Check if make country already exists in dictionary
	if make_country not in out_json:
		out_json[make_country] = {}
		out_json[make_country]['car_models'] = [make_display]
		out_json[make_country]['car_count'] =  1
	else:
		out_json[make_country]['car_models'].append(make_display)
		out_json[make_country]['car_count'] = out_json[make_country]['car_count'] + 1

for country in out_json:
	out_json[country]['car_models'] = sorted(out_json[country]['car_models'],reverse=True) 

print "Wrting results to %s" % out_file
fd = open(out_file, 'w')
fd.write(json.dumps(out_json, indent=4, sort_keys=True))
