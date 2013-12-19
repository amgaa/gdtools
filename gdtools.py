#!/usr/bin/env python

import httplib2
import pprint
import sys
import os
import time
from apiclient import sample_tools
from apiclient import errors
from oauth2client import client
from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.client import flow_from_clientsecrets
from oauth2client import client
from oauth2client.file import Storage
import gdfuncs


def main(args):
    if len(args) == 2 and args[1] in ['-h', '--help', '--h']:
        return gdfuncs.show_help(args)
    if len(args) != 1:
        return gdfuncs.show_help(args)
    OAUTH_SCOPE = 'https://www.googleapis.com/auth/drive'
# Redirect URI for installed apps
    REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'
# Run through the OAuth flow and retrieve credentials
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


    t_start = time.time()
    while True:
        t_now = time.time()
        if t_now - t_start > 10:
            t_start = t_now
            drive_service = build('drive', 'v2', http=http)

        input_args = raw_input('command: ').strip()
        input_args = map(str.strip, input_args.split())

        if len(input_args) == 0:
            continue
        if input_args[0] == 'help':
            gdfuncs.show_commands()
        if input_args[0] == 'get_info':
            gdfuncs.show_files( gdfuncs.retrieve_all_files(drive_service) )
            t_start = time.time()

#        if input_args[0] == 'show_info_by_id':
#            if len(input_args) == 2:
#                gdfuncs.show_by_id(drive_service, input_args[1])
#                t_start = time.time()

        if input_args[0] == 'show_perms_by_id':
            if len(input_args) == 2:
                gdfuncs.show_perms_by_id(drive_service, input_args[1])
                t_start = time.time()
            else:
                print "Wrong argument: " + ' '.join(args)

        if input_args[0] == 'show_perms':
            if len(input_args) == 1:
                print "Wrong arguments:"
                print "example: perms <file_name>"
            else:
                filename = ' '.join(input_args[1:])
                gdfuncs.show_perms(drive_service, filename)
                t_start = time.time()
                
        if input_args[0] == 'give_perm_by_id':
            if len(input_args) == 5:
                gdfuncs.insert_permission(drive_service, 
                                          input_args[1], 
                                          input_args[2], 
                                          input_args[3], 
                                          input_args[4])
                t_start = time.time()
            else:
                print "Wrong argument: " + ' '.join(args)
                print "example: give_perm <file_id> <value> <type> <role>"
                print "value: email address of user or group. If the type is 'anyone', please write 'None'"
                print "type: one of 'user', 'group', or 'anyone'"
                print "role: one of 'owner', 'writer', or 'reader' "                


        if input_args[0] == 'give_perm':
            if len(input_args) == 5:
                filename = ' '.join(input_args[1:])
                gdfuncs.give_perm(drive_service, 
                                  input_args[1], 
                                  input_args[2], 
                                  input_args[3], 
                                  input_args[4])
                t_start = time.time()
            else:
                print "Wrong arguments:"
                print "example: give_perm <file_name> <value> <type> <role>"
                print "value: email address of user or group. If the type is 'anyone', please write 'None'"
                print "type: one of 'user', 'group', or 'anyone'"
                print "role: one of 'owner', 'writer', or 'reader' "                
        

        if input_args[0] == 'remove_perm_by_ids':
            if not len(input_args) == 3:
                print "Wrong arguments:"
                print "example: remove_perm_by_ids <file_id> <permission_id>"
            else:
                gdfuncs.remove_permission(drive_service, 
                                          input_args[1], 
                                          input_args[2])
                t_start = time.time()
                

        if input_args[0] == 'show_ids':
            if len(input_args) == 1:
                print "Wrong arguments:"
                print "example: show_ids <file_name>"
            else:
                filename = ' '.join(input_args[1:])
                gdfuncs.print_file_ids_for_filename(drive_service, filename)
                t_start = time.time()
               
#        if input_args[0] == 'reload':
#        if input_args[0] == 'reload':
        if input_args[0] == 'reload':
            reload(gdfuncs)
        if input_args[0] == 'exit':
            break

    return 


if __name__=="__main__":
    sys.exit(main(sys.argv))
