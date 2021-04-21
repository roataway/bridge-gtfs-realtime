import logging
from datetime import datetime

from google.transit import gtfs_realtime_pb2

from constants import ROUTE_ID_MAP

LOG = logging.getLogger("gtfs")


# keep a list of route IDs that we're not aware of. We rely on this set to
# reduce log cluttering
UNKNOWN_ROUTES = set()


def create_gtfs_feed(vehicle_states: dict) -> gtfs_realtime_pb2.FeedMessage:
    """Transform out internal state into a FeedMessage structure that GTFS expects"""
    # https://developers.google.com/transit/gtfs-realtime/reference#message-feedmessage"""
    feed_message = gtfs_realtime_pb2.FeedMessage()
    feed_message.header.gtfs_realtime_version = "2.0"
    feed_message.header.incrementality = gtfs_realtime_pb2.FeedHeader.FULL_DATASET
    feed_message.header.timestamp = int(datetime.now().timestamp())

    created_entries = 0
    for board_id, state in vehicle_states.items():
        if state.route_id in ROUTE_ID_MAP:
            # create the FeedEntity and populate it with the values from our own state structure
            feed_entity = feed_message.entity.add()
            feed_entity.id = f'{created_entries}-{board_id}'

            # https://developers.google.com/transit/gtfs-realtime/reference#message-vehicledescriptor
            feed_entity.vehicle.vehicle.id = state.rtu_id
            feed_entity.vehicle.vehicle.label = state.board_name
            feed_entity.vehicle.timestamp = int(state.last_seen)

            # https://developers.google.com/transit/gtfs-realtime/reference#message-position
            feed_entity.vehicle.position.longitude = state.lon
            feed_entity.vehicle.position.latitude = state.lat
            feed_entity.vehicle.position.speed = state.speed
            feed_entity.vehicle.position.bearing = state.direction

            # https://developers.google.com/transit/gtfs-realtime/reference#message-tripdescriptor
            # note that the route_id is different here, ROUTE_ID_MAP[entity.route_id] is what we usually call "name_concise"
            feed_entity.vehicle.trip.route_id = ROUTE_ID_MAP[state.route_id]
            created_entries +=1
        else:
            if state.route_id not in UNKNOWN_ROUTES:
                LOG.warning('Skipping board %s from unknown upstream_route_id=%s', board_id, state.route_id)
                UNKNOWN_ROUTES.add(state.route_id)

    LOG.debug("Produced %i entries in the feed", created_entries)
    return feed_message
