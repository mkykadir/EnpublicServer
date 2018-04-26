from flask import Flask, jsonify, request, render_template, redirect, url_for, json, send_from_directory
from flask_basicauth import BasicAuth
from flask_login import LoginManager, current_user, login_user, login_required, logout_user
from neomodel import config, db
from data_models import Achievement, User, Vehicle, Station, Transition, Location, Activity
import os

# TODO: Return proper error messages for API calls


'''
query = "MATCH (n:Station) WHERE n.name=~{name} RETURN n.name, n.latitude, n.longitude"
places = graph.data(query, parameters={'name': name})
'''

"""
@apiDefine userperm User Permission Required
    This call requires user permissions to work, users' credentials should be passed through header with BasicAuth.
"""
"""
@apiDefine adminperm Admin Permission Required
    This call designed and developed for management console and only intended for admin use only from 
    management console.
"""


class AdminUser:
    username = "admin"
    
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.username

    @staticmethod
    def get_user():
        return AdminUser()


# Authentication credential check override
class EnpublicBasicAuth(BasicAuth):
    def check_credentials(self, username, password):
        try:
            user = User.nodes.get(username=username)
            test_hash = User.get_hash(user.salt, password)
            user_hash = user.hash

            if test_hash.decode('utf-8') == user_hash:
                return True

        except Exception as e:
            print(e)
            print(type(e))
            return False

        return False


app = None
auth = None
login_manager = None


try:
    secret_key = os.environ('ENPUBLIC_SECRET')
    db_url = os.environ['ENPUBLIC_DB_URL']

    app = Flask(__name__)
    app.secret_key = secret_key  # 'merhabalar'
    app.config['UPLOAD_FOLDER'] = 'files'
    auth = EnpublicBasicAuth(app)
    config.DATABASE_URL = db_url  # "bolt://neo4j:7823@localhost:7687"
    login_manager = LoginManager()
    login_manager.init_app(app)
except Exception as ex:
    print("Check database service or password!")
    print(str(ex))
    exit(1)


# Error Handlers


@app.errorhandler(401)
def unauthorized_access():
    return jsonify({'message': 'Unauthorized access, you need an account to access.'}), 401


@login_manager.user_loader
def load_admin(user_id):
    return AdminUser.get_user()


@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('admin_login'))


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
        input_password = data['password']
        salt_value, hash_value = User.get_salt_hash(input_password)

        new_user = User()
        new_user.name = data['name']
        new_user.username = data['username']
        new_user.email = data['email']
        new_user.salt = salt_value.decode('utf-8')
        new_user.hash = hash_value.decode('utf-8')

        new_user.save()

        profile_info = {
            'username': data['username'],
            'name': data['name'],
            'email': data['email']
        }
        return jsonify(profile_info)
    except Exception as e:
        print(type(e))
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
@apiHeader {String} authorization BasicAuth value of username and password pair
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
        user = User.nodes.get(username=auth_username)
        profile_info = {
            'username': user.username,
            'name': user.name,
            'email': user.email
        }
        return jsonify(profile_info)
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@app.route('/api/profile/activity', methods=['POST'])
@auth.required
def api_user_activities():
    data = request.get_json()

    try:
        transitions = data["transitions"]
        locations = data["locations"]

        trans_array = []
        loc_array = []
        for transition in transitions:
            trans_array.append(Transition(transition["activityType"], transition["transitionType"],
                                          transition["timestamp"]))

        for loc in locations:
            loc_array.append(Location(loc["latitude"], loc["longitude"], loc["timestamp"], loc["speed"],
                                      loc["accuracy"]))

        activities = Activity.transitions_to_activity(trans_array)
        merged_activities = Activity.merge_nears(activities)
        located_activities = Activity.add_locations(merged_activities, loc_array)
        # TODO: debug located_activities and work on algorithm for calculating busses
        # TODO: return gained achievements
        return jsonify({"result": 200})

    except Exception as e:
        print(type(e))
        print(e)
        return jsonify({"result": 500})


"""
@apiDefine achievementObject
@apiSuccess {Date} date Date of achievement gain
@apiSuccess {String} desc Description of achievement
@apiSuccess {String} key Identifier for achievement
"""

