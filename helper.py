import requests
from duffel_api import Duffel
import pandas as pd
from amadeus import ResponseError, Client
import datetime
from flask import render_template, session, redirect, request
from functools import wraps
import re




def book_flights(origin, destination, depart_date, return_date, born_on, title, gender, family_name, given_name):
    """
      Request flight offers and create flight orders
      based on applicant's desired trip information and personal details
    """
    #### Set API header:
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
        "origin": origin,
        "destination": destination,
        "departure_date": depart_date
      },
      {
        "origin": destination,
        "destination": origin,
        "departure_date": return_date
      }
    ]

    ## Set flight's passenger
    list_passengers = [
      {
        "phone_number": "+442080160508",
        "email": "ella@example.com",
        "born_on": born_on,
        "title": title,
        "gender": gender,
        "family_name": family_name,
        "given_name": given_name,
      }
    ]

    ##Search for offer
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

    ####Create flight order
    ## Set payment type
    payments = [
      {
        "type": "balance",
        "currency": offer_currency,
        "amount": offer_amount
      }
    ]

    ####Create oder after receiving payment:
    ## Update passenger id:
    list_passengers[0]["id"] = offer_passenger_id
    print(list_passengers)

    ## Request order
    try:
      order_request = duffel.orders.create().selected_offers([offer_id]).passengers(list_passengers).payments(payments).execute()
    except ResponseError as error:
      print('Order creation error ', error)
      return None

    order_id = order_request.id
    print('Order ID:', order_id)
    try:
      response = requests.get(f'https://api.duffel.com/air/orders?id={order_id}', headers=headers)
    except requests.exceptions.HTTPError as e:
      print("Error" + str(e))


    #####Print order
    order = response.json()
    flights = []
    print('Order has been created:', order["data"][0]["booking_reference"], 'with', order["data"][0]["owner"]["name"], '-', order["data"][0]["owner"]["iata_code"],)
    print('Total amount:',order["data"][0]["total_amount"],'',order["data"][0]["total_currency"])

    for i, slice in enumerate(order['data'][0]['slices']):
      flights.append({})
      no_of_flights = len(slice['segments'])
      print('Departure:', slice['origin']['name'], '-', slice['origin']['city_name'], ' at', slice['segments'][0]['departing_at'], 'operated by', slice['segments'][0]['operating_carrier']['name'])
      flights[i]["Origin"] = slice['origin']['name']
      flights[i]["Depart_at"] = slice['segments'][0]['departing_at']
      flights[i]["Depart_carrier"] = slice['segments'][0]['operating_carrier']['name']

      print('Arrival:', slice['destination']['name'], '-', slice['destination']['city_name'], ' at', slice['segments'][no_of_flights - 1]['arriving_at'], 'operated by', slice['segments'][no_of_flights - 1]['operating_carrier']['name'])
      flights[i]["Destination"] = slice['destination']['name']
      flights[i]["Arrive_at"] = slice['segments'][no_of_flights - 1]['arriving_at']
      flights[i]["Arrive_carrier"] = slice['segments'][no_of_flights - 1]['operating_carrier']['name']

      print('Duration (ISO8601):', slice["duration"])


    for passenger in order['data'][0]['passengers']:
        given_name = passenger['given_name']
        family_name = passenger['family_name']
        title = passenger['title'].upper()
        born_on = passenger['born_on']

    return {
        "booking_reference" : order["data"][0]["booking_reference"],
        "owner": order["data"][0]["owner"]["name"] + '-' + order["data"][0]["owner"]["iata_code"],
        "total_amount": order["data"][0]["total_amount"] + ' ' + order["data"][0]["total_currency"],
        "given_name": given_name,
        "family_name": family_name,
        "flights": flights,
        "title": title,
        "born_on": born_on
      }




#def book_hotels(city, depart_date, return_date, title, given_name, family_name):
#    """
#    Using Amadeus API, search for hotel offers in the destination city.
#    Book the cheapeast offer.
#    """
#    #Set API token:
#    amadeus = Client(
#        client_id='oIKLGdrhfMonZJsU8DAftn4eI5CDCseA',
#        client_secret='pm2YsUMqxXc7mzjG'
#    )

    #Get list of hotel offers for the certain date:
