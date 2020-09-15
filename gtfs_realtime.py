import time

import gtfs_realtime_pb2
import gtfs_realtime_pb2 as GTFS_real_time_proto
import json
from gtfs_realtime_pb2 import Alert, TripDescriptor, VehiclePosition
import datetime

from gtfs_realtime_translators.factories import TripUpdate, FeedMessage
import random, string

def randomword(length):
   letters = string.ascii_lowercase
   return ''.join(random.choice(letters) for i in range(length))

def create_gtfs_proto_entity(q, timestamp):
    gtfs_realtime_proto = GTFS_real_time_proto.FeedMessage()

    gtfs_realtime_proto.header.gtfs_realtime_version = "1.0"
    gtfs_realtime_proto.header.incrementality = gtfs_realtime_pb2.FeedHeader.FULL_DATASET
    gtfs_realtime_proto.header.timestamp = int(timestamp)
    for x in q:
        build_big_entity(x, gtfs_realtime_proto, timestamp)
    return gtfs_realtime_proto


def build_big_entity(x, gtfs_realtime_proto, timestamp):
    topic = x[0]
    val_x = x[1]
    val_x = json.loads(val_x.decode('utf8').replace("'", '"'))
    feedentity = gtfs_realtime_proto.entity.add()
    feedentity.vehicle.vehicle.id = str(topic)
    feedentity.vehicle.vehicle.label = 'troleibuz'
    feedentity.vehicle.timestamp = int(timestamp)

    # feedentity.header.gtfs_realtime_version = "1.0"
    # feedentity.header.incrementality = gtfs_realtime_pb2.FeedHeader.FULL_DATASET
    # feedentity.header.timestamp = int(time.mktime(datetime.datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ').timetuple()))

    feedentity.id = randomword(4)
    # feedentity.vehicle.trip.start_date = int(time.mktime(datetime.datetime.strptime(start_date, '%Y-%m-%dT%H:%M:%SZ').timetuple()))
    # feedentity.vehicle.trip.schedule_relationship = TripDescriptor.SCHEDULED
    feedentity.vehicle.position.longitude, feedentity.vehicle.position.latitude = val_x['longitude'], val_x['latitude']
    feedentity.vehicle.position.speed = val_x['speed']
    #feedentity.id = '0000076'
    # feedentity.vehicle.current_status = ""
   # feedentity.vehicle.stop_id = stop_id
    # feedentity.vehicle.current_stop_sequence = current_stop_sequence
    feedentity.vehicle.trip.trip_id = str(22)
    feedentity.vehicle.trip.route_id = str(22)
    feedentity.vehicle.trip.schedule_relationship = TripDescriptor.SCHEDULED

