from flask import Flask, url_for, redirect, jsonify, request, render_template, flash, send_from_directory
from flask_pymongo import PyMongo
from flask_basicauth import BasicAuth
from py2neo import Graph, Walkable, Node, Relationship
import datetime
import bcrypt
import os
from decimal import Decimal
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

#UPLOAD_FOLDER = 'C:\Users\mkyka\Documents\Enpublic\Uploads'
app = Flask(__name__)
app.secret_key = 'merhabalar'
app.config['MONGO_URI'] = os.environ['ENPUBLIC_DB_SERVER']
app.config['UPLOAD_FOLDER'] = 'files'
#app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
mongo = PyMongo(app)
auth = EnpublicBasicAuth(app)
graph = Graph()
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
def allowed_file(filename):
    splitted = filename.split('.')
    print(splitted[1].lower())
    if splitted[1].lower() == 'txt':
        print('true')
        return True
    else:
        return False

@app.route('/samples/<samplename>', methods=['GET'])
def get_sample_file(samplename):
    uploads = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
    return send_from_directory(directory=uploads, filename=samplename+'.txt', as_attachment=True)

@app.route('/panel/add_station', methods=['GET'])
def panel_add_station():
    return render_template('addstation.html')

@app.route('/panel/add_station', methods=['POST'])
def panel_add_single_station():
    name = request.form['inputStationName']
    location = request.form['inputStationLocation']
    location_strip = location.split(',')
    # TODO: Check for array size!
    latitude = float(location_strip[0])
    longitude = float(location_strip[1])
    tx = graph.begin()
    new_station = Node("Station", name=name, latitude=latitude, longitude=longitude)
    tx.create(new_station)
    tx.commit()
    return redirect(url_for('panel_add_station'))

@app.route('/panel/add_stations', methods=['POST'])
def panel_add_multiple_station():
    if 'file' not in request.files:
        flash('File error')
        return redirect(url_for('panel_add_station'))

    file = request.files['file']
    print(file.filename)
    if file.filename == '':
        flash('No file provided')
        return redirect(url_for('panel_add_station'))

    if file and allowed_file(file.filename):
        file_content = file.stream.read()
        file_lines = file_content.splitlines()
        tx = graph.begin()
        for line in file_lines:
            line = line.decode("utf-8")
            words = line.split(',')
            #TODO: Check for array size
            station_name = words[0]
            station_latitude = float(words[1])
            station_longitude = float(words[2])
            new_station = Node("Station", name=station_name, latitude=station_latitude, longitude=station_longitude)
            tx.create(new_station)

        tx.commit()
        return redirect(url_for('panel_add_station'))

    return redirect(url_for('panel_add_station'))

@app.route('/panel/list_station', methods=['GET'])
def panel_list_station():
    all_stations = graph.run("MATCH (a:Station) RETURN a.name, a.latitude, a.longitude, id(a)").data()
    return render_template('liststation.html', stations=all_stations)

@app.route('/panel/edit_station/<id>', methods=['GET'])
def panel_edit_station(id):
    return redirect(url_for('panel_list_station'))

@app.route('/panel/delete_station/<id>', methods=['GET'])
def panel_delete_station(id):
    return redirect(url_for('panel_list_station'))

@app.route('/panel/add_line', methods=['GET'])
def panel_add_line():
    all_stations = graph.run("MATCH (a:Station) RETURN a.name, id(a)").data()
    return render_template('addline.html', stations=all_stations)

@app.route('/panel/add_line', methods=['POST'])
def panel_add_single_line():
    name = request.form['inputLineName']
    description = request.form['inputLineDescription']
    color = request.form['inputLineColor']
    stations = request.form.getlist('inputLineStations')
    color = color[1:]
    tx = graph.begin()
    i = 0
    while i < len(stations) - 1:
        start_node = graph.node(int(stations[i]))
        end_node = graph.node(int(stations[i+1]))

        se = Relationship(start_node, "CONNECTS", end_node, color=color, description=description, metro=name, distance=2)
        tx.create(se)
        i += 1

    tx.commit()
    #TODO: Distance bilgilerinin girileceği sayfaya yönlendir
    return redirect(url_for('panel_add_line'))

