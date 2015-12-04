import json
import redis
import os


def get_redis():
    if os.environ['PRODUCTION'] == "0":
        vcap_services = json.loads(os.environ['VCAP_SERVICES'])
        redis_host = vcap_services['redis'][0]['credentials']['host']
        redis_port = vcap_services['redis'][0]['credentials']['port']
        redis_password = vcap_services['redis'][0]['credentials']['password']

        redis_connection = redis.StrictRedis(host=redis_host, port=redis_port, db=0, password=redis_password)
    else:
        redis_connection = redis.StrictRedis(host='localhost', port=6379, db=0)
    return redis_connection
