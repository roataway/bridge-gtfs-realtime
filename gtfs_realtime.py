import logging
from datetime import datetime

from google.transit import gtfs_realtime_pb2

from structures import FeedEntity
from util import random_word, build_trolley_relation

LOG = logging.getLogger("gtfs")


# TODO move this to git sub-repo
# global dict that maps a route_id (aka id_upstream) to its name that passengers usually use (aka name_concise), e.g.:
# 1 -> 30, 2 -> 32, etc.
ROUTE_ID_MAP = build_trolley_relation("routes.csv")


def create_gtfs_proto_entity(state: dict) -> gtfs_realtime_pb2.FeedMessage:
    """Transform out internal state into a FeedMessage structure that GTFS expects"""
    result = gtfs_realtime_pb2.FeedMessage()
    result.header.gtfs_realtime_version = "1.0"
    result.header.incrementality = gtfs_realtime_pb2.FeedHeader.FULL_DATASET
    result.header.timestamp = int(datetime.now().timestamp())
    output_entities = []

    for board_id, feed_entity in state.items():
        if feed_entity.trip_id in ROUTE_ID_MAP:
            output_entities.append(feed_entity)

    if not output_entities:
        # when no data are available, we just return None
        LOG.debug("No feeds to return")
        return None

    # if we got this far it means we've got some data, so we proceed normally
    for entity in output_entities:
        build_big_entity(entity, result)

    LOG.debug("Produced %i entries in the feed", len(output_entities))
    return result


def build_big_entity(entity: FeedEntity, feed):
    feedentity = feed.entity.add()
    feedentity.vehicle.vehicle.id = entity.id
    feedentity.vehicle.vehicle.label = entity.label
    feedentity.vehicle.timestamp = int(datetime.now().timestamp())

    feedentity.id = random_word(4)

    feedentity.vehicle.position.longitude = entity.lon
    feedentity.vehicle.position.latitude = entity.lat
    feedentity.vehicle.position.speed = entity.speed
    feedentity.vehicle.position.bearing = entity.direction
    feedentity.vehicle.trip.route_id = ROUTE_ID_MAP[entity.trip_id]
