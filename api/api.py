from flask import Blueprint, request, jsonify
from flask_security import http_auth_required, current_user
from extensions import user_datastore, neo_db, Achievement, User
from models import Station, Vehicle, Transition, Activity, Location
import utils

api = Blueprint('api', 'api', url_prefix='/api')

"""
@apiDefine admin Admin Permission
    This call requires Admin permissions
"""
"""
@apiDefine user User Permission
    This call requires normal user permissions
"""


@api.errorhandler(401)
def unauthorized_access():
    return jsonify({'message': 'Unauthorized access, you need an account to access.'}), 401


"""
@api {post} /signup Register New User
@apiName RegisterUser
@apiGroup User
@apiDescription Register new client user. Android application registers users from this call.
You cannot register users for admin panel through this call.
@apiVersion 1.0.0
@apiParam {String} email Email address
@apiParam {String} password Password for login
@apiParam {String} full_name Full real name of user
@apiParamExample {json} Example parameters to send:
    {
        "email": "address@email.com",
        "password": "pass",
        "full_name" "User Name"
    }
@apiSuccess {String} email Email address of registered user
@apiSuccess {String} name Full real name of registered user
@apiSuccessExample {json} Success-Response:
    HTTP/1.1 200 OK
    {
        "email": "address@email.com",
        "name": "User Name"
    }
@apiError AllErrors Error description will be returned in message
@apiErrorExample {json} Error-Response:
    HTTP/1.1 500 Server Error
    {
        "message": "Error detail and explanation message"
    }
"""


@api.route('/signup', methods=['POST'])
def api_signup():
    data = request.get_json()
    try:
        user_datastore.create_user(email=data['email'], password=data['password'], full_name=data['full_name'])
        profile_info = {
            'email': data['email'],
            'name': data['full_name']
        }
        return jsonify(profile_info)
    except Exception as e:
        print(type(e))
        return jsonify({'message': str(e)}), 500


"""
@api {get} /profile Profile Information of Logged in User
@apiName UserProfile
@apiGroup User
@apiPermission user
@apiDescription Get profile information of currently logged in user. Android client uses that call to check if user
    credentials are correct.
@apiVersion 1.0.0
@apiHeader {String} authorization BasicAuth value of email and password of user
@apiHeaderExample {String} BasicAuth-Example
    Basic YWRkcmVzc0BtYWlsLmNvbToxMjM=
@apiSuccess {String} email Email address of user
@apiSuccess {String} name Full real name of user
@apiSuccessExample {json} Success-Response:
    HTTP/1.1 200 OK
    {
        "email": "address@email.com",
        "name": "User Name"
    ]
"""


@api.route('/profile', methods=['GET'])
@http_auth_required
def api_profile():
    profile_info = {
        'email': current_user['email'],
        'name': current_user['full_name']
    }
    return jsonify(profile_info)


"""
@apiDefine achievementObject
@apiSuccess {String} name Identifier of achievement object
@apiSuccess {String} description Description message of achievement
"""


"""
@api {post} /profile/activity Activity data of users
@apiName UserActivity
@apiGroup User
@apiPermission user
@apiDescription Send activity information of user and get gained achievements from this activity.
@apiVersion 1.0.0
@apiHeader {String} authorization BasicAuth value of email and password of user
@apiHeaderExample {String} BasicAuth-Example
    Basic YWRkcmVzc0BtYWlsLmNvbToxMjM=
@apiParamExample {json} Example parameters to send:
    {
        "locations": [...],
        "transitions": [...]
    }
@apiUse achievementObject
@apiSuccess {achievementObject[]}   List of achievements
@apiSuccessExample {json} Success-Response:
    HTTP/1.1 200 OK
    [
        {
            "name": "achievementid",
            "description": "Best achievement ever!"
        }
    ]
"""


@api.route('/profile/activity', methods=['POST'])
@http_auth_required
def api_user_activities():
    data = request.get_json()

    try:
        old_achievements = utils.get_user_achievements(current_user)
        transitions = data["transitions"]
        locations = data["locations"]

        transitions_array = []
        locations_array = []
        for transition in transitions:
            transitions_array.append(Transition(transition["activityType"], transition["transitionType"],
                                                transition["timestamp"]))

        for location in locations:
            locations_array.append(Location(location["latitude"], location["longitude"], location["timestamp"],
                                            location["speed"], location["accuracy"]))

        activities = Activity.transitions_to_activity(transitions_array)
        merged_activities = Activity.merge_nears(activities)
        located_activities = Activity.add_locations(merged_activities, locations_array)
        utils.activity_handler(located_activities, current_user)
        new_achievements = utils.get_user_achievements(current_user)
        ret_object = list(set(new_achievements).difference(set(old_achievements)))
        return jsonify(ret_object)
    except Exception as e:
        print(type(e))
        print(e)
        return jsonify({"message": str(e)}), 500


"""
@api {get} /achievement Achievements Gained by User
@apiName UserAchievements
@apiGroup User
@apiPermission user
@apiDescription Returns a list of achievements gained by logged-in user.
@apiVersion 1.0.0
@apiHeader {String} authorization BasicAuth value of email and password
@apiHeaderExample
    Basic YWRkcmVzc0BtYWlsLmNvbToxMjM=
@apiUse achievementObject
@apiSuccess {achievementObject[]}   List of achievements
@apiSuccessExample {json} Success-Response:
    HTTP/1.1 200 OK
    [
        {
            "name": "achievementid",
            "description": "Best achievement ever!"
        }
    ]
"""


@api.route('/achievement', methods=['GET'])
@http_auth_required
def api_user_achievements():
    ret_object = utils.get_user_achievements(current_user)
    return jsonify(ret_object)


