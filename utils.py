import uuid
from extensions import neo_db, user_datastore, Achievement
from models import Station, Vehicle


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
    query = "USING PERIODIC COMMIT" \
            " LOAD CSV FROM {path} AS file" \
            " CREATE (n:Station {short:file[0], name:file[1], latitude:toFloat(file[2]), longitude:toFloat(file[3]), " \
            "directed:0, nearby:0, searched:0, visited:0}) WITH n CALL spatial.addNode('spati',n) YIELD node RETURN " \
            "'added'"

    params = {'path': file_link}
    neo_db.cypher_query(query=query, params=params)


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
    Achievement(name='long_distance', description='You took very long ways with public transportation!', required=50, stats_id='distance').save()
    Achievement(name='directed_a_lot', description='Using Enpublic to find your way, best way!', required=100, stats_id='directed').save()
    Achievement(name='searched_a_lot', description='Learning never finishes even in public transportation...', required=100, stats_id='searched').save()
