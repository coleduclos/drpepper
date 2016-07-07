import json, urllib, boto3

print "Beginning Script..."

url = "http://www.carqueryapi.com/api/0.3/?cmd=getMakes"
out_json = {}
out_file = "cars.json"
bucket_name = "bugcrowd-infrastructure-interview"
bucket_key = "coleduclos/cars.json"
car_model_key = "car_model"
car_count_key = "car_count"

# Fetch the json data from the url
print "Fetching data from %s" % url
data = urllib.urlopen(url)
json_data = json.load(data)

# Loop through the data and add to our out_json
for car in json_data['Makes']:
	make_country =  car['make_country']
	make_display = car['make_display']

	# Check if make country already exists in dictionary
	if make_country not in out_json:
		out_json[make_country] = {}
		out_json[make_country][car_model_key] = [make_display]
		out_json[make_country][car_count_key] =  1
	else:
		out_json[make_country][car_model_key].append(make_display)
		out_json[make_country][car_count_key] = out_json[make_country][car_count_key] + 1

# Loop through each country in out_json and order cars (descending)
for country in out_json:
	out_json[country][car_model_key] = sorted(out_json[country][car_model_key], reverse=True) 

# Write the json object to the out_file
print "Wrting results to %s" % out_file
fd = open(out_file, 'w')
fd.write(json.dumps(out_json, indent=4, sort_keys=True))

# Upload to AWS S3 bucket
print "Uploading results to AWS S3 bucket %s/%s" % (bucket_name, bucket_key)
s3 = boto3.resource('s3')
s3.Bucket(bucket_name).put_object(Key=bucket_key, Body=json.dumps(out_json, indent=4, sort_keys=True))

print "FINISHED"