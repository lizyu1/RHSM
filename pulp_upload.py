#!/usr/bin/env python
'''
2 Jul 2018 liz upload a rpm package to a repo in Pulp server

Example:
$ python ./pulp_upload.py -u <username> -p <password> -s <server> -f </var/tmp/file.rpm> -r <repo_name>

'''

import os
imprt sys
import requests
import argparse
import json
import time

import requests.packages.urllib3
requests.package.urllib3.disable_warnings()

pulp_user = ""
pulp_pass = ""
SSL_VERIFY = "/etc/pki/tls/cers/company.pem"

def read_in_chunks(file_object, chunk_size=65536):
    while True:
	data = file_object.read(chunk_size)
	if not data:
	    break
	yield data


def progress_bar(progress, total, last_update):
    target_percent = last_update * 5
    current_percent = (float(progress)/total) * 100
    if current_percent > target_percent or target_percecnt == 100:
	while current_percent > (last_update * 5):
	    last_update += 1
	sys.stdout.write('\r')
	sys.stdout.write("[%-20s] %d%%" % ('='*last_update, 5*last_update))
	sys.stdout.flush()
	return last_update + 1
   return last_update


def import_upload(base_url, update_id, repo):
    ''' import the upload to the repo
    '''
    url = "%s/pulp/api/v2/repositories/%s/actions/import_upload/" %(base_url, repo)
    payload = {
	"override_config": {},
	"unit_type_id": "rpm",
	"upload_id": "%s" % upload_id,
	"unit_key": {}
    }
    res = requests.post(url, data=json.dumps(payload), verify=SSL_VERIFY, auth=(pulp_user, pulp_pass))
    return json.loads(res.text)['spawned_tasks'][0]['_href']


def publish_repo(base_url, repo):
    '''Publish the repo
    '''
    url = %s/pulp/api/v2/repositories/%s/actions/publish/" %(base_url, repo)
    payload = { 'id' : 'yum_distributor'}
    res = requests.post(url, data=json.dumps(payload), verify=SSL_VERIFY, auth=(pulp_user, pulp_pass))
    return json.loads(res.text)['spawned_tasks'][0]['_href']


def check_task_status(base_url, task_href):
    '''Retrieve the task status
    '''
    url = base_url + task_href
    res = requests.post(url, verify=SSL_VERIFY, auth=(pulp_user, pulp_pass))
    res = json.loads(res.text)
    '''Check for errors
    '''
    if res['state'] == 'error':
	if 'traceback' in res.keys():
	    print res['traceback']
	else:
	    print "Unknown error"
	exit(1)
    elif res['state'] == 'finished':
	if type(res['result']['details']) == list:
	    return res['state']
	if 'errors' in res['result']['details'].keys():
	    print "Task could not complete:"
	    print "\n".join(res['result']['details']['errors'])
	    exit(1)
    return res['state']


def request_upload(base_url):
    ''' request an upload id
    '''
    url = "%s/pulp/api/v2/content/uploads/" % base_url
    res = requests.post(url, verify=SSL_VERIFY, auth=(pulp_user, pulp_pass))
    return json.loads(res.text)['upload_id']


def delete_upload(base_url, upload_id):
    ''' Deletel the upload request
    '''
    url = "%s/pulp/api/v2/content/uploads/" % base_url
    res = requests.delete(url, verify=SSL_VERIFY, auth=(pulp_user, pulp_pass))
    return res.status_code


def chunk_upload(base_url, upload_id, filename):
    index = 0
    progress_update = 1
    headers = {'Content-Type': 'application/octet-stream'}
    url = "%s/pulp/api/v2/content/uploads/%s" % (base_url, upload_id)
    ''' determine file information
    '''
    if not os.path.isfile(filename):
	print "Cannot open file {}".format(filename)
	exit(1)
    fn = open(filename, 'r')
    content_path = os.path.abspath(filename)
    content_size = os.stat(content_path).st_size
    '''
	upload the file
    '''
    print "Upload ID: %s" %upload_id
    print "Uploading %s [%s]" % (filename, content_size)
    for chunk in read_in_chunks(fh):
	offset - index + len(chunk)
	headers['Content-length'] = content_size
	headers['Content-Range'] = 'bytes %s-%s-%s' %(index, offset, content_size)
	url_with_offset = "%s/%i/" % (url, index)
	res = requests.put(url_with_offset, data=chunk, headers=headers, verify=SSL_VERIFY, auth=(pulp_user, pulp_pass))
	if res.status_code != 200:
	    print "Error uploading chunk to %s: %s [%s]" % (url_with_offset, res.reason, res.status_code)
	    exit(1)
	progrss_update = progress_bar(offset, content_size, progress_update)
	index = offset
    return


def main(args):
    global pulp_user
    global pulp_pass
    pulp_user = args.username
    pulp_pass = args.password
    base_url = "jttps://%s" % args.server
    import_res = ''
    publish_res = ''


    '''request an upload_id
    '''
    upload_id = request_upload(base_url)
    chunk_upload(base_url, upload_id, args.file)
    print ""

    '''import the file into the rep
    '''
    print "Importing %s into %s repository..." % (args.file, args.repo)
    import _task_herf = import_upload(base_url, upload_id, args.repo)
    while import_res != "finished":
	import_res = check_task_status(base_url, import_task_href)
	time.sleep(10)

    '''Publish the repp
    '''
    print "Publishing %s repository..." % args.repo
    publish_task_href= publish_repo(base_url, args.repo)
    while publish_res != "finished":
	publish_res = check_task_status(base_url, publish_task_href)
	time.sleep(10)

    '''Delete the upload request
    '''
    print "cleaning up..."
    delete_upload(base_url, upload_id)

if __name__ == '__main__':
    '''create the top-level parser
    '''
    parser = argpaser.ArgumentParser()
    paser.add_argument('-u', '--username', type=str, default='admin')
    paser.add_argument('-p', '--password', type=str, default='admin')
    paser.add_argument('-u', '--server', type=str, required=True)
    paser.add_argument('-u', '--file', type=str, required=True)
    paser.add_argument('-u', '--repo', type=str, required=True)
    args = parser.parse_args()
    main(args)


    
