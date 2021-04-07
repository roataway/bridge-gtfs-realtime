import json
from datetime import datetime

from util import random_word


class FeedEntity:
    """A class to represent the state of a vehicle, ready for serialization to ProtoBuf"""
    id: str
    vehicle_id: str
    vehicle_label: str
    vehicle_timestamp: int
    feed_id: int
    vehicle_position_lat: float
    vehicle_position_lot: float
    vehicle_trip_id: str
    vehicle_speed: float

    def __init__(self, data: dict, route_id: str):
        self.id = random_word(6)
        self.vehicle_id = data['board']
        self.vehicle_label = 'troleibuz'
        datetime_object = datetime.strptime(data['timestamp'], '%Y-%m-%dT%H:%M:%SZ')
        self.vehicle_timestamp = datetime_object.timestamp()  # this must be the time when the server received it?
        self.vehicle_position_lat = data['latitude']
        self.vehicle_position_lot = data['longitude']
        self.vehicle_speed = data['speed'] / 3.6  # convert to m/s
        self.vehicle_trip_id = route_id

    def __str__(self):
        return f'lat:{self.vehicle_position_lat}, lon:{self.vehicle_position_lot}, route_id:{self.vehicle_trip_id}'