"""
@api {get} /api/achievement Achievements Gained by User
@apiName UserAchievements
@apiPermission userperm
@apiGroup User
@apiDescription Get list of achievement that were gained by user during usage of system
@apiVersion 1.0.0
@apiHeader {String} authorization BasicAuth value of username and password pair
@apiHeaderExample {String} BasicAuth-Example
    Basic dXNlcjpwYXNz
@apiUse achievementObject
@apiSuccess {achivementObject[]} result  List of achievements
@apiSuccessExample {json} Success-Response:
    HTTP/1.1 200 OK
    {
        "result": [
            {
                "date": 1519208927000,
                "desc": "Achievement description",
                "key": "achv-key"
            }
        ]
    }
@apiError ServerErrors Error description will be returned in message
@apiErrorExample {json} Error-Response:
    HTTP/1.1 500 Server Error
    {
        "message": "Error detail and explanation message"
    }
"""


@app.route('/api/achievement', methods=['GET'])
@auth.required
def api_user_achievements():
    try:
        result = []
        auth_username = request.authorization.username
        user = User.nodes.get(username=auth_username)
        for achievement in user.achievements.all():
            appending = {
                "key": achievement.key,
                "description": achievement.description,
                "req_value": achievement.req_value
            }
            result.append(appending)

        return jsonify(result)
    except Exception as e:
        return jsonify({'message': str(e)}), 500


"""
@api {get} /api/achievement/:key Get Achievement Details
@apiName AchievementDetails
@apiGroup Gamification
@apiDescription Get detailed information of achievement identified by key value
@apiVersion 1.0.0
@apiParam {String} key Unique ID of achievement, key value
@apiUse achievementObject
@apiSuccessExample {json} Success-Response
    HTTP/1.1 200 OK
    {
        "date": 1519208927000,
        "desc": "Achievement description",
        "key": "achv-key"
    }
@apiError ServerErrors Error description will be returned in message
@apiErrorExample {json} Error-Response:
    HTTP/1.1 500 Server Error
    {
        "message": "Error detail and explanation message"
    }
"""


@app.route('/api/achievement/<achievement_id>', methods=['GET'])
def api_get_achievement_info(achievement_id):
    try:
        achievement = Achievement.nodes.get(key=achievement_id)
        result = {
            "key": achievement.key,
            "description": achievement.description,
            "req_value": achievement.req_value
        }
        return jsonify(result)
    except Exception as e:
        return jsonify({'message': str(e)}), 500


# TODO: Do we need add achievement operation since we cannot manage calls for this?
"""
@api {post} /api/achievement Add New Achievement
@apiName AddAchievement
@apiPermission adminperm
@apiGroup Gamification
@apiDescription Add new achievement to the system
@apiVersion 1.0.0
@apiParam {String} description Description of achievement
@apiParam {String} key Unique identifier for achievement 
@apiParam {Integer} req_value required limit for achieving
"""


# TODO: Add admin authentication to _admin_ functions
@app.route('/api/achievement', methods=['POST'])
def api_admin_achievement_add():
    data = request.get_json()
    try:
        new_achievement = Achievement()
        new_achievement.key = data['key']
        new_achievement.description = data['description']
        new_achievement.req_value = data['req_value']
        new_achievement.save()
        return jsonify(data)
    except Exception as e:
        return jsonify({'message': str(e)}), 500


# ===END: USER OPERATIONS===

# ===START: STATION OPERATIONS===


@app.route('/api/station', methods=['GET'])
@auth.required
def api_station_search():
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

            # graph.data(query, parameters={'lat': latitude, 'lon': longitude, 'dist': distance})
            stations = db.cypher_query(query=query, params={'lat': latitude, 'lon': longitude, 'dist': distance})
            stations = stations[0]
            for station in stations:
                nearby_stations = {
                    'name': station[0],
                    'location': [station[1], station[2]]
                }
                retobject.append(nearby_stations)

            return jsonify(retobject)
        except Exception as e:
            return jsonify({'message': str(e)}), 500
    else:
        # Return stations with similar names
        try:
            stations = Station.nodes.filter(name__istartswith=name)

            retobject = []
            for station in stations:
                found = {
                    'name': station.name,
                    'location': [station.latitude, station.longitude]
                }
                retobject.append(found)

            return jsonify(retobject)
        except Exception as e:
            return jsonify({'message': str(e)}), 500


