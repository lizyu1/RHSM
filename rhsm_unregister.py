#!/usr/bin/python
# 23-10-2017 liz

import json
import sys
import decrypt


try:
    import requests
except ImportError:
    print "Please install the python-requests module."
    sys.exit(-1)

USERNAME = "admin"
PASSWORD = decrypt.decode("jfkldergdlfgkdlfkgjdlsidfgk20o=")
SSL_VERIFY = "/etc/pki/tls/certs/my_SHA256.pem"


def main(hostname):
    """
    Performs a GET using the passed URL location
    """

    r = requests.get('https://url/api/v2/hosts/{0}'.format(hostname), auth=(USERNAME, PASSWORD), verify=SSL_VERIFY)

    if not "Resoure host not found by id" in str(r.text):
        d = json.loads(r.content)
        id = d["id"]

        try:
	    delete_subscription = requests.delete('https://url/api/v2/hosts/%s/subscriptions' %id, auth=(USERNAME, PASSWORD), verify=SSL_VERIFY)
	    print delete_subscription.text
	    if delete_subscription.status_code.ok:
	        print "Subscription successfully removed"
	    delete_host = requests.delete('https://url/api/v2/hosts/{0}'.format(id), auth=(USERNAME, PASSWORD), verify=SSL_VERIFY)
	    if delete_host.ok:
	        print "Delete host from Satellite server successful"

    	except:
	    print "Unable to delete subscription"		

    else:
	print "System has not yet registered to Redhat Satellite server"

if __name__ == "__main__":
  if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        scriptname = sys.argv[0].split('/')[:-1]
        print("Usage: {0} <hostname>".format(scriptname))
