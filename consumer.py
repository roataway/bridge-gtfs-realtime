"""Simple test tool to consume GTFS-RT feeds and dump them to stdout. Usage:
`python consumer.py <URL>`, examples:
python consumer.py https://data.texas.gov/download/eiei-9rpf/application%2Foctet-stream
python consumer.py https://localhost:5000/get_data
"""
import logging
from time import sleep
import sys

import requests
from google.transit import gtfs_realtime_pb2

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)5s %(funcName)s - %(message)s")

    feed_url = sys.argv[-1]
    logging.info('Consuming GTFS-RT from %s', feed_url)
    while True:
        r = requests.get(feed_url)
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(r.content)
        logging.debug(feed)

        logging.debug('------------------- getting another message in 30s')
        sleep(30)
