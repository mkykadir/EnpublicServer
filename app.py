from flask import Flask, url_for, redirect, jsonify, request
from flask_pymongo import PyMongo
from flask_basicauth import BasicAuth
import datetime
import bcrypt
# from decimal import Decimal

# BasicAuth check_credentials method override
class EnpublicBasicAuth(BasicAuth):
    def check_credentials(self, username, password):
        user = mongo.db.users.find_one({'_id': username})
        if user is not None:
            salt_value = user['salt']
            hash_value = user['hash']
            login_value = bcrypt.hashpw(str.encode(password), str.encode(salt_value))
            if login_value.decode('utf-8') == hash_value:
                return True

        return False

app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'enpublic'
mongo = PyMongo(app)
auth = EnpublicBasicAuth(app)
#db = mongo.db

''' Achievement operation
    auth_header = request.authorization
    if auth_header.username is not None: # check if user logs in
        if auth.check_credentials(auth_header.username, auth_header.password):
            station_get_achievement = {
                'id': '111', # id should be updated
                'value': 0
            }

            find_achievement = mongo.db.users.find( # find if user has this achievement
                {'_id': auth_header.username, 'achievement.id': '111'}
            )

            if find_achievement is None: # add if user doesnt have this achievement
                mongo.db.users.find_one_and_update(
                    {'_id':auth_header.username}, {'$addToSet': {'achievement':station_get_achievement}}
                )

            mongo.db.users.find_one_and_update( # increase achievement value
                {'_id': auth_header.username, 'achievement.id': '111'}, {'$inc': {'achievement.$.value': 1}}
            )
'''

@app.route('/signup', methods=['POST'])
def add_user():
    data = request.get_json()
    salt_value = bcrypt.gensalt()
    hash_value = bcrypt.hashpw(str.encode(data['password']), salt_value)
    # TODO: Need to validate mail address
    new_user = {
        '_id': data['username'],
        'email': data['email'],
        'date': datetime.datetime.utcnow(),
        'salt': salt_value.decode('utf-8'),
        'hash': hash_value.decode('utf-8'),
        'operations':{
            'stationsearch': 0
        },
        'achievement': []
    }
    mongo.db.users.insert(new_user)
    # TODO: Check insert errors etc
    return jsonify({'result': 200})

@app.route('/station', methods=['POST'])
def add_station():
    data = request.get_json()
    count = 0
    for station in data:
        new_station = {
            'name': station['name'],
            'type': station['type'],
            'location': station['location'],
            'line': station['line']
        }
        mongo.db.stations.insert(new_station)
        count = count + 1

    return jsonify({'num': count})

@app.route('/station', methods=['GET'])
def get_all_stations():
    object = []
    for station in mongo.db.stations.find():
        found_station = {
            'name': station['name'],
            'type': station['type'],
            'location': station['location'],
            'line': station['line']
        }
        object.append(found_station)

    return jsonify(object)

@app.route('/station/search', methods=['GET'])
@auth.required
def search_station():
    auth_header = request.authorization
    mongo.db.users.find_one_and_update(
        {'_id': auth_header.username}, {'$inc': {'operations.stationsearch': 1}}
    )
    object = []
    name = request.args.get('name')
    regex = "^" + name

    places = mongo.db.stations.find({"name": {"$regex": regex, "$options": 'i'}})

    for station in places:
        found_station = {
            'name': station['name'],
            'type': station['type'],
            'location': station['location'],
            'line': station['line']
        }
        object.append(found_station)


    return jsonify(object)

@app.route('/station/nearby', methods=['GET'])
def get_nearby_location_stations():
    object = []
    lat = float(request.args.get('lat'))
    lon = float(request.args.get('lon'))

    places = mongo.db.stations.find({"location": {"$near": [lat, lon]}}).limit(10)

    for station in places:
        nearby_station = {
            'name': station['name'],
            'type': station['type'],
            'location': station['location'],
            'line': station['line']
        }
        object.append(nearby_station)

    return jsonify(object)




if __name__ == '__main__':
    app.run(debug=True)
