import asyncio
import json
import urllib.request
from concurrent.futures import ThreadPoolExecutor
import re

input_data = {"key": "AIzaSyAENvVkz2yAweS2hXcyDi5FmAA9Q3Trnko"}
file_input = 'test locations.csv'
file_output = 'test locations_output.csv'
temp_filename = 'tempfile.csv'

addresses = ['Helsinki, Southern Finland, Finland', 'Japan', 'Greater New York City Area', 'San Francisco Bay Area']
results = dict()

def address_treatment(address, level=2):
    goal = address.split(" ")
    for i in range(len(goal)):
        goal[i] = re.sub(r',', '', goal[i])
    goal = set(goal)
    goal = " ".join(goal)
    if level == 2:        
        goal =" ".join(goal.split('Area'))
        goal =" ".join(goal.split('Greater'))
        goal =" ".join(goal.split('Bay'))
    return goal

@asyncio.coroutine
def get_cities(address,idx):
    #url = 'https://maps.googleapis.com/maps/api/geocode/json?key=abcdfg&address='+zipcode+'&sensor=true'
    url = 'https://maps.googleapis.com/maps/api/geocode/json?key='+ input_data['key'] + '&address="' + address_treatment(address, 2) + ''
    print(url)
    response = yield from loop.run_in_executor(executor, urllib.request.urlopen, url)
    string = response.read().decode('utf-8')
    data = json.loads(string)
    print(data)
    results.update({idx: [address]})

if __name__ == "__main__":
    executor = ThreadPoolExecutor(1)
    loop = asyncio.get_event_loop()
    tasks = [asyncio.async(get_cities(z, i)) for i, z in enumerate(addresses)]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()
    print(results)