import json

country = ''
state = ''
city = ''

url = 'https://maps.googleapis.com/maps/api/geocode/json?key=' + input_data['key']  + '&address="' + input_data['address'] + '"'
req = requests.get(url).json()

for item in range(len(req['results'][0]['address_components'])):
	if req['results'][0]['address_components'][item]['types'][0] == 'country':
		country = str(req['results'][0]['address_components'][item]['long_name'])
	elif req['results'][0]['address_components'][item]['types'][0] == 'administrative_area_level_1':
		state = str(req['results'][0]['address_components'][item]['long_name'])
	elif req['results'][0]['address_components'][item]['types'][0] == 'locality':
		city = str(req['results'][0]['address_components'][item]['long_name'])

return {'City' : city, 'State': state , 'Country': country }