@app.route('/panel/add_lines', methods=['POST'])
def panel_add_multiple_line():
    if 'file' not in request.files:
        flash('Please select a file')
        return redirect(url_for('panel_add_line'))

    file = request.files['file']
    print(file.filename)
    if file.filename == '':
        flash('Filename error')
        return redirect(url_for('panel_add_line'))

    if file and allowed_file(file.filename):
        file_content = file.stream.read()
        file_lines = file_content.splitlines()
        tx = graph.begin()
        for line in file_lines:
            line = line.decode("utf-8")
            words = line.split(',')
            #TODO: Check for array size
            line_name = ''
            line_description = ''
            line_color = ''
            line_stations = []
            i = 0
            for word in words:
                if i == 0:
                    line_name = word
                elif i == 1:
                    line_description = word
                elif i == 2:
                    line_color = word
                else:
                    line_stations.append(int(word))

                i += 1

            i = 0
            while i < len(line_stations) - 1:
                #TODO: Check if station exists
                start_node = graph.node(int(line_stations[i]))
                end_node = graph.node(int(line_stations[i+1]))

                se = Relationship(start_node, "CONNECTS", end_node, color=line_color, description=line_description, metro=line_name, distance=2)
                tx.create(se)
                i += 1

        tx.commit()
    # TODO: Distance girilecek sayfaya yönlendir
    return redirect(url_for('panel_add_line'))

@app.route('/panel/list_lines', methods=['GET'])
def panel_list_line():
    all_lines = graph.run("MATCH (a:Station)-[r:CONNECTS]->(b:Station) RETURN distinct(r.metro) AS name, r.description AS description").data()
    return render_template('listline.html', lines=all_lines)

@app.route('/panel/edit_line/<name>', methods=['GET'])
def panel_edit_line(name):
    return redirect(url_for('panel_list_line'))

@app.route('/panel/delete_line/<name>', methods=['GET'])
def panel_delete_line(name):
    return redirect(url_for('panel_list_line'))

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

'''
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
'''
'''
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
'''
@app.route('/station/direct', methods=['GET'])
def get_directions():
    from_station = request.args.get('from')
    from_station = from_station.title()
    to_station = request.args.get('to')
    to_station = to_station.title()
    object = []

    querys = "MATCH (a:Station {name:'{from}'}), (b:Station {name:'{to}'})"
    querys += " MATCH p = allShortestPaths((a)-[:CONNECTS*]-(b)) RETURN p"
    # print(querys)

    wgraph = graph.data(querys, parameters={'from': from_station, 'to': to_station})

    for wpath in wgraph:
        innerobject = []
        walking = wpath['p']
        nodelist = list(walking.nodes())
        relationlist = list(walking.relationships())

        i = 0
        while i < len(relationlist):
            myobject = {
                'name': nodelist[i]['name'],
                'latitude': nodelist[i]['latitude'],
                'longitude': nodelist[i]['longitude'],
                'way': {
                    'line': relationlist[i]['metro'],
                    'color': relationlist[i]['color']
                }
            }
            innerobject.append(myobject)
            i += 1

        lastobject = {
            'name': nodelist[i]['name'],
            'latitude': nodelist[i]['latitude'],
            'longitude': nodelist[i]['longitude']
        }
        innerobject.append(lastobject)
        object.append(innerobject)

    return jsonify(object)


@app.route('/station/search', methods=['GET'])
def search_station():
    object = []
    name = request.args.get('name')
    query = "MATCH (n:Station) WHERE n.name=~'(?i){name}.*' RETURN n.name, n.latitude, n.longitude"

    places = graph.data(query, parameters={'name': name})
    #places = mongo.db.stations.find({"name": {"$regex": regex, "$options": 'i'}})
    for station in places:
        found_station = {
            'name': station['n.name'],
            'location': [station['n.latitude'],station['n.longitude']]
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

    query = "CALL spatial.withinDistance('geom', {latitude: {lat}, longitude: {lon}}, 2) YIELD node AS d RETURN d.name AS name, d.latitude AS latitude, d.longitude AS longitude"
    places = graph.data(query, parameters={'lat': lat, 'lon': lon})

    for station in places:
        nearby_station = {
            'name': station['name'],
            'location': [station['latitude'], station['longitude']]
        }
        object.append(nearby_station)

    return jsonify(object)

# TODO: Station hakkında istatistik bilgileri tutulsun mu?

if __name__ == '__main__':
    app.run(debug=True)
