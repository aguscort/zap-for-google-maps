# -*- coding: utf-8 -*-
import json
import re
import csv
import os
import sys
import asyncio
import concurrent.futures
import requests

country = ''
state = ''
city = ''
address = ''
wordFound = False
results = []
addresses = []
loops_num = 0
input_data = {"key": "AIzaSyAENvVkz2yAweS2hXcyDi5FmAA9Q3Trnko"}
file_input = 'test locations.csv'
file_output = 'test locations_output.csv'
temp_filename = 'tempfile.csv'
pool = 50
urls = []

def remove_dups(locations):
    p_locations = []
    for i in locations:
        i = tuple(i)
        p_locations.append(i)
    return list(set(p_locations))


def address_treatment(address, level=2):
    f_address = address.split(" ")
    for i in range(len(f_address)):
        f_address[i] = re.sub(r',', '', f_address[i])
    f_address = set(f_address)
    f_address = " ".join(f_address)
    if level == 2:
        f_address = " ".join(f_address.split('Area'))
        f_address = " ".join(f_address.split('Greater'))
        f_address = " ".join(f_address.split('Bay'))
    return f_address.strip()


def get_address(response, address, level):
    country = ''
    state = ''
    city = ''
    wordFound = False

    try:
        for word in range(len(response['results'][0]['address_components'])):
            if response['results'][0]['address_components'][word]['types'][0]\
                == 'country':
                country = str(response['results'][0]\
                ['address_components'][word]['long_name'])
            elif response['results'][0]['address_components'][word]['types'][0]\
                == 'administrative_area_level_1':
                state = str(response['results'][0]\
                ['address_components'][word]['long_name'])
            elif response['results'][0]['address_components']\
                [word]['types'][0] == 'locality':
                city = str(response['results'][0]['address_components']\
                [word]['long_name'])

            listWords = ''.join(address).split(" ")
            toTest = country + ' ' + state + ' ' + city
            for i in range(len(listWords)):
                if toTest.find(listWords[i]) != -1:
                    wordFound = True
                    break
    except:
        country = ''
        state = 'Error'
        city = ''
        wordFound = False
    return ''.join(address), city, state, country,  wordFound


def get_urls():
    with open(file_input, 'r', encoding='UTF8') as f:
        reader = csv.reader(f)
        addresses = remove_dups(list(reader))
    
    with open(temp_filename, 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_ALL)
        writer.writerows(addresses[pool:])

    for j in range(len(addresses[:pool])):
        urls.append('https://maps.googleapis.com/maps/api/geocode/json?key='+ input_data['key'] + '&address="' + address_treatment(''.join(addresses[j]), 2) + '"')
    return urls, addresses[:pool]

def restore_file():
    with open(temp_filename, 'r', encoding='UTF8') as f:
        reader = csv.reader(f)
        addresses = list(reader)

    with open(file_input, 'a+', encoding='UTF8') as f:
        writer = csv.writer(f)
        writer.writerows(addresses)
    os.remove(temp_filename)

async def main():
    loops_num = 0
    urls, addresses = get_urls()
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=pool) as executor:

            loop = asyncio.get_event_loop()
            futures = [
                loop.run_in_executor(
                    executor,
                    requests.get,
                    urls[i]
                )
                for i in range(pool)
            ]
            for response in await asyncio.gather(*futures):
                address, city, state, country,  wordFound = \
                    get_address(response.json(), addresses[loops_num], 2)
                results.append((addresses[loops_num], city,
                    state, country, str(wordFound)))
                loops_num += 1
        with open(file_output, 'a+', encoding='UTF8', newline='') as f:
            writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_ALL)
            writer.writerows(results)            
        os.replace (temp_filename, file_input)
    except IndexError:
         print('IndexError' + str(loops_num))
         #restore_file()
    
if __name__ == '__main__':     
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())