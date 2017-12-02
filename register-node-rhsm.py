#!/usr/bin/python
# 1-12-2017 lyu14 Register the host to Redhat Satellite server

import json
import sys


try:
    import requests
except ImportError:
    print "Please install the python-requests module."
    sys.exit(-1)

USERNAME = "user"
PASSWORD = "passwd"

SSL_VERIFY = False

def main(hostname):

    r = requests.get('https://url/api/v2/hosts/{0}'.format(hostname), auth=(USERNAME, PASSWORD), verify=SSL_VERIFY)
#    print r.text
    d = json.loads(r.content)
    headers = {'Content-type': 'application/Json', 'Accept': 'text/plain'}
    payload = {}
    payload['name'] = hostname
    payload['lifecycle_environment_id'] = 1
    os = d["operatingsystem_name"]
    if os == "RedHat 7.3":
        payload['content_view_id']= 12
    else:
        payload['content_view_id']= 13


    try:
        add_subscription = requests.post('https://url/api/v2/hosts/subscriptions', headers=headers, data=json.dumps(payload), auth=(USERNAME, PASSWORD), verify=SSL_VERIFY)
        print add_subscription.text
        if add_subscription.status_code == 200:
            print "Successful subscription"
    except:
        pass

if __name__ == "__main__":
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        scriptname = sys.argv[0].split('/')[:-1]
        print "Usage: {0} <hostname>".format(scriptname)