"""
@apiDefine stationObject
@apiSuccess {String} name Name of the station
@apiSuccess {Number} latitude Station's location's latitude
@apiSuccess {Number} longitude Station's location's longitude
"""

"""
@api {get} /station?name Get Stations by Name
@apiName GetStations
@apiGroup Station
@apiPermission user
@apiDescription Get stations by name, this call will return results for stations' name starting with input variable
@apiVersion 1.0.0
@apiParam {String} name Name to search in stations
@apiSuccess {stationObject[]} List of stations
@apiSuccessExample {json} Success-Response:
    HTTP/1.1 200 OK
    [
        {
            "shortn": "STATI",
            "name": "Station1",
            "latitude": 40.123,
            "longitude": 20.123
        }
    ]
@apiError AllErrors Error description will be returned in message
@apiErrorExample {json} Error-Response:
    HTTP/1.1 500 Server Error
    {
        "message": "Error detail and explanation message"
    }
"""

"""
@api {get} /station?lat:=latitude?lon:=longitude?dist:=distance Get Nearby Stations by Location
@apiName GetNearbyStations
@apiPermission user
@apiGroup Station
@apiDescription Get nearby stations by location, this call will return results for nearby stations
@apiVersion 1.0.0
@apiParam {Number} lat Latitude of location to search, required
@apiParam {Number} lon Longitude of location to search, required
@apiParam {Number} dist Distance in km's to search within, optional variable
@apiSuccess {stationObject[]} List of stations
@apiSuccessExample {json} Success-Response:
    HTTP/1.1 200 OK
    [
        {
            "shortn": "STATI",
            "name": "Station1",
            "latitude": 40.123,
            "longitude": 20.123
        }
    ]
@apiError AllErrors Error description will be returned in message
@apiErrorExample {json} Error-Response:
    HTTP/1.1 500 Server Error
    {
        "message": "Error detail and explanation message"
    }
"""


@api.route('/station', methods=['GET'])
@http_auth_required
def api_station():
    name = request.args.get('name')
    if name is None:
        ret_object = []
        query = "CALL spatial.closest('spati', {latitude: {lat}, longitude: {lon}}, {dist}) YIELD node AS result SET " \
                "result.nearby=result.nearby+1 RETURN result.name AS name, result.latitude AS latitude, " \
                "result.longitude AS longitude, result.short AS shortn "

        try:
            latitude = float(request.args.get('lat'))
            longitude = float(request.args.get('lon'))
            distance = request.args.get('dist')

            if distance is None:
                distance = 0.005
            else:
                distance = float(distance)

            stations = neo_db.cypher_query(query=query, params={'lat': latitude, 'lon': longitude, 'dist': distance})
            stations = stations[0]
            for station in stations:
                nearby_stations = {
                    'name': station[0],
                    'latitude': station[1],
                    'longitude': station[2],
                    'shortn': station[3]
                }
                ret_object.append(nearby_stations)

            return jsonify(ret_object)
        except Exception as e:
            print(type(e))
            return jsonify({'message': str(e)}), 500
    else:
        current_user.stats.searched += 1
        current_user.save()
        try:
            stations = Station.nodes.filter(name__istartswith=name)
            ret_object = []
            for station in stations:
                found = {
                    'shortn': station.short,
                    'name': station.name,
                    'latitude': station.latitude,
                    'longitude': station.longitude
                }
                ret_object.append(found)

            return jsonify(ret_object)
        except Exception as e:
            print(type(e))
            return jsonify({'message': str(e)}), 500


"""
@apiDefine vehicleObject
@apiSuccess {String} code Identifier code of vehicle
@apiSuccess {String} color HEX color code of vehicle
"""

"""
@apiDefine directObject
@apiSuccess {String} name Name of the station
@apiSuccess {Number} latitude Station's location's latitude
@apiSuccess {Number} longitude Station's location's longitude
@apiSuccess {vehicleObject} next Vehicle information to depart from station
"""

"""
@apiDefine directResult
@apiSuccess {directObject[]}   Resulting path
"""

"""
@api {get} /station/direct?from:=station_id?to:=station_id Get Directions
@apiName GetDirections
@apiPermission user
@apiGroup Station
@apiDescription Get directions from a station to a destination station
@apiVersion 1.0.0
@apiParam {String} from Station identifier for starting station
@apiParam {String} to Station identifier for destionation station
@apiSuccess {directResult[]}   List of result route suggestions
@apiSuccessExample {json} Success-Response:
    HTTP/1.1 200 OK
    [
        [
            {
                "shortn": "STATI",
                "name": "Station1",
                "latitude": 40.123,
                "longitude": 20.123,
                "next": {
                    "code": "123K",
                    "color": "ffffff"
                }
            },
            {
                "shortn": "STATI2",
                "name": "Station2",
                "latitude": 41.123,
                "longitude": 21.123,
                "next": null
            }   
        ]
    ]
@apiError AllErrors Error description will be returned in message
@apiErrorExample {json} Error-Response:
    HTTP/1.1 500 Server Error
    {
        "message": "Error detail and explanation message"
    }
"""


@api.route('/station/direct', methods=['GET'])
@http_auth_required
def api_station_directions():
    from_name = request.args.get('from')
    to_name = request.args.get('to')

    from_station = Station.nodes.filter(short__iexact=from_name)[0]
    to_station = Station.nodes.filter(short__iexact=to_name)[0]

    current_user.stats.directed += 1
    current_user.save()

    result = utils.get_directions(from_station, to_station)

    return jsonify(result)
