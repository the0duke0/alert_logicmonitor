import sys
import json
import urllib
import base64
import csv
import gzip
from collections import OrderedDict


def send_request(url, device_id, property_name, property_value, token, user_agent='Splunk'):
    if url is None:
        sys.stderr.write("ERROR No URL provided\n")
        return False
    
    url = url.rstrip("/") + "/device/devices/%s?patchFields=customProperties&opType=replace" % device_id

    body_dict = {
        "CustomProperties": [
            {
                "name": property_name,
                "value": property_value
            }
        ]
    }
    body = json.dumps(body_dict)
    sys.stderr.write("INFO Sending POST request to url=%s with size=%d bytes payload\n" % (url, len(body)))
    sys.stderr.write("DEBUG Body: %s\n" % body)
    try:
        req = urllib.request.Request(url, body, {"Content-Type": "application/json", "User-Agent": user_agent})
        req.add_header("X-HTTP-Method-Override", "PATCH")
        req.add_header("Authorization", "Bearer %s" % token) 
        res =  urllib.request.urlopen(req)
        if 200 <= res.code < 300:
            sys.stderr.write("INFO LogicMonitor responded with HTTP status=%d\n" % res.code)
            return True
        else:
            sys.stderr.write("ERROR LogicMonitor responded with HTTP status=%d\n" % res.code)
            return False
    except urllib.error.HTTPError as e:
        sys.stderr.write("ERROR Error sending LogicMonitor request: %s\n" % e)
    except urllib.error.URLError as e:
        sys.stderr.write("ERROR Error sending LogicMonitor request: %s\n" % e)
    except ValueError as e:
        sys.stderr.write("ERROR Invalid URL: %s\n" % e)
    return False


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] != "--execute":
        sys.stderr.write("FATAL Unsupported execution mode (expected --execute flag)\n")
        sys.exit(1)
    try:
        settings = json.loads(sys.stdin.read())
        url = settings['configuration'].get('url')
        device_id = settings['configuration'].get('device_id')
        property_name = settings['configuration'].get('property_name')
        property_value = settings['configuration'].get('property_value')
        token = settings['configuration'].get('token')
#       body = settings.get('result')
        user_agent = settings['configuration'].get('user_agent', 'Splunk')
        if not send_request(url, device_id, property_name, property_value, token, user_agent=user_agent):
            sys.exit(2)
    except Exception as e:
        sys.stderr.write("ERROR Unexpected error: %s\n" % e)
        sys.exit(3)
