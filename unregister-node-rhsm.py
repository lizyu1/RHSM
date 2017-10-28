#!/usr/bin/python
# 23-10-2017 liz

import json
import sys


try:
    import requests
except ImportError:
    print "Please install the python-requests module."
    sys.exit(-1)

USERNAME = "username"
PASSWORD = "password"
# Ignore SSL for now
SSL_VERIFY = False


def main(hostname):
    """
    Performs a GET using the passed URL location
    """

    r = requests.get('https://url/api/v2/hosts/{0}'.format(hostname), auth=(USERNAME, PASSWORD), verify=SSL_VERIFY)

    print r.text
    d = json.loads(r.content)
    id = d["id"]
    print id

    try:
	delete_subscription = requiests.delete('https://url/api/v2/hosts/%s/subscriptions' %id, auth=(USERNAME, PASSWORD), verify=SSL_VERIFY)
	print delete_subscription.text
	if delete_subscription.status_code == 200:
	    print "Subscription successfully removed"
    except:
	pass


if __name__ == "__main__":
  if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        scriptname = sys.argv[0].split('/')[:-1]
        print("Usage: {0} <hostname>".format(scriptname))
