import uuid
from extensions import neo_db, user_datastore, Achievement, User
from models import Station, Vehicle
import operator


def file_name_check(file_name):
    if file_name == '':
        return False

    if file_name.split('.')[1].lower() == 'csv':
        return True
    else:
        return False


def generate_file_name():
    return str(uuid.uuid4().hex)


def vehicles_csv_handler(file_link):
    query = "USING PERIODIC COMMIT" \
            " LOAD CSV FROM {path} AS file" \
            " CREATE (:Vehicle {code: file[0], color: file[1], description: file[2]})"
    params = {'path': file_link}
    neo_db.cypher_query(query=query, params=params)


def stations_csv_handler(file_link):
    query = "USING PERIODIC COMMIT LOAD CSV FROM 'http://web.itu.edu.tr/yucelmuh/enpublic/stations.csv' AS " \
            "file WITH file CREATE (n:Station {short:file[0], name:file[1], latitude:toFloat(file[2]), " \
            "longitude:toFloat(file[3]), directed:0, nearby:0, searched:0, visited:0}) WITH n CALL spatial.addNode(" \
            "'spati',n) YIELD node WITH n CALL spatial.closest('spati', {latitude:n.latitude, longitude:n.longitude}, " \
            "0.005) YIELD node AS nd WITH n,nd CREATE (n)-[:WALK {distance: 4}]->(nd) CREATE (nd)-[:WALK {distance: " \
            "4}]->(n) "

    params = {'path': file_link}
    neo_db.cypher_query(query=query, params=params)
    delete_self_walk = "MATCH (n:Station)-[r:WALK]->(m:Station) WHERE n.short = m.short DELETE r"
    neo_db.cypher_query(query=delete_self_walk)


def relations_csv_handler(file_link):
    query = "USING PERIODIC COMMIT" \
            " LOAD CSV FROM {path} AS file" \
            " MATCH (a:Station {short: file[1]}), (b:Vehicle {code: file[0]})" \
            " CREATE (a)-[:FR {distance: toFloat(file[2])}]->(b)" \
            " CREATE (b)-[:TO {distance: 0.0}]->(a)"

    params = {'path': file_link}
    neo_db.cypher_query(query=query, params=params)


def create_admin_user():
    user_datastore.create_role(name='admin', description='Manages stations and information in system')
    user_datastore.create_user(email='admin@enpublic.com', password='123456', full_name='Admin',
                               roles=['admin'])


def create_neo_db():
    # Create temporary station and vehicle
    tmp_station = Station(short='STATI', name='Station', latitude=10.0, longitude=10.0).save()
    tmp_vehicle = Vehicle(code='100').save()

    spatial_query = "CALL spatial.addPointLayer('spati')"
    neo_db.cypher_query(query=spatial_query)

    tmp_station.delete()
    tmp_vehicle.delete()


def create_achievements():
    Achievement(name='directed_a_lot', description='Using Enpublic to find your way, best way!', required=10, stats_id='directed').save()
    Achievement(name='searched_a_lot', description='Learning never finishes even in public transportation...', required=10, stats_id='searched').save()
    Achievement(name='vehicles_a_lot', description='Used a lot of vehicles, you can now rate all of their comfort.', required=10, stats_id='vehicles').save()
    Achievement(name='walked_a_lot', description='You are walking a lot, you may want to try public transportation more!',
                required=10, stats_id='walked').save()
    Achievement(name='vehicled_a_lot', description='Your usage of vehicles is amazing! Keep going...',
                required=10, stats_id='vehicled').save()


def get_directions(fr, to):
    try:
        ret_object = []

        fr.directed += 1
        to.directed += 1
        fr.save()
        to.save()

        query = "MATCH (src:Station {short:{src}}), (dest:Station {short:{dest}}), p=allShortestPaths((src)-[*]->(" \
                "dest)) RETURN extract(n in nodes(p) | n.code) AS vehicle, extract(n in nodes(p) | n.short) AS " \
                "station, reduce(traveltime = 0, r in relationships(p) | traveltime + r.distance) AS totalTime ORDER " \
                "BY totalTime ASC LIMIT 5"

        graph = neo_db.cypher_query(query=query, params={'src': fr.short, 'dest': to.short})

        for result in graph[0]:
            result_obj = []
            vehicles = result[0]
            stations = result[1]

            iterator = 0

            while iterator < len(stations):
                obj = {}
                station_code = stations[iterator]
                if station_code is not None:
                    station = Station.nodes.get(short=station_code)
                    obj['shortn'] = station.short
                    obj['name'] = station.name
                    obj['latitude'] = station.latitude
                    obj['longitude'] = station.longitude
                    if iterator+1 < len(vehicles):
                        vehicle_code = vehicles[iterator+1]
                        if vehicle_code is not None:
                            vehicle = Vehicle.nodes.get(code=vehicle_code)
                            obj['next'] = {'code': vehicle.code, 'color': vehicle.color}
                        else:
                            obj['next'] = None
                    else:
                        obj['next'] = None

                    result_obj.append(obj)

                iterator += 1

            ret_object.append(result_obj)

        return ret_object
    except Exception as e:
        print(type(e))
        return {'message': str(e)}


def get_nearby_stations(lat, lon):
    ret_object = []
    query = "CALL spatial.closest('spati', {latitude: {lat}, longitude: {lon}}, {dist}) YIELD node AS result " \
            "RETURN result.name AS name, result.latitude AS latitude, " \
            "result.longitude AS longitude, result.short AS shortn LIMIT 1"

    try:
        stations = neo_db.cypher_query(query=query, params={'lat': lat, 'lon': lon, 'dist': 0.05})
        stations = stations[0]
        for station in stations:
            if station[1] == lat and station[2] == lon:
                continue

            nearby_stations = {
                'name': station[0],
                'latitude': station[1],
                'longitude': station[2],
                'shortn': station[3]
            }
            ret_object.append(nearby_stations)

        return ret_object
    except Exception as e:
        print(type(e))
        return {'message': str(e)}


def get_user_achievements(current_user):
    stats = current_user['stats']

    for achievement in Achievement.objects:
        if stats[achievement['stats_id']] >= achievement['required'] \
                and achievement.id not in current_user['achieved']:
            current_user.update(add_to_set__achieved=achievement)

    # current_user.save()
    user = User.objects(id=current_user.id).first()
    ret_object = []
    for achievement in user['achieved']:
        achieved = {
            "name": achievement.name,
            "description": achievement.description
        }
        ret_object.append(achieved)

    return ret_object


def merge_walking():
    # todo: do that for only added stations to reduce time!
    # todo: double sided relation for walking may be required
    stations = Station.nodes

    for station in stations:
        near_stations = get_nearby_stations(station.latitude, station.longitude)
        for nearby in near_stations:
            near_station = Station.nodes.filter(short__iexact=nearby['shortn'])[0]
            if not station.walk.is_connected(near_station):
                station.walk.connect(near_station)
            if not near_station.walk.is_connected(station):
                near_station.walk.connect(station)


def activity_handler(activities, current_user):
    for activity in activities:
        activity.locations.sort(key=operator.attrgetter('timestamp'))

        stations = []

        for location in activity.locations:
            nearby = get_nearby_stations(location.latitude, location.longitude)[0]
            stations.append(nearby['shortn'])

        stations = list(set(stations))
        print(stations)  # DEBUG

        if activity.type == 7:  # walking
            current_user.stats.walked += len(stations)
        elif activity.type == 8:  # on vehicle
            current_user.stats.vehicled += len(stations)

        current_user.save()
