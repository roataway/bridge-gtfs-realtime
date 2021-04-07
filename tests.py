import unittest
from datetime import datetime

from structures import FeedEntity
from gtfs_realtime import create_gtfs_proto_entity


class MyTestCase(unittest.TestCase):
    def test_something(self):
        json = '{"latitude": 46.983774, "longitude": 28.860348, "speed": 16, "direction": 136, "timestamp": ' \
               '"2021-03-20T12:18:10Z", "board": "1296", "rtu_id": "0000362", "route": "22"} '
        topic = "0"
        feedEntity = FeedEntity(json, topic, datetime.now().timestamp())
        feedEntity1 = FeedEntity(json, "1", datetime.now().timestamp())
        feedEntity2 = FeedEntity(json, "2", datetime.now().timestamp())
        feedEntity3 = FeedEntity(json, "3", datetime.now().timestamp())
        feedEntity4 = FeedEntity(json, "4", datetime.now().timestamp())
        feedEntity5 = FeedEntity(json, "5", datetime.now().timestamp())
        d_q={
            "0" : [feedEntity],
            "1" : [feedEntity1],
            "2" : [feedEntity2],
            "3" : [feedEntity3],
            "4" : [feedEntity4],
            "5" : [feedEntity5],
        }
        create_gtfs_proto_entity(d_q)

        assert feedEntity is not None


if __name__ == '__main__':
    unittest.main()
