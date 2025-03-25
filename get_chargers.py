import requests
import pandas as pd
from datetime import datetime
import random  # Dodato ovde

API_KEY = 'b69cf987-9bb4-41c4-8bf5-d3707493a94b'
BASE_URL = 'https://api.openchargemap.io/v3/poi/'

params = {
    'key': API_KEY,
    'latitude': 51.5074,
    'longitude': -0.1278,
    'distance': 10,
    'maxresults': 20
}

response = requests.get(BASE_URL, params=params)

if response.status_code == 200:
    chargers = response.json()
    print(f"Pronađeno {len(chargers)} punionica u Londonu:")
    
    data = []
    current_hour = datetime.now().hour
    for charger in chargers:
        address = charger['AddressInfo']
        name = address['Title']
        lat = address['Latitude']
        lon = address['Longitude']
        if 8 <= current_hour <= 10 or 17 <= current_hour <= 19:
            status = 'Occupied' if random.random() < 0.7 else 'Free'
        else:
            status = 'Free' if random.random() < 0.7 else 'Occupied'
        print(f"- {name} na {lat}, {lon} - Status: {status}")
        data.append([name, lat, lon, status])
    
    df = pd.DataFrame(data, columns=['Name', 'Latitude', 'Longitude', 'Status'])
    df.to_csv('D:\ChargeSmart\chargers_london.csv', index=False)
    print("Podaci sačuvani u D:\\ChargeSmart\\chargers_london.csv")
else:
    print(f"Greška: {response.status_code}")