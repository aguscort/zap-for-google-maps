import json
import requests
import re
import csv


timeout = 2
country = ''
state = ''
city = ''
wordFound = False
results = []
addresses= []
loops_num = 0
input_data = {"key" :  "", \
"storage_key" : ""}


def remove_dups(locations):
    p_locations = []
    for i in locations:
        i = tuple(i)
        p_locations.append(i)
    return list(set(p_locations))

def address_treatment(address, level=2):
    f_string = address.split(" ")
    for i in range(len(f_string)):
        f_string[i] = re.sub(r',', '', f_string[i])
    f_string = set(f_string)
    f_string = " ".join(f_string)
    if level == 2:        
        f_string =" ".join(f_string.split('Area'))
        f_string =" ".join(f_string.split('Greater'))
        f_string =" ".join(f_string.split('Bay'))
    return f_string


def get_url(location, level):    
    return 'https://maps.googleapis.com/maps/api/geocode/json?key=' + input_data['key']  + '&address="' + address_treatment(location) + '"'


def get_address(address, level):    
    country = ''
    state = ''
    city = ''
    wordFound = False

    url = get_url(address, level) 
    req = requests.get(url, timeout=timeout).json()
    try:
        for word in range(len(req['results'][0]['address_components'])):
            if req['results'][0]['address_components'][word]['types'][0] == 'country':
                country = str(req['results'][0]['address_components'][word]['long_name'])
            elif req['results'][0]['address_components'][word]['types'][0] == 'administrative_area_level_1':
                state = str(req['results'][0]['address_components'][word]['long_name'])
            elif req['results'][0]['address_components'][word]['types'][0] == 'locality':
                city = str(req['results'][0]['address_components'][word]['long_name'])
        
            list_words = address.split(" ")
            to_test = country + ' ' + state + ' ' + city
            for i in range(len(list_words)):
                 if  to_test.find(list_words[i]) != -1:
                     wordFound = True
                     break
    except:
        country = ''
        state = 'Error'
        city = ''
        wordFound = False

    return address, city, state , country,  wordFound 


with open("test locations.csv", 'r', encoding='UTF8') as f:
    reader = csv.reader(f)
    addresses = remove_dups(list(reader))

for item in range(len(addresses)):
    address = addresses[item][0]
    address, city, state , country,  wordFound = get_address(address,1)
    if  (city == '' and state != ''):
        address, city, state , country,  wordFound = get_address(address,2)
     
    results.append ( {'location' : address, 'City' : city, 'State': state , 'Country': country, 'Status' : wordFound })
    loops_num += 1
    print (str(loops_num) + ' - location: ' + address + ' | City: ' + city + ' | State: ' + state + ' | Country: ' + country + ' | Status: ' +  str(wordFound))
