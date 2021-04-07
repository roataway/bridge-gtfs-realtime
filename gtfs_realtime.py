import time
from datetime import datetime

from google.protobuf import text_format
import gtfs_realtime_pb2
import gtfs_realtime_pb2 as GTFS_real_time_proto
import json
import csv

import random, string

from FeedEntity import FeedEntity

trolley_relation = {}
with open('routes.csv', mode='r') as infile:
    reader = csv.reader(infile)
    trolley_relation = {rows[0].replace('"', '') : rows[1].replace('"', '') for rows in reader}




def randomword(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


def create_gtfs_proto_entity(bus_queue: dict) -> GTFS_real_time_proto.FeedMessage:
    gtfs_realtime_proto = GTFS_real_time_proto.FeedMessage()
    gtfs_realtime_proto.header.gtfs_realtime_version = "1.0"
    gtfs_realtime_proto.header.incrementality = gtfs_realtime_pb2.FeedHeader.FULL_DATASET
    gtfs_realtime_proto.header.timestamp = int(datetime.now().timestamp())
    feeds = []
    print("xxxxxxxxxxxxxxxxx")
    for k, v in bus_queue.items():
        feeds_bus = v
        if len(feeds_bus) > 0:
            feedbus = feeds_bus.pop()
            if feedbus.vehicle_trip_id in trolley_relation:
                feeds.append(feedbus)
    is_empty = True
    if len(feeds) > 0:
        is_empty = False
    for feed in feeds:
        build_big_entity(feed, gtfs_realtime_proto)

    if is_empty:
        return None
    return gtfs_realtime_proto


def build_big_entity(feed: FeedEntity, gtfs_realtime_proto):
    topic = feed.vehicle_trip_id

    feedentity = gtfs_realtime_proto.entity.add()
    feedentity.vehicle.vehicle.id = feed.vehicle_id
    feedentity.vehicle.vehicle.label = feed.vehicle_label
    feedentity.vehicle.timestamp = int(datetime.now().timestamp())

    # feedentity.header.gtfs_realtime_version = "1.0"
    # feedentity.header.incrementality = gtfs_realtime_pb2.FeedHeader.FULL_DATASET
    # feedentity.header.timestamp = int(time.mktime(datetime.datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ').timetuple()))

    feedentity.id = randomword(4)
    # feedentity.vehicle.trip.start_date = int(time.mktime(datetime.datetime.strptime(start_date, '%Y-%m-%dT%H:%M:%SZ').timetuple()))
    # feedentity.vehicle.trip.schedule_relationship = TripDescriptor.SCHEDULED
    feedentity.vehicle.position.longitude, feedentity.vehicle.position.latitude = feed.vehicle_position_lot, feed.vehicle_position_lat
    feedentity.vehicle.position.speed = feed.vehicle_speed
    # feedentity.id = '0000076'
    # feedentity.vehicle.current_status = ""
    # feedentity.vehicle.stop_id = stop_id
    # feedentity.vehicle.current_stop_sequence = current_stop_sequence
    feedentity.vehicle.trip.route_id = trolley_relation[feed.vehicle_trip_id]

    #feedentity.vehicle.trip.schedule_relationship = TripDescriptor.SCHEDULED
