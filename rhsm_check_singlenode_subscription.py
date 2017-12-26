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
PASSWORD = decrypt.decode("jfkldergdlfgkdlfkgjdlsidfgk20o="
SSL_VERIFY = "/etc/pki/tls/certs/my_SHA256.pem"


def main(hostname):

    r = requests.get('https://url/api/v2/hosts/{0}'.format(hostname), auth=(USERNAME, PASSWORD), verify=SSL_VERIFY)

    if not "Resoure host not found by id" in str(r.text):
        d = json.loads(r.content)
        print "Subscription status is {0}".format(d["subscription_status_label"])
    else:
        print "Host not found"


if __name__ == "__main__":
  if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        scriptname = sys.argv[0].split('/')[:-1]
        print("Usage: {0} <hostname>".format(scriptname))
