#!/usr/bin/env python
"""
 Check all the subscriptions, remove the one which does not exist in DNS

 18-12-2017 liz Initial code
 9-1-2018 liz Added email function
 10-7-2018 liz Added New York and London Satellite servers
 12-7-2018 liz Added create Remedy ticket function
"""

import json
import sys
import os
import smtplib
from email.mime.text import MIMEText
import rhsm_unregister
import decrypt

try:
    import requests
except ImportError:
    print "Please install the python-requests module."
    sys.exit(-1)


SYD_USERNAME = "admin"
SYD_PASSWORD = decrypt.decode("xxxxx")
NYC_USERNAME = "admin"
NYC_PASSWORD = decrypt.decode("xxxxx")
LON_USERNAME = "admin"
LON_PASSWORD = decrypt.decode("xxxxx")
SYD_SAT = "https://sydney.liz.com"
NYC_SAT = "https://newyork.liz.com"
LON_SAT = "https://london.liz.com"
SYD_PHYSICAL_ID = "69" #Get the ID from one of the virt_only:false license
SYD_VIRTUAL_ID = "83"  #Get the ID from one of the virt_only:true license
NYC_PHYSICAL_ID = "4"
NYC_VIRTUAL_ID = "12"
LON_PHYSICAL_ID = "19"
LON_VIRTUAL_ID = "9"
SYD_ORG_ID = "1"  # Organization ID
NYC_ORG_ID = "3"
LON_ORG_ID = "3"
SSL_VERIFY = "/etc/pki/tls/certs/my.pem"
SUB_STR = "/katello/api/organizations/{}/subscriptions/{}"


def dns(hostname):
    """
    hostname nslookup
    if not found in DNS, then remove its subscription
    """
    if os.system('nslookup ' + hostname + '>/dev/null') == 256:
        print "{} does not exist in DNS, removing its subscription".format(hostname)
        rhsm_unregister.main(hostname)
    else:
        print "{0} is in DNS".format(hostname)


def get_license_id(sat_server):
    """
    Input:
	Satellite Server
    Output:
	Login credential, Physical license ID and Virtual license ID, Organization ID
    """
    case = {
        "sydney": [SYD_SAT, SYD_USERNAME, SYD_PASSWORD, SYD_PHYSICAL_ID, SYD_VIRTUAL_ID,
                        SYD_ORG_ID],
        "newyork": [NYC_SAT, NYC_USERNAME, NYC_PASSWORD, NYC_PHYSICAL_ID, NYC_VIRTUAL_ID,
                        NYC_ORG_ID],
        "london": [LON_SAT, LON_USERNAME, LON_PASSWORD, LON_PHYSICAL_ID, LON_VIRTUAL_ID,
                        LON_ORG_ID]
    }
    return case.get(sat_server, "Unknown Satellite Server")


def check_usage(license_id):
    """
    for each Physical and Virtual license ID, return the count of the free and total licenses
    """
    sat_server = license_id[0]
    sat_server_username = license_id[1]
    sat_server_password = license_id[2]
    physical_license_id = license_id[3]
    virtual_license_id = license_id[4]
    sat_server_org_id = license_id[5]

    counts = []
    for lic_id in [physical_license_id, virtual_license_id]:
        url = sat_server + SUB_STR.format(sat_server_org_id, lic_id)
        response = requests.get(url, auth=(sat_server_username, sat_server_password),
                                verify=SSL_VERIFY)
        data = json.loads(response.content)
        counts.append([data['available'], data['quantity']])
    return counts


def sendmail_if_required(sat_server, license_counts, host_count):
    """
    send the email to Unix team advising running low on license.
    since we have 4000 license in Sydney, this function will trigger when we have used 3550.
    """
    physical_available = license_counts[0][0]
    virtual_available = license_counts[1][0]
    physical_total = license_counts[0][1]
    virtual_total = license_counts[1][1]

    if "london" in sat_server:
        sat_server = "London Satellite Server"
    elif "newyork" in sat_server:
        sat_server = "New York Satellite Server"
    else:
        sat_server = "Sydney Satellite Server"

    sender = "RHSM_usage_alert_{}".format(sat_server)
    receiver = "lizy@gmail.com"

    if virtual_total == -1:
        virtual_total = "unlimited"
    if physical_total == -1:
        physical_total = "unlimited"

    if host_count > 3550:
        html = """\
        <html>
          <head></head>
            <body>
                <p>Unix team,<br><br>
	 	Total host registered on the {{{sat_server}}} are {{{host_count}}}.</br>
                Total licenses are {{{virtual_total}}}.<br>
             </p>
           </body>
         </html>
         """.format(virtual_total=virtual_total, sat_server=sat_server, host_count=host_count)

        msg = MIMEText(html, 'html')
        msg['Subject'] = "Running low on RedHat Satellite licenses {}".format(sat_server)
        msg['From'] = sender
        msg['To'] = receiver

        smtp = smtplib.SMTP('localhost')
        smtp.sendmail(sender, receiver, msg.as_string())
        smtp.quit()

    print "Available licenses for Physical are {}/{}".format(physical_available, physical_total)
    print "Available licenses for Virtual are {}/{}".format(virtual_available, virtual_total)


def check_total_hosts_registered(sat_server, sat_server_username, sat_server_password):
    """
    report the number of hosts have been registered
    """
    page = 1
    host_count = 0
    while True:
        url = "{}/api/v2/hosts?per_page=20&page={}&full_results=true".format(sat_server, page)
        response = requests.get(url, auth=(sat_server_username, sat_server_password),
                                verify=SSL_VERIFY)
        data = json.loads(response.content)
        for i in data['results']:
            host = i['certname']
            if "hpe" not in host and "virt-who" not in host:
                host_count += 1
                dns(host)
        if not data['results']:
            break
        page += 1
    print "Number of hosts registered are {}".format(host_count)
    return host_count


def send_ticket_to_remedy(sat_server, host_count):
    """
    create remedy ticket when 3550/4000 hosts have been registered
    """

    if host_count < 3500:
        severity = "NONE"
    elif host_count > 3500:
        severity = "MINOR"
    elif host_count > 3550:
        severity = "MAJOR"

    if severity == "MINOR" or severity == "MAJOR":
        summary = "".join(("/usr/local/bin/post_msg -r {} -m ".format(severity)
                           , "'{} is running low on RedHat licenses'".format(sat_server)
                           , "hostname=sat_server sub_source=UNIX "
                          ))
        print "Create Remedy ticket {}".format(summary)
        os.system(summary)


def main():
    """
    report the subscription usage on each Satellite servers, send email and create remedy
    ticket if we are running low in licenses
    """
    sat_servers = ["sydney", "newyork", "london"]
    for server in sat_servers:
        print server
        license_id = get_license_id(server)
        sat_server = get_license_id(server)[0]
        sat_server_username = get_license_id(server)[1]
        sat_server_password = get_license_id(server)[2]
        license_counts = check_usage(license_id)
        host_count = check_total_hosts_registered(sat_server, sat_server_username,
                                                  sat_server_password)
        sendmail_if_required(sat_server, license_counts, host_count)
        send_ticket_to_remedy(sat_server, host_count)

if __name__ == "__main__":
    main()
