#!/usr/bin/env python

import httplib2
import pprint
import sys
import os
import re
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


        if input_args[0] == 'show_all':
            gdfuncs.show_all( gdfuncs.retrieve_all_files(drive_service) )
            t_start = time.time()

        

        if input_args[0] == 'show_perms_by_id':
            if len(input_args) == 2:
                gdfuncs.show_perms_by_id(drive_service, input_args[1])
                t_start = time.time()
            else:
                print "Wrong argument: " + ' '.join(args).strip()


        if input_args[0] == 'show_perms':
            if len(input_args) == 1:
                print "Wrong arguments:"
                print "example: perms \"<file_name>\""
            else:
                filename = ' '.join(input_args[1:]).strip().strip("\"").strip()
                gdfuncs.show_perms(drive_service, filename)
                t_start = time.time()

                
        if input_args[0] == 'give_perm_by_id':
            if len(input_args) == 5:
                gdfuncs.insert_permission(drive_service, 
                                          input_args[1].strip(), 
                                          input_args[2].strip(), 
                                          input_args[3].strip(), 
                                          input_args[4].strip())
                t_start = time.time()
            else:
                print "Wrong argument: " + ' '.join(args)
                print "example: give_perm_by_id <file_id> <email> <user|group> <owner|writer|reader>"

        if input_args[0] == 'give_perm_by_id_recursive':
            if len(input_args) == 5:
                gdfuncs.insert_permission(drive_service, 
                                          input_args[1].strip(), 
                                          input_args[2].strip(), 
                                          input_args[3].strip(), 
                                          input_args[4].strip())
                t_start = time.time()
            else:
                print "Wrong argument: " + ' '.join(args)
                print "example: give_perm_by_id_recursive <folder_id> <email> <user|group> <owner|writer|reader>"


        if input_args[0] == 'give_perm':
            if len(input_args) >= 5:
                filename = ' '.join(input_args[1:-3]).strip().strip("\"").strip()
                gdfuncs.give_perm(drive_service, 
                                  filename, 
                                  input_args[-3], 
                                  input_args[-2], 
                                  input_args[-1])
                t_start = time.time()
            else:
                print "Wrong arguments:"
                print "example: give_perm \"<file_name>\" <value> <type> <role>"
                print "value: email address of user or group. If the type is 'anyone', please write 'None'"
                print "type: one of 'user', 'group', or 'anyone'"
                print "role: one of 'owner', 'writer', or 'reader' "                


        if input_args[0] == 'show_files':
            if not len(input_args) == 1:
                print "Wrong arguments: No argument needed"
            else:
                gdfuncs.show_files(drive_service)
                t_start = time.time()

        
        if input_args[0] == 'show_folders':
            if not len(input_args) == 1:
                print "Wrong arguments: No argument needed"
            else:
                gdfuncs.show_folders(drive_service)
                t_start = time.time()


        if input_args[0] == 'remove_perm_by_perm_id':
            if not len(input_args) == 3:
                print "Wrong arguments:"
                print "example: remove_perm_by_id <file_id> <permission_id>"
            else:
                gdfuncs.remove_permission(drive_service, 
                                          input_args[1].strip(), 
                                          input_args[2].strip())
                t_start = time.time()

        
#        if input_args[0] == 'remove_perm':
#            args = ' '.join(input_args[1:])
#            names = re.findall(r'\"(.+?)\"',args)
#            if not len(names) == 2:
#                print "Wrong arguments:" + args
#                print "example: remove_perm \"<filename>\" \"<user_name>\""
#            else:
#                gdfuncs.remove_permission_beta(drive_service, 
#                                          names[0], 
#                                          names[1])
#                t_start = time.time()

        if input_args[0] == 'remove_perm_by_username':
            if  len(input_args) < 3:
                print "Wrong arguments:" + args
                print "example: remove_perm <file/folder_id> \"<user_name>\""
            else:
                file_id = input_args[1].strip().strip("\"").strip()
                user_name = ' '.join(input_args[2:]).strip().strip("\"").strip()
                print "1 user name: " + user_name
                print "args: " + str(input_args)
                gdfuncs.remove_permission_gamma(drive_service, 
                                          file_id, 
                                          user_name)
                t_start = time.time()

        if input_args[0] == 'remove_perm_by_username_recursive':
            if  len(input_args) < 3:
                print "Wrong arguments:"
                print "example: remove_perm_by_username_recursive <folder_id> <username>"
            else:
                folder_id = input_args[1].strip().strip("\"").strip()
                user_name = ' '.join(input_args[2:]).strip().strip("\"").strip()
                gdfuncs.remove_permission_recursive(drive_service, 
                                                    folder_id, 
                                                    user_name)
                t_start = time.time()
                
        
        if input_args[0] == 'show_ids':
            if len(input_args) == 1:
                print "Wrong arguments:"
                print "example: show_ids \"<file_name>\""
            else:
                filename = ' '.join(input_args[1:]).strip().strip("\"").strip()
                gdfuncs.print_file_ids_for_filename(drive_service, filename)
                t_start = time.time()
               
        if input_args[0] == 'ls_folder_by_id':
            if not len(input_args) == 2:
                print "Wrong arguments:"
                print "example: ls_folder_by_id <folder_id>"
            else:
                gdfuncs.print_files_in_folder(drive_service, input_args[1])
                t_start = time.time()

        if input_args[0] == 'ls_folder':
            if len(input_args) == 1:
                print "Wrong arguments:"
                print "example: ls_folder \"<folder_name>\""
            else:
                folder_name = ' '.join(input_args[1:]).strip().strip("\"").strip()
                gdfuncs.print_files_in_folder_by_name(drive_service, folder_name)
                t_start = time.time()

        if input_args[0] == 'ls_folder_by_id_recursive':
            if not len(input_args) == 2:
                print "Wrong arguments:"
                print "example: ls_folder_by_id_recursive <folder_id>"
            else:
                gdfuncs.print_all_childs_in_folder(drive_service, input_args[1])
                t_start = time.time()

        if input_args[0] == 'ls_folder_by_name_recursive':
            if  len(input_args) == 1:
                print "Wrong arguments:"
                print "example: ls_folder_by_name_recursive <folder_name>"
            else:
                folder_name = ' '.join(input_args[1:]).strip().strip("\"").strip()
                gdfuncs.print_files_in_folder_by_name_recursive(drive_service, folder_name)
                t_start = time.time()

        if input_args[0] == 'ls_all_children_ids':
            if not len(input_args) == 2:
                print "Wrong arguments:"
                print "example: ls_all_children_ids <folder_id>"
            else:
                childs = list()
                childs = gdfuncs.get_all_childs_in_folder(drive_service, input_args[1])
                for child in childs:
                    print child
                t_start = time.time()
                
        # Reload gdfuncs module
        if input_args[0] == 'reload':
            reload(gdfuncs)
        if input_args[0] == 'exit':
            break

    return 


if __name__=="__main__":
    sys.exit(main(sys.argv))
