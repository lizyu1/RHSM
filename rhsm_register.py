#!/usr/bin/env python
"""
This module registers a host against a Satellite Server

Example:
  $ rhsm_register.py myhost 7

History:
  1-12-2017 liz Register the host to Redhat Satellite server Sydney
  15-5-2018 liz Register the host to Redhat Satellite server New York
  16-5-2018 liz Add 3rd command line arguement of major RHEL version integer, e.g. 6 or 7
  12-07-2018 liz import argparse
  24-07-2018 liz add logging
"""

import json
import sys
import argparse
import logging
import requests
import decrypt

PARSER = argparse.ArgumentParser()
PARSER.add_argument("hostname", help="myhost")
PARSER.add_argument("RHEL_major_release_number", help="6 or 7")
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


def which_sat(hostname):
    """ Determines which Satellite authorisation to use based on hostname

    Input:
      hostname = hostname of node

    Output:
      Success: truncated host name
      Failure: invalid host message
    """
    case = {
        "usyd": [SYD_SAT, SYD_USERNAME, SYD_PASSWORD],
        "unyc": [NYC_SAT, NYC_USERNAME, NYC_PASSWORD],
        "ulon": [LON_SAT, LON_USERNAME, LON_PASSWORD]
    }
    return case.get(hostname[:4], "Invalid host")


def content_view_and_lifecycle(hostname, os_version):
    """ Determines which Satellite Content View and Lifecycle Environment to use

    Input:
      hostname: Name of node to check
      os_version: Major version of OS

    Output:
      Success: truncated host name and os version
      Failure: invalid RHEL version message
    """
    case = {
        "usyd,6": [13, 1],
        "usyd,7": [12, 1],
        "unyc,6": [11, 2],
        "unyc,7": [10, 2],
        "ulon,6": [5, 2],
        "ulon,7": [6, 2]
    }
    return case.get("{},{}".format(hostname[:4], os_version), "Invalid RHEL version")


def main(hostname, osname):
    """ Registers host with Satellite server

    Input:
      hostname: Name of node to register
      OS major release number: OS Major release number

    Output:
      Success: N/A
      Failure: Help message
    """
    # hostname = args[0]
    # osname = args[1]
    auth = which_sat(hostname)

    result = requests.get('{}/api/v2/hosts/{}'.format(auth[0], hostname),
                          auth=(auth[1], auth[2]), verify=SSL_VERIFY)
    headers = {'Content-type': 'application/Json', 'Accept': 'text/plain'}
    payload = {}
    payload['name'] = hostname
    payload['content_view_id'] = content_view_and_lifecycle(hostname, osname)[0]
    payload['lifecycle_environment_id'] = content_view_and_lifecycle(hostname, osname)[1]
    print payload

    try:
        add_subscription = requests.post('{}/api/v2/hosts/subscriptions'.format(auth[0]),
                                         headers=headers, data=json.dumps(payload),
                                         auth=(auth[1], auth[2]), verify=SSL_VERIFY)
        print add_subscription.text
        if add_subscription.ok:
            print "Successful added the subscription for {}".format(hostname)
            LOGGER.info( "Successful added the subscription for %s", hostname)
    except requests.exceptions.RequestException as error:
        print "Failed to add subscription {}".format(hostname)
        LOGGER.warning("Failed to add subscription %s", hostname)
        LOGGER.warning(error)
        LOGGER.warning(result.text)


if __name__ == "__main__":
    ARGS = PARSER.parse_args()
    main(sys.argv[1], sys.argv[2])
