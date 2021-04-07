import time
import logging
from datetime import datetime
import json
import csv

from google.protobuf import text_format
import gtfs_realtime_pb2
import gtfs_realtime_pb2 as GTFS_real_time_proto

from structures import FeedEntity
from util import random_word, build_trolley_relation

LOG = logging.getLogger('gtfs')


# TODO move this to git sub-repo
# global dict that maps a route_id (aka id_upstream) to its name that passengers usually use (aka name_concise), e.g.:
# 1 -> 30, 2 -> 32, etc.
ROUTE_ID_MAP = build_trolley_relation('routes.csv')


def create_gtfs_proto_entity(state: dict) -> GTFS_real_time_proto.FeedMessage:
    gtfs_realtime_proto = GTFS_real_time_proto.FeedMessage()
    gtfs_realtime_proto.header.gtfs_realtime_version = "1.0"
    gtfs_realtime_proto.header.incrementality = gtfs_realtime_pb2.FeedHeader.FULL_DATASET
    gtfs_realtime_proto.header.timestamp = int(datetime.now().timestamp())
    result = []

    for board_id, feed_entity in state.items():
        if feed_entity.vehicle_trip_id in ROUTE_ID_MAP:
            result.append(feed_entity)

    if not result:
        # when no data are available, we just return None
        LOG.debug('No feeds to return')
        return None

    # if we got this far it means we've got some data, so we proceed normally
    for feed in result:
        build_big_entity(feed, gtfs_realtime_proto)

    LOG.debug('Produced %i entries in the feed', len(result))
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

    feedentity.id = random_word(4)
    # feedentity.vehicle.trip.start_date = int(time.mktime(datetime.datetime.strptime(start_date, '%Y-%m-%dT%H:%M:%SZ').timetuple()))
    # feedentity.vehicle.trip.schedule_relationship = TripDescriptor.SCHEDULED
    feedentity.vehicle.position.longitude, feedentity.vehicle.position.latitude = feed.vehicle_position_lot, feed.vehicle_position_lat
    feedentity.vehicle.position.speed = feed.vehicle_speed
    # feedentity.id = '0000076'
    # feedentity.vehicle.current_status = ""
    # feedentity.vehicle.stop_id = stop_id
    # feedentity.vehicle.current_stop_sequence = current_stop_sequence
    feedentity.vehicle.trip.route_id = ROUTE_ID_MAP[feed.vehicle_trip_id]

    #feedentity.vehicle.trip.schedule_relationship = TripDescriptor.SCHEDULED
