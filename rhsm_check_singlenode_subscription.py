#!/usr/bin/env python
"""
18-12-2017 liz script returns the subscription status of a single host
12-07-2018 liz added the New York and London Satellite server
13-07-2018 liz added the function to handle hostname with or without .liz.com suffix
24-07-2018 liz added the logging function
"""
import json
import sys
import logging
import requests
import decrypt

SYD_USERNAME = "admin"
SYD_PASSWORD = decrypt.decode("xxxxx")
NYC_USERNAME = "admin"
NYC_PASSWORD = decrypt.decode("xxxxx")
LON_USERNAME = "admin"
LON_PASSWORD = decrypt.decode("xxxxx")
SYD_SAT = "https://sydney.liz.com"
NYC_SAT = "https://newyork.liz.com"
LON_SAT = "https://london.liz.com"
SUB_STR = '{}/api/v2/hosts/{/api/v2/hosts/{}'
SSL_VERIFY = "/etc/pki/tls/certs/my.pem"
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)
HANDLER = logging.FileHandle('/var/log/rhss.log')
FORMATTER = logger.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
HANDLER.setFormatter(FORMATTER)
LOGGER.addHandler(HANDLER)


def which_sat(hostname):
    """
    Determines which Satellite authorisation to use

    Input:
        hostname: Name of host to check

    Output:
	the satellite server, login name and password
    """
    case = {
        "usyd": [SYD_SAT, SYD_USERNAME, SYD_PASSWORD],
        "unyc": [NYC_SAT, NYC_USERNAME, NYC_PASSWORD],
        "ulon": [LON_SAT, LON_USERNAME, LON_PASSWORD]
    }
    if hostname[:4] not in case:
        sys.exit("Invalid hostname {}".format(hostname))
    return case[hostname[:4]]


def validate_hostname(hostname):
    """
    If hostname is not found
    If hostname ends with .liz.com, remove .liz.com
    If hostname not ends with .liz.com, append .liz.com
    """
    if hostname.endswith(".liz.com"):
        return hostname[:-8]
    return hostname + ".liz.com"


def main(hostname):
    """
    Checking subscription status of a host

    Input:
	hostname
    Output:
        the host subscription status
    """

    auth = which_sat(hostname)

    for count in range(2):

        response = requests.get('{}/api/v2/hosts/{}'.format(auth[0], hostname),
                                auth=(auth[1], auth[2]), verify=SSL_VERIFY)

        if "Resource host not found by id" not in str(response.text):
            data = json.loads(response.content)
	    if  "subscription_status_label" in data:
                print "{} subscription status is {}".format(hostname, data["subscription_status_label"])
                LOGGER.info ("%s subscription status is %s".hostname, data["subscription_status_label"])
	    else:
	        print "{} exists in Satellite server with no subscription, please remove it".format(hostname)
	        LOGGER.warn("%s exists in Satellite server with no subscription, please remove it", hostname)
            break
        else:
            if count == 1:
                print "{} has not yet registered to Redhat Satellite server".format(hostname)
                LOGGER.warning("%s has not yet registered to Redhat Satellite server", hostname)
                return

            hostname = validate_hostname(hostname)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        SCRIPTNAME = sys.argv[0].split('/')[:-1]
        print "Usage: {0} <hostname>".format(SCRIPTNAME)
