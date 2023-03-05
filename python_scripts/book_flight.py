import requests
from duffel_api import Duffel
import pandas as pd
import time


####Set headers:
duffel = Duffel(access_token='duffel_test_8LPk3Pl965NJ-2BMSVrwirQToD5zgUojZPM0gw1HPR2')
headers = {
  'Authorization': 'Bearer duffel_test_8LPk3Pl965NJ-2BMSVrwirQToD5zgUojZPM0gw1HPR2',
  'Duffel-Version':'beta',
  'Accept':'application/json',
  'Content-Type':'application/json',
}



#####Search for flights
## Set flight's destination
slices = [
  {
    "origin": "LON",
    "destination": "NYC",
    "departure_date": "2022-11-21"
  },
  {
    "origin": "NYC",
    "destination": "LON",
    "departure_date": "2022-12-21"
  }
]

## Set flight's passenger
list_passengers = [
  {
    "phone_number": "+442080160508",
    "email": "ella@example.com",
    "born_on": "1993-12-31",
    "title": "Ms",
    "gender": "F",
    "family_name": "Pham",
    "given_name": "Ella",
  }
]

##Sear for offer
passengers = [{ "type": "adult" }]
offer_requests = duffel.offer_requests.create().slices(slices).passengers(passengers).cabin_class("economy").execute()
offer_request_id = offer_requests.id
##Get list of offers
return_offers = duffel.offers.list(offer_request_id, "total_amount", None)

##Save information of the cheapest offer
for offer in return_offers:
    offer_passenger_id = offer.passengers[0].id
    offer_id = offer.id
    offer_airline = offer.owner.name
    offer_currency = offer.total_currency
    offer_amount = offer.total_amount
    break
print(offer_id, offer_airline, offer_currency, offer_amount, offer_passenger_id)


#### Collecting payment from passenger:
##Create payment intent:
payment_intent = {
    "amount": "300.00",
    "currency": 'GBP',
}

pm_int = duffel.payment_intents.create().payment(payment_intent).execute()
pm_int = duffel.payment_intents.get(pm_int.id)
print(pm_int.status)
print(pm_int.client_token)

##Confirm payment intent:
duffel.payment_intents.confirm(pm_int.id)
####Create flight order
## Set payment type
payments = [
  {
    "type": "balance",
    "currency": offer_currency,
    "amount": offer_amount
  }
]



####Create order after receiving payment:
## Update passenger id:
list_passengers[0]["id"] = offer_passenger_id
print(list_passengers)

## Request order
order_request = duffel.orders.create().selected_offers([offer_id]).passengers(list_passengers).payments(payments).execute()
order_id = order_request.id
print('Order ID:', order_id)
try:
  response = requests.get(f'https://api.duffel.com/air/orders?id={order_id}', headers=headers)
except requests.exceptions.HTTPError as e:
  print("Error" + str(e))




#####Print order
order = response.json()
print('Order has been created:', order["data"][0]["booking_reference"], 'with', order["data"][0]["owner"]["name"], '-', order["data"][0]["owner"]["iata_code"],)
print('Total amount:',order["data"][0]["total_amount"],'',order["data"][0]["total_currency"])
for slice in order['data'][0]['slices']:
  no_of_flights = len(slice['segments'])
  print('Departure:', slice['origin']['name'], '-', slice['origin']['city_name'], ' at', slice['segments'][0]['departing_at'], 'operated by', slice['segments'][0]['operating_carrier']['name'])
  print('Arrival:', slice['destination']['name'], '-', slice['destination']['city_name'], ' at', slice['segments'][no_of_flights - 1]['arriving_at'], 'operated by', slice['segments'][no_of_flights - 1]['operating_carrier']['name'])
  print('Duration (ISO8601):', slice["duration"])
for passenger in order['data'][0]['passengers']:
  print('Passenger:', passenger['given_name'], passenger['family_name'])

time.sleep(61)
