import json, requests
from SonarSettings import headers



def get_json_from_api(url, params):
    resp = requests.get(url = url, headers=headers, params = params, verify=False)
    if not resp.ok:
        new_url = resp.request.url.replace('%253A', ':').replace('%252C', ',').replace('%252F', '/')
        resp = requests.get(url = new_url, headers=headers, verify=False)
    #get_normal_logger().info('Json : {0}'.format(resp.text))
    return json.loads(resp.text)
#     print resp.text
#     return resp
