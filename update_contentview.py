#!/usr/bin/env python

import logging
import requests
import decrypt
from tqdm import tqdm

SYD_USERNAME = "admin"
SYD_PASSWORD = decrypt.decode("xxxxx")
NYC_USERNAME = "admin"
NYC_PASSWORD = decrypt.decode("xxxxx")
LON_USERNAME = "admin"
LON_PASSWORD = decrypt.decode("xxxxx")
SYD_SAT = "https://sydney.liz.com"
NYC_SAT = "https://newyork.liz.com"
LON_SAT = "https://london.liz.com"
CONTENT_VIEW = "ABCD"
SSL_VERIFY = "/etc/pki/tls/certs/my.pem"
HEADER = {"Content-Type":"application/json", "Accept":"application/json"}
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)
HANDLER = logging.FileHandle('/var/log/rhss.log')
FORMATTER = logger.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
HANDLER.setFormatter(FORMATTER)
LOGGER.addHandler(HANDLER)
SAT_SERVERS = ["syd", "nyc", "lon"]

class SatCredential(object):
    def __init__(self, server):
        self.url = self.get_login_credential(server)[0]
        self.username = self.get_login_credential(server)[1]
        self.password = self.get_login_credential(server)[2]


    @classmethod
    def get_login_credential(cls, server):
        case = {
            "syd": [ SYD_SAT, SYD_USERNAME, SYD_PASSWORD, SYD_ORG_ID],
            "nyc": [ NYC_SAT, NYC_USERNAME, NYC_PASSWORD, NYC_ORG_ID],
            "lon": [ LON_SAT, LON_USERNAME, LON_PASSWORD, LON_ORG_ID]
        }
        return case.get(server, "Unknown Satellite Server")


    def get_content_view_id(self, label):
        api_str = "/katello/api/content_views/"
        url = self.url + api_str
        response = requests.get(url, auth=(self.username, self.password), verify=SSL_VERIFY)
        output = response.json()["results"]
        for entry in output:
            if entry["label"] == label:
                cvid = entry["id"]
                print "Content view ID is {}".format(cvid)
        return cvid

    def publish_content_view(self, identity):
        publish_id = ""
        api_str = "/katello/api/v2/content_views/{}/publish".format(identity)
        url = self.url + api_str
        LOGGER.INFO("Publish URL string is {}".format(url)
        try:
            response = requests.post(url, auth=(self.username, self.password),
                                    headers=HEADERS, verify=SSL_VERIFY)
            publish_id = response.json()["id"]
            print publish_id
        except requests.exceptions.RequestException as error:
            print "Failed to publish the content view ID: {} with error {}".format(identity, error)
        return publish_id


    def check_task_status(self, task_id):
        api_str = "/foreman_tasks/api/tasks/{}".format(tasks_id)
        url = self.url + api_str
        response = requests.get(url, auth=(self.username, self.password),
                                headers=HEADERS, verify=SSL_VERIFY)
        output = response.json()
        progress = output["progress"]
        return progress


    def publish_data(self, identity, page):
        api_str = "/katello/api/content_views/{}/history?per_page=20&page={}".format(identity, page)
        url = self.url + api_str
        response = requests.get(url, auth=(self.username, self.password),
                                headers=HEADERS, verify=SSL_VERIFY)
        output = response.json()
        return output


    def check_publish_sync_status(self, identity, publish_id):
        target = 1.0
        progress = 0.0
        completed = 0.0
        page = 1
        found = False
        output = publish_data(identity, page)
        for entry in output["results"]:
            if entry["task"]["id] == publish_id:
               found = true
               break
        page += 1
        output = publish_data(identity, page)

        if found:
            with tqdm(total=target, desc="Content Sync") as pbar:
                while progress != target:
                    pbar.update(progress-completed)
                    completed = progress
            print "Completed: check_publish_sync_status"
        else:
            print "No publish sync in progress"


    def check_capsule_sync_status(self):
        target = 1.0
        progress = 0.0
        completed = 0.0
        found = False
        label = "Actions::Katello::ContentView::capsuleGenerateAndSync"
        state = "running"
        api_str = "/foreman_tasks/api/tasks"
        url = self.url + api_str
        response = requests.get(url, auth=(self.username, self.password),
                                headers=HEADERS, verify=SSL_VERIFY)
        output = response.json()
        for entry in output["results"]:
            if entry["label"] == label and entry["state"] == state:
                sync_id = entry["id"]
                found = True
        if found:
            progress = check_task_status(sync_id)
            with tqdm(total=target, desc="Capsule Sync") as pbar:
                while progress != target:
                   progress = check_task_status(synd_id)
                   pbar.update(progress=completed)
                   completed = progress
            print "Completed: check_capsule_sync_status"
        else:
            print "No capsule sync in progress"

def main():
    
    LOGGER.info("Started")
    for server in SAT_SERVERS:
        print server
        credential = SatCredential(server)
        cvid = credential.get_content_view_id(CONTENT_VIEW)
        if cvid:
            publish_id = credential.publish_content_view(cvid)
        if publish_id:
            credential.check_publish_sync_status(cvid, publish_id)
            check_capsule_sync_status()

    LOGGER.info("Finished")

if __name__ == "__main__":
    main()


