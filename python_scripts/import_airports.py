import requests
from duffel_api import Duffel
import pandas as pd
import time
import datetime


####Set headers:
duffel = Duffel(access_token='duffel_test_8LPk3Pl965NJ-2BMSVrwirQToD5zgUojZPM0gw1HPR2')
headers = {
  'Authorization': 'Bearer duffel_test_8LPk3Pl965NJ-2BMSVrwirQToD5zgUojZPM0gw1HPR2',
  'Duffel-Version':'beta',
  'Accept':'application/json',
  'Content-Type':'application/json',
}

name = []
city = []
iata_code = []
time_zone = []
longitude = []
latitude = []

response = requests.get(f"https://api.duffel.com/air/airports", headers=headers)
print(response.json())
after = response.json()["meta"]["after"]
i = 1

while(after):
    try:
        response = requests.get(f"https://api.duffel.com/air/airports?after={after}", headers=headers)
        results = response.json()
        after = response.json()["meta"]["after"]
        for a in results["data"]:
              name.append(a["name"])
              city.append(a["city_name"])
              iata_code.append(a["iata_code"])
              time_zone.append(a["time_zone"])
              longitude.append(a["longitude"])
              latitude.append(a["latitude"])
        i += 1
        if i % 5 == 0:
          time.sleep(60)
        print(response.json())
        print(i)
    except KeyError:
        print(response.json())
        break

Airports_df = pd.DataFrame({"Name":name
                           ,"Iata_Code":iata_code
                           ,"City":city
                           ,"Timezone":time_zone
                           ,"Longitude":longitude
                           ,"Latitude":latitude})

print(len(Airports_df))

Airports_df.to_csv("Airports.csv")