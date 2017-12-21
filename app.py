from flask import Flask, url_for, redirect, jsonify, request
from flask_pymongo import PyMongo
from flask_basicauth import BasicAuth
import datetime
import bcrypt
import os
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
app.config['MONGO_URI'] = os.environ['ENPUBLIC_DB_SERVER']
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
        'name': data['name'],
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

@app.route('/login', methods=['GET'])
@auth.required
def check_user():
    return jsonify({'result': 200})

@app.route('/profile', methods=['GET'])
@auth.required
def get_user_profile():
    auth_header = request.authorization
    calculate_user_achievements(auth_header.username)
    user_info = mongo.db.users.find_one({'_id': auth_header.username})
    user_info.pop('date', None)
    user_info.pop('salt', None)
    user_info.pop('hash', None)
    user_info.pop('operations', None)
    return jsonify(user_info)

@app.route('/achievement', methods=['POST'])
@auth.required
def add_achievement():
    data = request.get_json()
    new_achievement = {
        '_id': data['name'],
        'description': data['description'],
        'operation': data['operation'],
        'value': data['value']
        # may need to hold image for achievement
    }
    mongo.db.achievements.insert(new_achievement)
    return jsonify({'result': 200})

def calculate_user_achievements(username):
    user = mongo.db.users.find_one({'_id': username})
    for achievement in mongo.db.achievements.find():
        if user['operations'][achievement['operation']] >= achievement['value']:
            mongo.db.users.find_one_and_update({'_id': username}, {'$addToSet': {'achievement': achievement['_id']}})

@app.route('/achievement', methods=['GET'])
@auth.required
def get_all_achievements():
    object = []
    for achievement in mongo.db.achievements.find():
        ret_achievement = achievement
        ret_achievement['name'] = ret_achievement['_id'].replace('-', ' ').title() # search-king to Search King
        ret_achievement.pop('operation', None)
        ret_achievement.pop('value', None)
        object.append(ret_achievement)

    return jsonify(object)

@app.route('/achievement/<achievement_id>')
@auth.required
def get_achievement(achievement_id):
    ret_achievement = mongo.db.achievements.find_one({'_id': achievement_id})
    ret_achievement['name'] = ret_achievement['_id'].replace('-', ' ').title()
    ret_achievement.pop('operation', None)
    ret_achievement.pop('value', None)
    return jsonify(ret_achievement)


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
def search_station():
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

    # gamification part for search
    auth_header = request.authorization
    if auth_header is not None:
        if auth_header.username is not None: # check if user logs in
            if auth.check_credentials(auth_header.username, auth_header.password):
                mongo.db.users.find_one_and_update(
                    {'_id': auth_header.username}, {'$inc': {'operations.stationsearch': 1}}
                )

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

# TODO: Station hakkında istatistik bilgileri tutulsun mu?

if __name__ == '__main__':
    app.run(debug=True)
