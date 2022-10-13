import json, requests
from loggerTools import get_normal_logger

def get_json_from_api(url, params):
    resp = requests.get(url = url, params = params)
    #get_normal_logger().info('Json : {0}'.format(resp.text))
    return json.loads(resp.text)
