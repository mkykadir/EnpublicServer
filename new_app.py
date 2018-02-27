from flask import Flask, jsonify, request
from flask_basicauth import BasicAuth
from py2neo import Graph, Walkable, Node, Relationship, DatabaseError, GraphError
import time
import bcrypt

'''
query = "MATCH (n:Station) WHERE n.name=~{name} RETURN n.name, n.latitude, n.longitude"
places = graph.data(query, parameters={'name': name})
'''

"""
@apiDefine userperm User Permission Required
    This call requires user permissions to work, users' credentials should be passed through header with BasicAuth.
"""


# Authentication credential check override
class EnpublicBasicAuth(BasicAuth):
    def check_credentials(self, username, password):
        query = "MATCH (n:User) WHERE n.username={username} RETURN n.salt AS salt, n.hash AS hash"
        try:
            user_salthash = graph.data(query, parameters={'username': username})
            salt_value = user_salthash[0]['salt']  # Query returns array
            hash_value = user_salthash[0]['hash']  # Query returns array
            login_value = bcrypt.hashpw(str.encode(password), str.encode(salt_value))
            if login_value.decode('utf-8') == hash_value:
                return True
        except Exception as e:
            print(e)
            return False

        return False


app = Flask(__name__)
app.secret_key = 'merhabalar'  # TODO: Need to select good key
auth = EnpublicBasicAuth(app)
graph = Graph(password='7823')  # TODO: Need to get password from ENV variables

# Error Handlers


@app.errorhandler(401)
def unauthorized_access(error):
    return jsonify({'message': 'Unauthorized access, you need an account to access.'}), 401


# API calls

# ===START: USER OPERATIONS===


"""
@api {post} /api/signup Register User
@apiName RegisterUser
@apiGroup User
@apiDescription Register new client user to the system. Android client users and Android client application
uses this call to register new user. This call doesn't work for admin users and management panel.
@apiVersion 1.0.0
@apiParam {String} username Username of the user
@apiParam {String} password Password of the user
@apiParam {String} name Full real name of the user
@apiParam {String} email E-Mail address of the user
@apiParamExample {json} Example usage:
    {
        "username": "user",
        "password": "pass",
        "name": "User Name",
        "email": "user@provider.com"
    }
@apiSuccess {String} username Username of the user
@apiSuccess {String} name Full real name of the user
@apiSuccess {String} email E-Mail address of the user
@apiSuccessExample {json} Success-Response:
    HTTP/1.1 200 OK
    {
        "username": "user",
        "name": "User Name",
        "email": "user@provider.com"
    }
@apiError AllErrors Error description will be returned in message
@apiErrorExample {json} Error-Response:
    HTTP/1.1 500 Server Error
    {
        "message": "Error detail and explanation message"
    }
"""


@app.route('/api/signup', methods=['POST'])
def api_signup_user():
    data = request.get_json()
    try:
        gen_salt_value = bcrypt.gensalt()
        gen_hash_value = bcrypt.hashpw(str.encode(data['password']), gen_salt_value)

        query = "CREATE (n:User {username:{username}, email:{email}, name:{name}, date:{date}, salt:{salt}, " \
                "hash:{hash}}) "
        qparameters = {
            'username': data['username'],
            'email': data['email'],
            'name': data['name'],
            'date': int(round(time.time()*1000)),
            'salt': gen_salt_value.decode('utf-8'),
            'hash': gen_hash_value.decode('utf-8')
        }
        graph.data(query, parameters=qparameters)
        profile_info = {
            'username': data['username'],
            'name': data['name'],
            'email': data['email']
        }
        return jsonify(profile_info)
    except KeyError:
        return jsonify({'message': 'Missing required parameters'}), 400
    except Exception as e:
        return jsonify({'message': str(e)}), 500


'''
# Check user credentials if s/he exists in database
# NOTE: This call will not check for panel administration
@app.route('/api/login', methods=['GET'])
@auth.required
def api_check_user():
    # TODO do we need that?
    # check credentials by basic auth
'''


