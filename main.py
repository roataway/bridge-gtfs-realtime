import gtfs_realtime_pb2 as GTFS_real_time_proto



    # do something with read_metric

if __name__ == '__main__':
    with open('vehicle_position.pb', 'rb') as f:
        read_metric = GTFS_real_time_proto.FeedMessage()
        read_metric.ParseFromString(f.read())
        print(read_metric)
