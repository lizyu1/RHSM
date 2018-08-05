#!/usr/bin/env python
"""
It will unregister the host and then remove it from the Satellite server

Example:
  $ rhsm_unregister.py myhostname

History:
  23-10-2017 liz    Initial creation
  17-05-2018 liz    Add functions to un-register host in New York Red Hat Satellite Server
  11-07-2018 liz    Add functions to handle hostname and hostname.liz.com
  12-07-2018 liz    Import argparse
  24-07-2018 liz    Import logging
"""

import json
import sys
import argparse
import logging
import requests
import decrypt

PARSER = argparse.ArgumentParser()
PARSER.add_argument("hostname", help="usydind12345")
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)
HANDLER = logging.FileHandle('/var/log/rhss.log')
FORMATTER = logger.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
HANDLER.setFormatter(FORMATTER)
LOGGER.addHandler(HANDLER)
SYD_USERNAME = "admin"
SYD_PASSWORD = decrypt.decode("xxxxx")
NYC_USERNAME = "admin"
NYC_PASSWORD = decrypt.decode("xxxxx")
LON_USERNAME = "admin"
LON_PASSWORD = decrypt.decode("xxxxx")
SYD_SAT = "https://sydney.liz.com"
NYC_SAT = "https://newyork.liz.com"
LON_SAT = "https://london.liz.com"
SSL_VERIFY = "/etc/pki/tls/certs/my.pem"
SUB_STR = '{}/api/v2/hosts/{}/subscriptions'


def which_sat(hostname):
    """
    Determines which Satellite authorisation to use

    Input:
        hostname: Name of host to check

    Output:
        Success: Returns truncated hostname
        Failure: Returns invalid host message
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
        hostname = hostname[:-8]
        return hostname[:-8]
    return hostname + ".liz.com"


def main(hostname):
    """
    Unregisters host from Red Hat Satellite server

    Input:
        Hostname: Name of host to unregister

    Output:
        Success: Success messages
        Failure: Failure messages
    """
    auth = which_sat(hostname)

    for count in range(2):

        response = requests.get('{}/api/v2/hosts/{}'.format(auth[0], hostname),
                                auth=(auth[1], auth[2]), verify=SSL_VERIFY)

        if "Resource host not found by id" not in str(response.text):
            details = json.loads(response.content)
            ident = details["id"]
            break
        else:
            if count == 1:
                print "{} not registered to Redhat Satellite server {}".format(hostname, auth[0])
                LOGGER.info("%s not registered to Redhat Satellite server %s", hostname, auth[0])
                return

            hostname = validate_hostname(hostname)

    try:
        delete_subscription = requests.delete(SUB_STR.format(auth[0], ident),
                                              auth=(auth[1], auth[2]), verify=SSL_VERIFY)
        print delete_subscription.text
        if delete_subscription.ok:
            print "Successfully deleted the subscription for {}".format(hostname)
            LOGGER.info("Successfully deleted the subscription for %s", hostname)
        delete_host = requests.delete('{}/api/v2/hosts/{}'.format(auth[0], ident),
                                      auth=(auth[1], auth[2]), verify=SSL_VERIFY)
        if delete_host.ok:
            print "Successfully deleted the host {} from Satellite server".format(hostname)
            LOGGER.info("Successfully deleted the host %s from Satellite server", hostname)
    except requests.exceptions.RequestException as error:
        print "Unable to delete subscription for {}".format(hostname)
        LOGGER.info("Unable to delete subscription for %s", hostname)
        LOGGER.warning(error)
        LOGGER.warning(delete_subscription, delete_host)


if __name__ == "__main__":
    ARGS = PARSER.parse_args()
    main(sys.argv[1])