"""
@api {get} /api/profile Profile Information of User
@apiName UserProfile
@apiPermission userperm
@apiGroup User
@apiDescription Get profile information of the user. Android client uses this call to show users' profile.
@apiVersion 1.0.0
@apiHeader {String} authorization BasicAuth value of username and password tuple
@apiHeaderExample {String} BasicAuth-Example
    Basic dXNlcjpwYXNz
@apiSuccess {String} username Username of the user
@apiSuccess {String} name Full real name of the user
@apiSuccess {String} email E-Mail address of the user
@apiSuccessExample {json} Success-Response:
    HTTP/1.1 200 OK
    {
        "username": "user",
        "name": "User Name",
        "email": "user@provider.com"
    }
@apiError ServerErrors Error description will be returned in message
@apiErrorExample {json} Error-Response:
    HTTP/1.1 500 Server Error
    {
        "message": "Error detail and explanation message"
    }
"""


@app.route('/api/profile', methods=['GET'])
@auth.required
def api_user_profile():
    try:
        auth_username = request.authorization.username
        query = "MATCH (n:User) WHERE n.username={username} RETURN n.username AS username, n.email AS email, " \
                "n.name AS name "
        user_info = graph.data(query, parameters={'username': auth_username})
        profile = user_info[0]
        profile_info = {
            'username': profile['username'],
            'name': profile['name'],
            'email': profile['email']
        }
        return jsonify(profile_info)
    except Exception as e:
        return jsonify({'message': str(e)}), 500


# Get achieved achievements by user
@app.route('/api/achievement', methods=['GET'])
@auth.required
def api_user_achievements():
    try:
        auth_username = request.authorization.username
        query = "MATCH (n:User {username:{username}})-[b:ACHIEVED]->(a:Achievement) RETURN a.desc AS desc, " \
                "a.key AS key, b.date AS date "
        achievements = graph.data(query, parameters={'username': auth_username})
        return jsonify(achievements)
    except Exception as e:
        return jsonify({'message': str(e)}), 500


# Get detailed achievement information
# This information will be used when user clicks one of the achieved achievements
# in his/her profile
@app.route('/api/achievement/<achievement_id>', methods=['GET'])
def api_get_achievement_info(achievement_id):
    try:
        query = "MATCH (n:Achievement {key: {key}}) RETURN n.desc AS desc, n.key AS key LIMIT 1"
        result = graph.data(query, parameters={'key': achievement_id})
        return jsonify(result[0])
    except (DatabaseError, GraphError, IndexError):
        return jsonify({'message': 'Item not found'}), 404
    except Exception as e:
        return jsonify({'message': str(e)}), 500


# TODO: Add admin authentication to _admin_ functions
@app.route('/api/achievement', methods=['POST'])
def api_admin_achievement_add():
    data = request.get_json()
    try:
        query = "CREATE (achievement:Achievement {desc: {desc}, key: {key}, required: {required}})"
        qparameters = {
            'desc': data['desc'],
            'key': data['key'],
            'required': data['required']
        }
        graph.data(query, parameters=qparameters)
        return jsonify(qparameters)
    except KeyError:
        return jsonify({'message': 'Missing required parameters'}), 400
    except Exception as e:
        return jsonify({'message': str(e)}), 500


# ===END: USER OPERATIONS===

# ===START: STATION OPERATIONS===

# TODO: POST version for admin panel to add station(s)
@app.route('/api/station', methods=['GET'])
@auth.required
def api_station_search():
    # TODO: If admin return statistical information of station
    name = request.args.get('name')
    if name is None:
        # Return nearby stations
        retobject = []
        query = "CALL spatial.closest('stati', {latitude: {lat}, longitude: {lon}}, {dist}) YIELD node AS result SET " \
                "result.nearby=result.nearby+1 RETURN result.name AS name, result.latitude AS latitude, " \
                "result.longitude AS longitude "

        try:
            latitude = float(request.args.get('lat'))
            longitude = float(request.args.get('lon'))
            distance = request.args.get('dist')
            if distance is None:
                distance = float(1)  # Set 1 km if distance not provided TODO: Determine good distance
            else:
                distance = float(distance)

            stations = graph.data(query, parameters={'lat': latitude, 'lon': longitude, 'dist': distance})
            for station in stations:
                nearby_stations = {
                    'name': station['name'],
                    'location': [station['latitude'], station['longitude']]
                }
                retobject.append(nearby_stations)

            return jsonify(retobject)
        except Exception as e:
            return jsonify({'message': str(e)}), 500
    else:
        # Return stations with similar names
        try:
            query = "MATCH (n:Station) WHERE n.name=~{name} SET n.searched=n.searched+1 RETURN n.name AS name, " \
                    "n.latitude AS latitude, n.longitude AS longitude ORDER BY n.name"

            retobject = []
            regex_name = '(?i)' + name + '.*'
            stations = graph.data(query, parameters={'name': regex_name})
            for station in stations:
                found_station = {
                    'name': station['name'],
                    'location': [station['latitude'], station['longitude']]
                }
                retobject.append(found_station)
            return jsonify(retobject)
        except Exception as e:
            return jsonify({'message': str(e)}), 500


