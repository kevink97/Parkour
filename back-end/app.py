import json
import math
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

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

def get_json_parking_rule(lat, lon, max_radius):
    global KEY
    params = {'lat': lat, 'long' : lon, 'max-distance' : 10000,
            'max_results' : 10, 'apikey' : KEY}
    r = requests.get('https://apis.solarialabs.com/shine/v1/parking-rules/meters',
            params=params)
    return r.json()

def rad(x):
    return x * math.pi / 180;

def getDistance(lat1, long1, lat2, long2):
    lat1 = float(lat1)
    long1 = float(long1)
    lat2 = float(lat2)
    long2 = float(long2)
    R = 6378137;
    dLat = rad(lat2 - lat1);
    dLong = rad(long2 - long1);
    a = math.sin(dLat / 2) * math.sin(dLat / 2) + math.cos(rad(lat1)) * math.cos(rad(lat2)) * math.sin(dLong / 2) * math.sin(dLong / 2);
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a));
    d = R * c;
    return d; # returns the distance in mete

def getInformation(uid, lat, lon):
    return get_uid_match(uid, lat, lon, 10000)

def parse_crime():
    json = get_json_f('dataset/y7pv-r3kh.json')
    global crimes
    crimes = []
    for incident in json:
        cr = Crime(incident['rms_cdw_id'],incident['longitude'],incident['latitude'])
        crimes.append(cr)
parse_crime()


# TODO: get top 3 location around a fixed radius around the user's destination (lat, lon)
# Return a list of Parking class
def get_best_location(lat, lon, radius):
    json = get_json_parking_rule(lat, lon, radius)
    global parkings
    bestLocations = list()
    for parking in json:
        # lat, lon, price, distance, hours_of_operation, max_time)
        print(parking)
        p = Parking(parking['Meter_ID'], parking['Latitude'],
                parking['Longitude'],
                parking['Rate'],
                getDistance(lat, lon, float(parking['Latitude']), float(parking['Longitude'])),
                parking['Hours_of_Operation'], parking['Time_Limits'])
        bestLocations.append(p);
        if len(bestLocations) > 3:
            return bestLocations

# TODO: get crime probability.
def get_crime_probability(uid, lat, lon, radius):

    json = get_json_parking_rule(lat, lon, radius)
    p = None
    for parking in json:
        # TODO: look for particular uid
        if(parking['Meter_ID'] == uid):
            p = get_uid_match(uid, lat, lon, radius)
            break
    closeCrimeCount = 0
    for spot in crimes:
        if(getDistance(spot.lat, spot.lon, p.lat, p.lon) < 100000):
            closeCrimeCount += 1
    if(closeCrimeCount >= 5):
        probability = 3
    elif(closeCrimeCount >= 1):
        probability = 2
    else:
        probability = 1
    return (closeCrimeCount, probability)

def get_uid_match(uid, lat, lon, radius):
    print(type(uid), lat, lon, radius)
    json = get_json_parking_rule(lat, lon, radius)
    p = None
    for parking in json:
        # TODO: look for particular uid
        print(parking['Meter_ID'])
        if(parking['Meter_ID'] == uid):

            return Parking(parking['Meter_ID'], parking['Latitude'],
                parking['Longitude'], parking['Rate'],
                getDistance(lat, lon, float(parking['Latitude']), float(parking['Longitude'])),
                parking['Hours_of_Operation'], parking['Time_Limits'])





@app.route('/crime_probability', methods=['GET'])
def crime_probability():
    uid = request.args.get('uid')
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    (ct, p) = get_crime_probability(uid, lat, lon, 1000)
    return jsonify({'result' : { 'probability' : p, 'count': ct }})

@app.route('/information', methods=['GET'])
def information():
    uid = request.args.get('uid')
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    p = getInformation(uid, lat, lon)
    return jsonify({'result' : {
        'uid' : p.uid,
        'lat' : p.lat,
        'lon' : p.lon,
        'price' : p.price,
        'distance' : p.distance,
        'hours_of_operation' : p.hours_of_operation,
        'max_time' : p.max_time
        }})

@app.route('/best_parking')
def best_parking():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    locs = get_best_location(lat, lon, 10000)
    llocs = list()
    if locs is not None:
        for loc in locs:
            (ct, p) = get_crime_probability(loc.uid, loc.lat, loc.lon, 1000)
            llocs.append({
                'uid' : loc.uid,
                'lat' : loc.lat,
                'lon' : loc.lon,
                'price' : loc.price,
                'distance' : loc.distance,
                'hours_of_operation' : loc.hours_of_operation,
                'max_time' : loc.max_time,
                'crime' : p
                })
        return jsonify({'result': llocs})
    else:
        return jsonify({'result': llocs})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