@app.route('/api/station/direct', methods=['GET'])
@auth.required
def api_get_directions():
    # TODO: Needs improvement about walking paths
    # from_station = '(?i)' + request.args.get('from')
    # to_station = '(?i)' + request.args.get('to')

    from_name = request.args.get('from')
    to_name = request.args.get('to')

    try:
        return_object = []
        '''query = "MATCH (from:Station), (to:Station) WHERE from.name=~{from} AND to.name=~{to} SET " \
                "from.directed=from.directed+1 SET to.directed=to.directed+1 WITH from, to MATCH p = " \
                "allShortestPaths((from)-[:CONNECTS*]-(to)) RETURN p "

        wgraph = db.cypher_query(query, params={'from': from_station, 'to': to_station})'''

        from_station = Station.nodes.filter(name__iexact=from_name)[0]
        to_station = Station.nodes.filter(name__iexact=to_name)[0]
        from_station.directed += 1
        to_station.directed += 1
        from_station.save()
        to_station.save()

        query = "MATCH p=allShortestPaths((a:Station {name:{from}})-[:CONNECTS*]-(b:Station {name:{to}})) RETURN p"
        wgraph = db.cypher_query(query, params={'from': from_station.name, 'to': to_station.name})

        for wpath in wgraph[0]:
            path_info = wpath[0]
            nodes = path_info.nodes
            relations = path_info.relationships

            inner_res = {
                'start': from_station.name,
                'end': to_station.name
            }
            inner_obj = []
            i = 0
            while i < len(relations):
                inner = {
                    'name': nodes[i].properties['name'],
                    'latitude': nodes[i].properties['latitude'],
                    'longitude': nodes[i].properties['longitude'],
                    'way': {
                        'code': relations[i].properties['code'],
                        'color': relations[i].properties['color']
                    }
                }
                inner_obj.append(inner)
                i += 1

            last_obj = {
                'name': nodes[i].properties['name'],
                'latitude': nodes[i].properties['latitude'],
                'longitude': nodes[i].properties['longitude']
            }

            inner_obj.append(last_obj)
            inner_res['way'] = inner_obj
            inner_res['vehicles'] = Vehicle.find_different_vehicles(relations)
            return_object.append(inner_res)

        return jsonify(return_object)
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@app.route('/api/station/stats', methods=['GET'])
def api_admin_station_stats():
    try:
        stations = Station.nodes.order_by('name')
        retobject = []
        for station in stations:
            statistics = {
                'name': station.name,
                'latitude': station.latitude,
                'longitude': station.longitude,
                'statistics': {
                    'directed': station.directed,
                    'nearby': station.nearby,
                    'searched': station.searched,
                    'visited': station.visited
                }
            }
            retobject.append(statistics)

        return jsonify(retobject)
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@app.route('/api/station/all', methods=['GET'])
def api_admin_station_all():

    # query = "MATCH(n:Station) RETURN n.name AS name, n.latitude AS latitude, n.longitude AS longitude ORDER " \
    #         "BY n.name"

    try:
        stations = Station.nodes.order_by("name")
        retobject = []
        for station in stations:
            found = {
                "name": station.name,
                "latitude": station.latitude,
                "longitude": station.longitude,

            }
            retobject.append(found)

        return jsonify(retobject)
    except Exception as e:
        print(type(e))
        return jsonify({'message': str(e)}), 500


@app.route('/api/station', methods=['POST'])
def api_admin_station_add():
    data = request.get_json()
    return _api_admin_station_add(data)


def _api_admin_station_add(data):
    query = "CREATE (a:Station {name:{name}, latitude:{lat}, longitude:{lon}, directed:0, nearby:0, searched:0," \
            "visited:0}) WITH a CALL spatial.addNode('stati',a) YIELD node RETURN node"

    try:
        i = 0
        last_station = ''
        for station in data:
            db.cypher_query(query, params={'name': station['name'],
                                           'lat': station['latitude'],
                                           'lon': station['longitude']})
            last_station = station['name']
            i += 1

        message = "Total {0} stations added, last station added was {1}".format(i, last_station)
        return jsonify({'message': message}), 200
    except Exception as e:
        print(str(e))
        print(type(e))
        return jsonify({'message': str(e)}), 500


@app.route('/api/station', methods=['DELETE'])
def api_admin_station_delete():
    data = request.get_json()
    query = "MATCH (n:Station {name: {name}}) WITH n, n.name AS name DETACH DELETE n RETURN name"

    deleted = 0
    not_deleted = 0
    last_station = ''
    for station in data:
        try:
            result = db.cypher_query(query, params={'name': station})
            print(result)
            if len(result) == 0:
                not_deleted += 1
            else:
                deleted += 1
                last_station = station
        except Exception as e:
            print(str(e))
            print(type(e))
            not_deleted += 1
            continue

    message = ""
    if deleted > 0:
        message += "Total {0} stations deleted. ".format(deleted)

    if last_station != '':
        message += "Last station deleted was {0}. ".format(last_station)

    if not_deleted > 0:
        message += "{0} unsuccessful deletions.".format(not_deleted)

    return jsonify({'message': message})


