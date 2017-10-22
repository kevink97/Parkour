import json
import math
import requests
from flask import request

KEY = 'l6GBK4VxJWCgBAAgKyifQyK2bleECQG3'
SECRET = 'cAbR2VK4WLqTTG2T'

# Parking
# NOTE: only Seattle, WA parking plz
class Parking:
    def __init__(self, uid, lat, lon, price, distance, hours_of_operation, max_time):
        self.uid = uid
        self.lat = lat
        self.lon = lon
        self.price = price
        self.distance = distance
        self.hours_of_operation = hours_of_operation
        self.max_time = max_time

# Crime
class Crime:
    def __init__(self, uid, lat, lon):
        self.uid = uid
        self.lat = lat
        self.lon = lon

parkings = None # parking data
crimes = None # crime data

# Gets json from file
def get_json_f(filename):
    d = None
    with open(filename) as json_data:
        d = json.load(json_data)
    return d

def get_json_parking_rule(lat, lon, max_radius, max_results):
    global KEY
    params = {'lat': lat, 'long' : lon, 'max-distance' : max_radius,
            'max_results' : max_results, 'apikey' : KEY}
    r = requests.get('https://apis.solarialabs.com/shine/v1/parking-rules/meters',
            params=params)
    return r.json()

def rad(x):
    return x * math.pi / 180;

def getDistance(lat1, long1, lat2, long2):
    R = 6378137;
    dLat = rad(lat2 - lat1);
    dLong = rad(long2 - long1);
    a = math.sin(dLat / 2) * math.sin(dLat / 2) + math.cos(rad(lat1)) * math.cos(rad(lat2)) * math.sin(dLong / 2) * math.sin(dLong / 2);
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a));
    d = R * c;
    return d; # returns the distance in mete


def update_parking(lat, lon, radius):
    json = get_json_parking_rule(lat, lon, radius, 25)
    global parkings
    parkings = list()
    for parking in json:
        # lat, lon, price, distance, hours_of_operation, max_time)
        p = Parking(parking['Meter_ID'], parking['Latitude'],
            parking['Longitude'],
            parking['Rate'],
            getDistance(lat, lon, float(parking['Latitude']), float(parking['Longitude'])),
            parking['Hours_of_Operation'], parking['Time_Limits'])
        parkings.append(p)

def parse_crime():
    json = get_json_f('dataset/y7pv-r3kh.json')
    global crimes
    crimes = []
    for incident in json:
        crimes.append(Crime(incident['rms_cdw_id'],incident['longitude'],incident['latitude']))

# TODO: get top 3 location around a fixed radius around the user's destination (lat, lon)
# Return a list of Parking class
def get_best_location(lat, lon, radius):
    pass

# TODO: get crime probability.
def get_crime_probability(uid):
    parking = None
    for p in parkings:
        if p.uid == uid:
            parking = p
            break
    return calculate_crime_probability(lat, lon, radius)

@app.route('/crime_probability', methods=['GET'])
def crime_probability():
    uid = request.args.get('uid')
    return jsonify({'result' : get_crime_probability(uid)})

@app.route('/information', methods=['GET'])
def information():
    uid = request.args.get('uid')
    return jsonify({'result': get_information(uid)})

@app.route('/bkeghj')
def bleh():
    pass
