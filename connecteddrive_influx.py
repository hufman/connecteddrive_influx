#!/usr/bin/env python3

import os
import pprint
import sys
from typing import Any, Callable, Dict

import bimmer_connected.account
import bimmer_connected.country_selector
import bimmer_connected.state
import bimmer_connected.vehicle
import influxdb

import localsettings as settings


def convert_attributes(attributes: Dict[str, Any]) -> Dict[str, Any]:
	converted = {}
	for k, v in attributes.items():
		if k == "position":
			converted.update({
				p for p in v.items()
				if p[0] != 'status'
			})
		else:
			converted[k] = v
	return converted

def history_attr(attr_name: str) -> bool:
	return (attr_name == 'mileage' or
	        attr_name == 'lat' or
	        attr_name == 'lon')

def status_attr(attr_name: str) -> bool:
	return (history_attr(attr_name) or
	        attr_name.startswith('door') or
	        attr_name.startswith('window') or
	        attr_name.startswith('hood') or
	        attr_name.startswith('trunk') or
	        attr_name.startswith('remaining')
	)


def write_to_influx(client: influxdb.InfluxDBClient,
                    filter: Callable[[str], bool],
                    vehicle: bimmer_connected.vehicle.ConnectedDriveVehicle) -> None:
	data = convert_attributes(vehicle.state.attributes)
	fields = {k: v for k, v in data.items() if filter(k)}
	data = [{
		'measurement': 'status',
		'tags': {
			'vin': vehicle.vin,
			'name': vehicle.name
		},
		'time': vehicle.state.updateTime,
		'fields': fields
		}]
	client.write_points(data, time_precision='s')


region = bimmer_connected.country_selector.get_region_from_name(settings.connected_region)
account = bimmer_connected.account.ConnectedDriveAccount(
	settings.connected_username,
	settings.connected_password,
	region
)
influx = influxdb.InfluxDBClient(host=settings.influxdb_hostname, database="connecteddrive")

for vehicle in account.vehicles:
	vehicle.state.update_data()
	if sys.stdout.isatty():
		print(vehicle.name)
		pprint.pprint(vehicle.attributes)
		pprint.pprint(vehicle.state.attributes)

	for direction in bimmer_connected.vehicle.VehicleViewDirection:
		filename = f"{vehicle.vin}_{direction.name}.png"
		if os.path.exists(filename):
			continue
		with open(filename, 'wb') as output:
			output.write(vehicle.get_vehicle_image(2000, 2000, direction))

	write_to_influx(influx, status_attr, vehicle)
