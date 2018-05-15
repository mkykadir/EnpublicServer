import os
import utils
from flask import Blueprint, render_template, send_from_directory, request, redirect, url_for
from flask_security import roles_required
import validators
from models import Vehicle, Station


panel = Blueprint('panel', 'panel', url_prefix='/panel')


@panel.route('/', methods=['GET'])
@roles_required('admin')
def panel_main():                               # Index page for panel
    return render_template("panel_main.html")


@panel.route('/station', methods=['GET'])
@roles_required('admin')
def panel_manage_stations():                    # Station management page, add and list stations
    stations = Station.nodes.order_by('short')
    return render_template("manage_stations.html", stations=stations)


@panel.route('/station/add', methods=['POST'])
@roles_required('admin')
def panel_add_stations_from_csv():              # Get CSV file and add them to the Neo4j database
    if 'file_link' in request.form:
        file_link = request.form['file_link']
        if validators.url(file_link):
            utils.stations_csv_handler(file_link)

    return redirect(url_for('panel.panel_manage_stations'))


@panel.route('/station/<station_code>', methods=['GET'])
@roles_required('admin')
def panel_station_details(station_code):        # Get station details and update
    station = Station.nodes.get(short=station_code)
    vehicles = station.fr.all()
    return render_template("detail_station.html", station=station, vehicles=vehicles)


@panel.route('/station/<station_code>/update', methods=['POST'])
@roles_required('admin')
def panel_update_station(station_code):
    new_short = request.form['short']
    new_name = request.form['name']
    new_latitude = float(request.form['latitude'])
    new_longitude = float(request.form['longitude'])

    if new_short is None or new_name is None or new_latitude is None or new_longitude is None:
        return redirect(url_for('panel.panel_station_details', station_code=station_code))

    station = Station.nodes.get(short=station_code)
    station.short = new_short
    station.name = new_name
    station.latitude = new_latitude
    station.longitude = new_longitude

    station.save()
    return redirect(url_for('panel.panel_station_details', station_code=new_short))


@panel.route('/station/<station_code>/delete', methods=['GET'])
@roles_required('admin')
def panel_delete_station(station_code):
    station = Station.nodes.get(short=station_code)
    station.delete()
    return redirect(url_for('panel.panel_manage_stations'))


@panel.route('/station/<station_code>/deleterel/<vehicle_code>', methods=['GET'])
@roles_required('admin')
def panel_delete_station_relation(station_code, vehicle_code):
    vehicle = Vehicle.nodes.get(code=vehicle_code)
    station = Station.nodes.get(short=station_code)

    vehicle.to.disconnect(station)
    station.fr.disconnect(vehicle)
    return redirect(url_for('panel.panel_station_details', station_code=station_code))


@panel.route('/vehicle', methods=['GET'])
@roles_required('admin')
def panel_manage_vehicles():                    # Vehicle management page, add and list vehicles
    vehicles = Vehicle.nodes.order_by('code')
    return render_template("manage_vehicles.html", vehicles=vehicles)


@panel.route('/vehicle/add', methods=['POST'])
@roles_required('admin')
def panel_add_vehicles_from_csv():              # Get CSV file and add them to the Neo4j database
    if 'file_link' in request.form:
        file_link = request.form['file_link']
        if validators.url(file_link):
            utils.vehicles_csv_handler(file_link)

    return redirect(url_for('panel.panel_manage_vehicles'))


@panel.route('/vehicle/<vehicle_code>', methods=['GET'])
@roles_required('admin')
def panel_vehicle_details(vehicle_code):        # Get vehicle details and update
    vehicle = Vehicle.nodes.get(code=vehicle_code)
    stations = vehicle.to.all()
    return render_template("detail_vehicle.html", vehicle=vehicle, stations=stations)


@panel.route('/vehicle/<vehicle_code>/add/relations', methods=['POST'])
@roles_required('admin')
def panel_add_relations_from_csv(vehicle_code):
    if 'file_link' in request.form:
        file_link = request.form['file_link']
        if validators.url(file_link):
            utils.relations_csv_handler(file_link)

    return redirect(url_for('panel.panel_vehicle_details', vehicle_code=vehicle_code))


@panel.route('/vehicle/<vehicle_code>/deleterel/<station_code>', methods=['GET'])
@roles_required('admin')
def panel_delete_vehicle_relation(vehicle_code, station_code):
    vehicle = Vehicle.nodes.get(code=vehicle_code)
    station = Station.nodes.get(short=station_code)

    vehicle.to.disconnect(station)
    station.fr.disconnect(vehicle)
    return redirect(url_for('panel.panel_vehicle_details', vehicle_code=vehicle_code))


@panel.route('/vehicle/<vehicle_code>/update', methods=['POST'])
@roles_required('admin')
def panel_update_vehicle(vehicle_code):
    new_code = request.form['code']
    new_description = request.form['description']
    new_color = request.form['color'][1:]
    vehicle = Vehicle.nodes.get(code=vehicle_code)

    if new_code is None or new_description is None or new_color is None:
        return redirect(url_for('panel_vehicle_details', vehicle_code=vehicle_code))

    vehicle.code = new_code
    vehicle.description = new_description
    vehicle.color = new_color

    vehicle.save()
    return redirect(url_for('panel.panel_vehicle_details', vehicle_code=new_code))


@panel.route('/vehicle/<vehicle_code>/delete', methods=['GET'])
@roles_required('admin')
def panel_delete_vehicle(vehicle_code):
    vehicle = Vehicle.nodes.get(code=vehicle_code)
    vehicle.delete()
    return redirect(url_for('panel.panel_manage_vehicles'))


@panel.route('/samples/<sample_name>', methods=['GET'])
@roles_required('admin')
def panel_get_sample_file(sample_name):         # Send sample CSV files to client
    files = os.path.join(panel.root_path, 'files')
    return send_from_directory(directory=files, filename=sample_name + '.csv', as_attachment=True)
