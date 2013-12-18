#!/usr/bin/env python

import httplib2
import pprint
import sys
import os
from apiclient import sample_tools
from apiclient import errors
from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.client import flow_from_clientsecrets
from oauth2client import client
from oauth2client.file import Storage

# Check https://developers.google.com/drive/scopes for all available scopes
OAUTH_SCOPE = 'https://www.googleapis.com/auth/drive'
# Redirect URI for installed apps
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'

# Run through the OAuth flow and retrieve credentials
#flow = OAuth2WebServerFlow(CLIENT_ID, CLIENT_SECRET, OAUTH_SCOPE, REDIRECT_URI)
flow = flow_from_clientsecrets("client_secrets.json", OAUTH_SCOPE, REDIRECT_URI)
authorize_url = flow.step1_get_authorize_url()
print 'Go to the following link in your browser: ' + authorize_url
code = raw_input('Enter verification code: ').strip()
credentials = flow.step2_exchange(code)
storage = Storage('credentials')
storage.put(credentials)

# Create an httplib2.Http object and authorize it with our credentials
http = httplib2.Http()
http = credentials.authorize(http)

# Service
drive_service = build('drive', 'v2', http=http)

# Insert a file
#media_body = MediaFileUpload(FILENAME, mimetype='text/plain', resumable=True)
#body = {
#  'title': 'My document',
#  'description': 'A test document',
#  'mimeType': 'text/plain'
#}

#file = drive_service.files().insert(body=body, media_body=media_body).execute()
#pprint.pprint(file)

def retrieve_all_files(service):
    """Retrieve a list of File resources.
    
    Args:
    service: Drive API service instance.
    Returns:
    List of File resources.
    """
    result = []
    page_token = None
    while True:
        try:
            param = {}
            if page_token:
                param['pageToken'] = page_token
            files = service.files().list(**param).execute()

            result.extend(files['items'])
            page_token = files.get('nextPageToken')
            if not page_token:
                break
        except errors.HttpError, error:
            print 'An error occurred: %s' % error
            break
    return result

# Only title, (first for now)owner, (in TODO)permissions, modified 
def show_files(files):
    print "Title     Owner    Permission    Modified"
    for f in files:
        show_file(f)

def show_file(f):
    print "{:30s}|{:16s}|{:16s}|{:19}".format(f["title"][:20].encode('utf8'), \
                                                  f["ownerNames"][0][:16].encode('utf8'),\
                                                  "perms",\
                                                  f["modifiedDate"][:10].encode('utf8', 'ignore'))


def show_help(args):
    print "Usage: {}"
    print "No argument is required yet"

def show_commands():
    print "get_info"
    print "add_to_group <user> <group>" 
    print "rm_from_group <user> <group>"
    print "add_user <user> <file|folder>"
    print "rm_user <user> <file|folder>"
    print "add_group <group> <file|folder>"
    print "rm_group <group> <file|folder>"
    print "get_info"
    print "help"
    print "exit"

def main(args):
    if len(args) == 2 and args[1] in ['-h', '--help', '--h']:
        return show_help(args)
    if len(args) != 1:
        return show_help(args)
   
    while True:
        input_args = raw_input('command: ').strip()
        input_args = map(str.strip, input_args.split())
        if len(input_args) == 0:
            continue
        if input_args[0] == 'help':
            show_commands()
        if input_args[0] == 'get_info':
            show_files(retrieve_all_files(drive_service))
        if input_args[0] == 'add_to_group':
            continue
        if input_args[0] == 'rm_from_group':
            continue
        if input_args[0] == 'add_user':
            continue
        if input_args[0] == 'rm_user':
            continue
        if input_args[0] == 'exit':
            break
    return 



if __name__=="__main__":
    sys.exit(main(sys.argv))
