from amadeus import ResponseError, Client

#Search for hotel:
amadeus = Client(
    client_id='SyqBd95BnECikybzKF7A5ABySUCmqYSP',
    client_secret='nJIwMf9r28o1YwN9'
)

#Get list of hotel offers for the certain date:
try:
    response = amadeus.shopping.hotel_offers.get(
        cityCode = 'LON',
        checkInDate = '2022-12-20',
        checkOutDate = '2022-12-29',
        adults = '1',
        deadline = '2022-12-29T00:00:00+01:00',
        method = 'CREDIT_CARD',
        )
    results = response.data
    sorted_results = sorted(results, key = lambda hotel : hotel['offers'][0]['price']['total'], reverse = True) #Sort by total amout of the hotel
    offers ={
        'hotel' : [],
        'price' : [],
        'offer-id' : []
    }
    i = 0
    for offer in sorted_results:
        offers['hotel'].append(offer['hotel']['name'])
        offers['price'].append(offer['offers'][0]['price']['total'])
        offers['offer-id'].append(offer['offers'][0]['id'])
        i += 1
        if i == 5:
            break
    print(offers)
    offer_id = offers['offer-id'][0]
    print(offer_id)
except ResponseError as error:
    print(error)


#Check if offer is still available
try:
    availability = amadeus.shopping.hotel_offer_search(offer_id).get()
    print(availability.data)
except ResponseError as error:
    print(error)

#Book hotel:

try:
    guests = [{
        'id' : 1,
        'name': {
            'title' : 'Ms',
            'firstName' : 'Ella',
            'lastName'  : 'Pham',
        },
        'contact' : {
            'phone' : '+447493674430',
            'email' : 'thanhthuyphamvn@gmail.com'
        }
        }]
    payments = {
        'id': 1,
        'method': 'creditCard',
        'card': {
            'vendorCode': 'VI',
            'cardNumber': '4444333322221111',
            'expiryDate': '2027-03'}
        }
    booking = amadeus.booking.hotel_bookings.post(offer_id, guests, payments)
    print(booking.body)
except ResponseError as error:
    print(error.code)






test_data = [{'type': 'hotel-offers',
'hotel': {
    'type': 'hotel',
    'hotelId': 'XKLON321',
    'chainCode': 'XK',
    'dupeId': '501108165',
    'name': 'Hotel London Allocation',
    'cityCode': 'LON',
    'latitude': 51.50218,
    'longitude': -0.12714,
    'hotelDistance': {'distance': 0.4, 'distanceUnit': 'KM'},
    'address': {'lines': ['25 King Charles Street'], 'postalCode': 'SW1A 2', 'cityName': 'London', 'countryCode': 'GB'},
    'contact': {'phone': '020 7222 5152', 'fax': '020 7222 5153', 'email': 'resa@hotellondonallocation.com'},
    'amenities': ['PARKING']
    },
'available': True,
'offers': [
    {'id': '4VR23FUB9J',
    'checkInDate': '2022-12-20',
    'checkOutDate': '2022-12-29',
    'rateCode': 'REQ',
    'category': 'RAC',
    'description': {'text': 'On request rate incl. BRK', 'lang': 'EN'},
    'room': {
        'type': 'C1S',
        'typeEstimated': {'category': 'STANDARD_ROOM', 'beds': 1, 'bedType': 'SINGLE'},
        'description': {'text': 'Single Room', 'lang': 'EN'}},
    'guests': {'adults': 1},
    'price': {'currency': 'GBP', 'total': '1080.00', 'base': '1080.00', 'variations': {'changes': [{'startDate': '2022-12-20', 'endDate': '2022-12-29', 'base': '120.00'}]}},
    'self': 'https://test.api.amadeus.com/v2/shopping/hotel-offers/4VR23FUB9J'}],
'self': 'https://test.api.amadeus.com/v2/shopping/hotel-offers/by-hotel?hotelId=XKLON321&adults=1&checkInDate=2022-12-20&checkOutDate=2022-12-29'}]

AX_Card = { 'vendorCode': 'AX',
            'cardNumber': '377388973331006',
            'expiryDate': '2027-03'}