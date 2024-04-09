# zap-for-google-maps


## Statement:

A location is passed into the Zap from another app in [Zapier](https://zapier.com).

Using the Zapier Webhook Integration the goal is this data will query [Google Maps Geocoding API](https://developers.google.com/maps/documentation/geocoding/start) so it returns full address details (City, State, Country).

The big scope is this: the data is stored in [Close.io](https://close.io) and needed to be passed through Google Maps API so that it returns a city, state and coutry, because those are fields stored in the CRM, where the final result should be stored.


## Workflow:

![Send Location](https://github.com/aguscort/zap-for-google-maps/raw/master/images/zap-google-maps.png "Send Location")
---
### Step 1:

#### From:

#### To:

#### Parameters:

![Parameters](https://github.com/aguscort/zap-for-google-maps/raw/master/images/step1_parameters.png "Step 1 Parameters")

#### Step Description: 
We use the Dropbox as a trigger: as soon a file is saved into a folder, the zap is launched.

#### Reference Link:

#### Aditional Guidance:

---
### Step 2:

#### From:

##### To:

#### Parameters:

![Parameters](https://github.com/aguscort/zap-for-google-maps/raw/master/images/step2_parameters.png "Step 2 Parameters")

#### Step Description:
Get the info from the CSV file in order to be treated in further steps.

#### Code:

```python
import requests

req = requests.get(input_data['file_link']).text
addresses = "**".join(list(req.splitlines()))

return {'addreses' : addresses}
```
#### Reference Link:

#### Aditional Guidance:

---
### Step 3:

#### From:

#### To:

#### Parameters:

![Parameters](https://github.com/aguscort/zap-for-google-maps/raw/master/images/step3_parameters.png "Step 3 Parameters")

#### Step Description:
The strings are used through Google Maps to normalize the addresses. Some mechanisms are settled in order to improve the search and get better hit rate.

#### Code:

```python
import requests
import re
import json

country = ''
state = ''
city = ''
wordFound = False
results = []
addresses= []
loops_num = 0

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

def get_address(address, level):    
    country = ''
    state = ''
    city = ''
    wordFound = False

    url = 'https://maps.googleapis.com/maps/api/geocode/json?key=' + input_data['key']  + '&address="' + address_treatment(address) + '"'
    req = requests.get(url).json()
    try:
        for word in range(len(req['results'][0]['address_components'])):
            if req['results'][0]['address_components'][word]['types'][0] == 'country':
                country = str(req['results'][0]['address_components'][word]['long_name'])
            elif req['results'][0]['address_components'][word]['types'][0] == 'administrative_area_level_1':
                state = str(req['results'][0]['address_components'][word]['long_name'])
            elif req['results'][0]['address_components'][word]['types'][0] == 'locality':
                city = str(req['results'][0]['address_components'][word]['long_name'])
        
            listWords = address.split(" ")
            toTest = country + ' ' + state + ' ' + city
            for i in range(len(listWords)):
                if  toTest.find(listWords[i]) != -1:
                    wordFound = True
                    break
    except:
        country = ''
        state = 'Error'
        city = ''
        wordFound = False
    return address, city, state , country,  wordFound 

# Let's begin
addresses = input_data['locations_source'].split("**")

loops_num = 0
for item in range(len(addresses)):
    address = addresses[item]
    address, city, state , country,  wordFound = get_address(address,1)
    if  (city == '' and state != ''):
        address, city, state , country,  wordFound = get_address(address,2)
    results.append ({'location' : address+ '\n', 'City-state-country' : city + "," + state + "," + country + '\n', 'Status' : str(wordFound) + '\n' })
    
    if loops_num >=  int(input_data['limit']):
        break
    else:
        loops_num += 1        

return {'results' : results}
```

#### Reference Link: 
*  [Geocoding API](https://developers.google.com/maps/documentation/geocoding/start)
*  [Time Out Error](https://stackoverflow.com/questions/49388892/zapier-frequently-10-01-seconds-timeout)

#### Aditional Guidance:

---
### Step 4:

#### From:

#### To: 
Google SHeets

#### Parameters:

![Parameters](https://github.com/aguscort/zap-for-google-maps/raw/master/images/step4_parameters.png "Step 4 Parameters")

#### Step Description:
The results from previou step are going to populate a Google Spreadsheet.

#### Reference Link:

#### Aditional Guidance:


## PoC:

Time error are showed in Zap execution when a medium size file is suploaded.

## Standalone version

### How to get it running?

#### Requirements
In order to get this script running, you must have the following:

 1. [Install Python](https://docs.python-guide.org/starting/install3/osx/).

 2. install the required libraries:
 
```
pip install asyncio
pip install futures
pip install requests
pip install csv
pip install json
```

 3. Add the csv file into same folder that program.

Each execution the program will launch 500 request to Google Maps and populate a csv file with results. 

#### Versions
The program have two vession, the advanced is the [concurrent one](/../../code/step_code_standalone_concurrent.py)

