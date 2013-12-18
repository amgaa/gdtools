#!/usr/bin/env python

import httplib2
import pprint
import sys
import os
#from apiclient.discovery import build
#from apiclient.http import MediaFileUpload
#from oauth2client.client import OAuth2WebServerFlow
from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from oauth2client.client import OAuth2WebServerFlow


INFO  = {}
f = open('auth_file.txt', 'r')
for line in f:
    head, body = line.split(':')
    INFO[head.strip()] = body.strip()

if not INFO.has_key("CLIENT_ID"):
    print "CLIENT_ID is not written in file auth_file.txt"
    exit(1)

if not INFO.has_key("CLIENT_SECRET"):
    print "CLIENT_SECRET is not written in file auth_file.txt"
    exit(1)

# Copy your credentials from the console
CLIENT_ID = INFO["CLIENT_ID"]
CLIENT_SECRET = INFO["CLIENT_SECRET"]

# Check https://developers.google.com/drive/scopes for all available scopes
OAUTH_SCOPE = 'https://www.googleapis.com/auth/drive'

# Redirect URI for installed apps
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'

# Path to the file to upload
FILENAME = 'document.txt'

# Run through the OAuth flow and retrieve credentials
flow = OAuth2WebServerFlow(CLIENT_ID, CLIENT_SECRET, OAUTH_SCOPE, REDIRECT_URI)
authorize_url = flow.step1_get_authorize_url()
print 'Go to the following link in your browser: ' + authorize_url
code = raw_input('Enter verification code: ').strip()
credentials = flow.step2_exchange(code)

# Create an httplib2.Http object and authorize it with our credentials
http = httplib2.Http()
http = credentials.authorize(http)

drive_service = build('drive', 'v2', http=http)

# Insert a file
media_body = MediaFileUpload(FILENAME, mimetype='text/plain', resumable=True)
body = {
  'title': 'My document',
  'description': 'A test document',
  'mimeType': 'text/plain'
}

file = drive_service.files().insert(body=body, media_body=media_body).execute()
pprint.pprint(file)



def show_help(args):
    print "Usage:  {0} [OPTION] ".format(args[0]) 
    print  "[ --add_to_group <user> <group> ]" 
    print " [ --rm_from_group <user> <group> ]"
    print " [ --add_user <user> <file|folder> ]"
    print " [ --rm_user <user> <file|folder> ]"
    print " [ --add_group <group> <file|folder> ]"
    print " [ --rm_group <group> <file|folder> ]"
    print " [ --get_info ]"
    print " [ -h | --help ]"
    return

def retreive_info():
    return 

def main(args):

    if args[1] not in ['--add_to_group',      \
                           '--rm_from_group', \
                           '--add_user',      \
                           '-rm_user',        \
                           '--get_info'] or   \
       args[1] in ['-h', '--help', '--h']:
        show_help(argv)
   
    if args[1] == '--list':
        return retreive_info()
        



if __name__=="__main__":
    sys.exit(main(sys.argv))