#    try:
#        response = amadeus.shopping.hotel_offers.get(
#            cityCode = city,
#            checkInDate = depart_date,
#            checkOutDate = return_date,
#            adults = '1',
#            deadline = str(datetime.datetime.strptime(depart_date, '%Y-%m-%d') + datetime.timedelta(days= -1)),
#            method = 'CREDIT_CARD',
#           )
#        results = response.data
#        sorted_results = sorted(results, key = lambda hotel : hotel['offers'][0]['price']['total'], reverse = True) #Sort by total amout of the hotel
#        print(sorted_results[1])
#        offers ={
#            'hotel' : [],
#            'price' : [],
#            'offer-id' : [],
#            'currency' : []
#        }
#        i = 0
#        for offer in sorted_results:
#            offers['hotel'].append(offer['hotel']['name'])
#            offers['price'].append(offer['offers'][0]['price']['total'])
#            offers['currency'].append(offer['offers'][0]['price']['currency'])
#            offers['offer-id'].append(offer['offers'][0]['id'])
#            i += 1
#            if i == 2:
#                break
#        print(offers)
#        offer_id = offers['offer-id'][0]
#        hotel = offers['hotel'][0]
#        price = offers['price'][0]
#        currency = offers['currency'][0]
#        print(offer_id)
#    except ResponseError as error:
#        print(error.code)
#        return None


    #Check if offer is still available
#    try:
#        amadeus.shopping.hotel_offer_search(offer_id).get()
#        print("Hotel offer is still available", offer_id)

        #Book hotel:
#        try:
#            guests = [{
#                'id' : 1,
#                'name': {
#                    'title' : title,
#                    'firstName' : given_name,
#                    'lastName'  : family_name,
#                },
#                'contact' : {
#                    'phone' : '+447493674430',
#                    'email' : 'thanhthuyphamvn@gmail.com'
#                }
#                }]
#            payments = {
#               'id': 1,
#                'method': 'creditCard',
#                'card': {
#                    'vendorCode': 'VI',
#                    'cardNumber': '4444333322221111',
#                    'expiryDate': '2027-03'}
#                }
#            booking = amadeus.booking.hotel_bookings.post(offer_id, guests, payments)
#            print(booking.data)
#            hotel_booking = {
#              'offer_id' : offer_id,
#              'hotel' : hotel,
#              'price' : price,
#              'check_in': depart_date,
#              'check_out' : return_date,
#              'booking_id' : booking.data[0]["associatedRecords"][0]["reference"],
#              'currency' : currency
#            }
#            print(hotel_booking)
#            return hotel_booking
#        except ResponseError as error:
#            print("Booking encouter error", error.code)
#            hotel_booking = {
#              'offer_id' : offer_id,
#              'hotel' : hotel,
#              'price' : price,
#              'check_in': depart_date,
#              'check_out' : return_date,
#              'currency' : currency
#            }
#            return hotel_booking

#    except ResponseError as error:
#        print("Hotel offer is not available", error.code)
#        return None




#Source: From cs50's week9 template
def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code




#Source: From cs50's week9 template
def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function



#Function to check if required input are provided:
def required_input(vars):
    '''
    Function to check if all required variables are provided
    '''
    result = 'pass'
    for var in vars:
      print("Validating ", var)
      if not request.form.get(var):
          result = 'failed'
    return result


#Function to check if input is of type date:
def date_validate(vars):
  '''
  Function to check if the input is compatible with type date
  '''

  result = 'pass'
  for var in vars:
      print("Validating date format of", var)
      print(request.form[var])
      try:
          datetime.datetime.strptime(request.form[var], "%Y-%m-%d")
          print(result)
      except ValueError:
          result = 'failed'
          print(result)
          break
  return result


#Function to check if input is of type email:
def email_validate(vars):
  '''
  Function to check if the input is compatible with type email
  '''
  result = 'pass'
  for var in vars:
      print("Validating email format of ", var)
      if '@' not in request.form[var]:
           result = 'failed'
  return result


#Function to check if input include malicious code:
def input_validate(vars):
  '''
  Function to check if the input contain special charactores
  '''
  result = 'pass'
  regex = r"[',\"]"
  for var in vars:
      print("Validating input of ", var)
      try:
        test_str = request.form[var]
        matches = re.findall(regex, test_str)
        if len(matches) > 0:
            result = 'failed'
      except (ValueError):
        result = 'failed'
  return result