@app.route('/api/station', methods=['PUT'])
def api_admin_station_update():
    data = request.get_json()

    '''
    query = "MATCH (n:Station {name:{oldname}}) SET n.name = {newname}, n.latitude = {latitude}, n.longitude = {" \
            "longitude}"
    '''
    updated = 0
    last_updated = ''
    not_updated = 0
    for station in data:
        try:
            to_update = Station.nodes.get(name=station['oldname'])
            to_update.name = station['newname']
            to_update.latitude = station['latitude']
            to_update.longitude = station['longitude']
            to_update.save()
            last_updated = station['oldname']
            updated += 1
        except Exception as e:
            print(str(e))
            print(type(e))
            not_updated += 1
            continue

    message = ""
    if updated > 0:
        message += "Total {0} stations updated. ".format(updated)

    if last_updated != '':
        message += "Last station updated was old {0}. ".format(last_updated)

    if not_updated > 0:
        message += "{0} unsuccessful updates.".format(not_updated)

    return jsonify({'message': message})


@app.route('/api/line', methods=['POST'])
def api_admin_line_add():
    data = request.get_json()
    return _api_admin_line_add(data)


def _api_admin_line_add(data):
    try:
        stations = data['stations']
        '''
        query = "MATCH (a:Station {name:{start}}), (b:Station {name:{end}}) CREATE (a)-[rel:CONNECTS {color:{" \
                "color}, description:{desc}, distance:{dist}, metro:{line}}]->(b)"
        '''
        if len(stations) < 2:
            return jsonify({'message': 'You need to have at least 2 stations'}), 500

        i = 0
        while i + 1 < len(stations):
            start_station = Station.nodes.get(name=stations[i]['name'].title())
            end_station = Station.nodes.get(name=stations[i + 1]['name'].title())
            rel_param = {
                'code': data['line'],
                'color': data['color'],
                'description': data['desc'],
                'distance': data['dist']
            }
            start_station.connect(end_station, rel_param).save()
            i += 1

        return jsonify({'message': 'Line added'}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500


# TODO: Line delete and edit

'''
# Search stations by name
@app.route('/api/station/search', methods=['GET'])
def api_search_station_name():
    try:
        name = request.args.get('name') # Get input value from user
'''


# ===END: STATION OPERATIONS===

# Administration GUI calls
@app.route('/')
def initial_address():
    return redirect(url_for('admin_login'))


@app.route('/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('panel_add_station'))

    if request.method == 'GET':
        return render_template('login.html')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'admin' and password == '7823':  # encrypt this part
            login_user(AdminUser.get_user())
            return redirect(url_for('panel_add_station'))
        else:
            return redirect(url_for('admin_login'))


@app.route('/logout', methods=['GET'])
def admin_logout():
    logout_user()
    return redirect(url_for('admin_login'))


@app.route('/samples/<samplename>', methods=['GET'])
@login_required
def get_sample_file(samplename):
    uploads = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
    return send_from_directory(directory=uploads, filename=samplename + '.json', as_attachment=True)


def allowed_file(filename):
    splitted = filename.split('.')
    print(splitted[1].lower())
    if splitted[1].lower() == 'json':
        return True
    else:
        return False


@app.route('/addstation', methods=['GET'])
@login_required
def panel_add_station():
    return render_template('new_addstation.html')


@app.route('/addstations', methods=['POST'])
@login_required
def panel_add_multiple_station():
    if 'file' not in request.files:
        return redirect(url_for('panel_add_station'))

    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('panel_add_station'))

    if file and allowed_file(file.filename):
        file_content = file.stream.read()
        data = json.loads(file_content)
        _api_admin_station_add(data)

    return redirect(url_for('panel_add_station'))


@app.route('/liststation', methods=['GET'])
@login_required
def panel_list_station():
    return render_template('new_liststation.html')


@app.route('/addline', methods=['GET'])
@login_required
def panel_add_line():
    return render_template('new_addline.html')


@app.route('/addlines', methods=['POST'])
@login_required
def panel_add_multiple_line():
    if 'file' not in request.files:
        return redirect(url_for('panel_add_line'))

    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('panel_add_line'))

    if file and allowed_file(file.filename):
        file_content = file.stream.read()
        data = json.loads(file_content)
        _api_admin_line_add(data)

    return redirect(url_for('panel_add_line'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)  # TODO: Remove Debug from release version
