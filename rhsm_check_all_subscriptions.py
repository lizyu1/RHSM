#!/usr/bin/python
# 23-10-2017 liz

import json
import sys
import os
import rhsm_unregister
import decrypt


try:
    import requests
except ImportError:
    print "Please install the python-requests module."
    sys.exit(-1)

USERNAME = "admin"
PASSWORD = decrypt.decode("jfkldergdlfgkdlfkgjdlsidfgk20o="
SSL_VERIFY = "/etc/pki/tls/certs/my_SHA256.pem"


def dns(hostname):
    if os.system('nslookup ' + hostname + '>/dev/null') == 256:
	print "This host " + hostname + " does ot exist in DNS, remove its subscription")
	rhsm_unregister.main(hostname)
    else:
	print hostname, " is in DNS"


def main():
    page = 1
    host_count = 0
    while True:
	URL = "https://url/api/v2/hosts?per_page=20&page={0}&full_results=true".format(page)
        r = requests.get(URL, auth=(USERNAME, PASSWORD), verify=SSL_VERIFY)
        d = json.loads(r.content)
        for i in d['results']:
            host=i['certname']
            host_count+=1
            dns(hostname)

            if len(d['results']) == 0:
                break
                page+=1

        print "Number of hosts registered are {0}".format(host_count)
        

if __name__ == "__main__":
  main()