@app.route('/api/station/direct', methods=['GET'])
@auth.required
def api_get_directions():
    # TODO: Needs improvement about walking paths
    from_station = '(?i)' + request.args.get('from')
    to_station = '(?i)' + request.args.get('to')

    try:
        return_object = []
        query = "MATCH (from:Station), (to:Station) WHERE from.name=~{from} AND to.name=~{to} SET " \
                "from.directed=from.directed+1 SET to.directed=to.directed+1 WITH from, to MATCH p = " \
                "allShortestPaths((from)-[:CONNECTS*]-(to)) RETURN p "

        wgraph = graph.data(query, parameters={'from': from_station, 'to': to_station})

        for wpath in wgraph:
            inner_object = []
            walking = wpath['p']
            node_list = list(walking.nodes())
            relation_list = list(walking.relationships())

            i = 0
            while i < len(relation_list):
                inner = {
                    'name': node_list[i]['name'],
                    'latitude': node_list[i]['latitude'],
                    'longitude': node_list[i]['longitude'],
                    'way': {
                        'line': relation_list[i]['metro'],
                        'color': relation_list[i]['color']
                    }
                }
                inner_object.append(inner)
                i += 1

            last_object = {
                'name': node_list[i]['name'],
                'latitude': node_list[i]['latitude'],
                'longitude': node_list[i]['longitude']
            }
            inner_object.append(last_object)
            return_object.append(inner_object)

        return jsonify(return_object)
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@app.route('/api/station/stats', methods=['GET'])
def api_admin_station_stats():
    try:
        query = "MATCH (n:Station) RETURN n.name AS name, n.latitude AS latitude, n.longitude AS longitude, " \
                "n.directed AS directed, n.nearby AS nearby, n.searched AS searched, n.visited AS visited ORDER BY " \
                "n.name "

        stations = graph.data(query)
        retobject = []
        for station in stations:
            statistics = {
                'name': station['name'],
                'latitude': station['latitude'],
                'longitude': station['longitude'],
                'statistics': {
                    'directed': station['directed'],
                    'nearby': station['nearby'],
                    'searched': station['searched'],
                    'visited': station['visited']
                }
            }
            retobject.append(statistics)

        return jsonify(retobject)
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@app.route('/api/station', methods=['POST'])
def api_admin_station_add():
    # TODO: Add lines
    data = request.get_json()
    query = "CREATE (a:Station {name:{name}, latitude:{lat}, longitude:{lon}, directed:0, nearby:0, searched:0," \
            "visited:0}) WITH a CALL spatial.addNode('stati',a) YIELD node RETURN node"

    try:
        i = 0
        last_station = ''
        for station in data:
            graph.data(query, parameters={'name': station['name'], 'lat': station['latitude'], 'lon': station['longitude']})
            last_station = station['name']
            i += 1

        message = "Total {0} stations added, last station added was {1}".format(i, last_station)
        return jsonify({'message': message}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@app.route('/api/line', methods=['POST'])
def api_admin_line_add():
    data = request.get_json()

    try:
        stations = data['stations']
        query = "MATCH (a:Station {name:{start}}), (b:Station {name:{end}}) CREATE (a)-[rel:CONNECTS {color:{" \
                "color}, description:{desc}, distance:{dist}, metro:{line}}]->(b)"

        if len(stations) < 2:
            return jsonify({'message': 'You need to have at least 2 stations'}), 500

        i = 0
        while i+1 < len(stations):
            params = {
                'start': stations[i]['name'].title(),
                'end': stations[i+1]['name'].title(),
                'color': data['color'],
                'desc': data['desc'],
                'dist': stations[i]['dist'],
                'line': data['line']
            }
            graph.data(query, parameters=params)
            i += 1

        return jsonify({'message': 'Line added'}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

'''
# Search stations by name
@app.route('/api/station/search', methods=['GET'])
def api_search_station_name():
    try:
        name = request.args.get('name') # Get input value from user
'''

# ===END: STATION OPERATIONS===

# Administration GUI calls


if __name__ == '__main__':
    app.run(debug=True)  # TODO: Remove Debug from release version
