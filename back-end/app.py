import json

# Parking
# NOTE: only Seattle, WA parking plz
class Parking:
    def __init__(uid, lat, lon, price, distance, max_hour, hours_of_operation, max_time):
        self.uid = uid
        self.lat = lat
        self.lon = lon
        self.price = price
        self.distance = distance
        self.max_hour = max_hour
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

# TODO: get top 3 location around a fixed radius around the user's destination (lat, lon)
# Return a list of Parking class
def get_best_location(lat, lon, radius):
    pass

# TODO: algorithm to calculate crime probability
# NOTE: May want radius????????????????
def calculate_crime_probability(uid):
    pass

# TODO: get crime probability.
def get_crime_probability(uid):
    return calculate_crime_probability(uid)

print(get_json_f('dataset/y7pv-r3kh.json'))
