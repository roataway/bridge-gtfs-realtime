# after this many seconds, vehicle states will expire and will be removed from the global data structure
STATE_TTL = 5 * 60

# keep up to this many vehicles in the state data structure. RTEC has <400 units, so this should be OK
MAX_VEHICLES = 500

# roataway API coordinates for the MQTT data stream
MQTT_BROKER = 'opendata.dekart.com'
MQTT_PORT = 1945


FORMAT_TIME = '%Y-%m-%dT%H:%M:%SZ'

# http response to return when we've got an empty feed
NO_CONTENT = ('', 204)