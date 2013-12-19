#!/usr/bin/env python

import httplib2
import pprint
import sys
import os
from apiclient import sample_tools
from apiclient import errors
from apiclient.discovery import build
from apiclient.http import MediaFileUpload
#from oauth2client import client
#from oauth2client.client import OAuth2WebServerFlow
#from oauth2client.client import flow_from_clientsecrets
#from oauth2client import client
#from oauth2client.file import Storage


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
def show_all(files):
    """ Prints out file/folder name, owner. and IDs    
    """
    print "Title       Owner       id    "
    for f in files:
        show_file(f)

def show_files(service):
    """ Prints out only files
    """
    try:
        files = retrieve_all_files(service)
        print "Title       Owner       id    "
        for f in files:
            if not f["mimeType"] == "application/vnd.google-apps.folder":
                show_file(f)
    except errors.HttpError, error:
        print 'An error occurred: %s' % error

def show_folders(service):
    """ Prints out only folders
    """
    try:
        files = retrieve_all_files(service)
        print "Title       Owner       id    "
        for f in files:
            if f["mimeType"] == "application/vnd.google-apps.folder":
                show_file(f)
    except errors.HttpError, error:
        print 'An error occurred: %s' % error


def show_file(f):
    if f["mimeType"] == "application/vnd.google-apps.folder":
        ftype = "Dir"
    else:
        ftype = "File"
    print "{:5s} | {:30s}|{:16s}|{:36s}".format(ftype,
                                                f["title"][:30].encode('utf8'),
                                                f["ownerNames"][0][:16].encode('utf8'),
                                                f["id"] )

def is_folder(f):
    """ Checks if a file is folder
    """
    if f["mimeType"] == "application/vnd.google-apps.folder":
        return True
    return False

def print_permission(service, file_id, permission_id):
    """Print information about the specified permission.

    Args:
    service: Drive API service instance.
    file_id: ID of the file to print permission for.
    permission_id: ID of the permission to print.
    """
    try:
        permission = service.permissions().get(
            fileId=file_id, permissionId=permission_id).execute()

        if permission.has_key("name"): print 'Name: %s' % permission['name']
        print 'Role: %s' % permission['role']
        print 'Type: %s' % permission['type']
        print 'Perm_id: %s' % str(permission)#['id']
        for additional_role in permission.get('additionalRole', []):
            print 'Additional role: %s' % additional_role
    except errors.HttpError, error:
        print 'An error occurred: %s' % error

def retrieve_permissions(service, file_id):
    """Retrieve a list of permissions.

    Args:
    service: Drive API service instance.
    file_id: ID of the file to retrieve permissions for.
    Returns:
    List of permissions.
    """
    try:
        permissions = service.permissions().list(fileId=file_id).execute()
        return permissions.get('items', [])
    except errors.HttpError, error:
        print 'An error occurred: %s' % error
    return None

def show_perms_by_id (service, file_id):
    """ Shows permissions of a file when file_id is given

    Args:
    service: Drive API service instance.
    file_id: ID of the file to retrieve permissions for.
    Returns:
    Prints each permissions
    """
    try:
        perm_ids = retrieve_permissions(service, file_id)
        for perm_id in perm_ids:
#            print "perm_id: " + str(perm_id)
            print_permission(service, file_id, perm_id["id"])
    except errors.HttpError, error:
        print 'An error occurred: %s' % error
    return None
        

def show_perms(service, filename):
    """ Shows permissions of a file when filename is given

    Args:
    service: Drive API service instance.
    filename: Title of the file to retrieve permissions for.
    Returns:
    Prints each permissions
    """
    print "filename: " + filename
    file_ids = list()
    try:
        file_ids = get_file_ids_for_filename(service, filename)
        if  len(file_ids) > 1:
            print "There are multiple files named: " + filename
            print "Cannot change permission. Please use unique filename."
            return
        if len(file_ids) == 0:
            print "We could not find file named: " + filename
            return 
        show_perms_by_id(service, file_ids[0])
    except errors.HttpError, error:
        print 'An error occured: %s' % error
    return None
        
def print_file_ids_for_filename(service, filename):
    """Prints the file IDs for an filename.
    Args:
    service: Drive API service instance.
    filename: Title of the file(s)
    """

    try:
        files = retrieve_all_files(service)
        name_list = list()
        for f in files:
            if f["title"] == filename:
                print "Id: " + f["id"]

    except errors.HttpError, error:
        print 'An error occured: %s' % error
    return None

def get_file_ids_for_filename(service, filename):
    """Returns the file IDs for an filename.
    
    Args:
    service: Drive API service instance.
    filename: Title of the file(s)
    Return:
    List of IDs of files named filename
    """

    try:
        files = retrieve_all_files(service)
        name_list = list()
        for f in files:
            if f["title"] == filename:
                name_list.append(f["id"])
        return name_list
    except errors.HttpError, error:
        print 'An error occured: %s' % error
    return None


def print_permission_id_for_email(service, email):
    """Prints the Permission ID for an email address.
    
    Args:
    service: Drive API service instance.
    email: Email address to retrieve ID for.
    """
    try:
        id_resp = service.permissions().getIdForEmail(email=email).execute()
        print id_resp['id']
    except errors.HttpError, error:
        print 'An error occured: %s' % error


def insert_permission(service, file_id, value, perm_type, role):
    """Insert a new permission.
    
    Args:
    service: Drive API service instance.
    file_id: ID of the file to insert permission for.
    value: User or group e-mail address, domain name or None for 'default'
    type.
    perm_type: The value 'user', 'group', 'domain' or 'default'.
    role: The value 'owner', 'writer' or 'reader'.
    Returns:
    The inserted permission if successful, None otherwise.
    """
    new_permission = {
        'value': value,
        'type': perm_type,
        'role': role
        }
    try:
        return service.permissions().insert(
            fileId=file_id, body=new_permission).execute()
    except errors.HttpError, error:
        print 'An error occurred: %s' % error
    return None

def remove_permission(service, file_id, permission_id):
    """Remove a permission.

    Args:
    service: Drive API service instance.
    file_id: ID of the file to remove the permission for.
    permission_id: ID of the permission to remove.
    """
    try:
        service.permissions().delete(
            fileId=file_id, permissionId=permission_id).execute()
    except errors.HttpError, error:
        print 'An error occurred: %s' % error
    
def remove_permission_beta(service, filename, user_name):
    """Remove a user's permission from a file with unique name.

    Args:
    service: Drive API service instance.
    filename: Name of the file to remove the permission for.
    User name: Name of the user to remove from permissions.
    """
    try:
        file_ids = list()
        perm_ids = list()
        
        # Look for file ID
        file_ids = get_file_ids_for_filename(service, filename)
        if  len(file_ids) > 1:
            print "There are multiple files named: " + filename
            print "Cannot change permission. Please use unique filename."
            return
        if len(file_ids) == 0:
            print "We could not find file named: " + filename
            print "Please check your filename"
            return

        # Look for permission ID
        permissions = service.permissions().list(fileId=file_ids[0]).execute()
        permissions = permissions.get('items', [])
        for perm in permissions:
            if perm.has_key("name"):
                if perm["name"] == user_name:
                    perm_ids.append(perm["id"])
        
        if len(perm_ids) > 1:
            print "There are mutiple users named: " + user_name
            print "Cannot change permission. Please use \" remove_perm_by_ids\" instead"
            return
        if len(perm_ids) == 0:
            print "There is no user named " + user_name + " has permission in this file."
            print "Please check your file and user name. "
            return
        return remove_permission(service, file_ids[0], perm_ids[0])
    except errors.HttpError, error:
        print 'An error occurred: %s' % error
    

def give_perm(service, filename, value, perm_type, role):
    """Insert a new permission.
    
    Args:
    service: Drive API service instance.
    filename: Title of the file to insert permission for.
    value: User or group e-mail address, domain name or None for 'default' type.
    perm_type: The value 'user', 'group', 'domain' or 'default'.
    role: The value 'owner', 'writer' or 'reader'.
    Returns:
    The inserted permission if successful, None otherwise.
    """
    try:
        file_ids = list()
        file_ids = get_file_ids_for_filename(service, filename)
        if  len(file_ids) > 1:
            print "There are multiple files named: " + filename
            print "Cannot change permission. Please use unique filename."
            return
        if len(file_ids) == 0:
            print "We could not find file named: " + filename
            print "Please check you filename"
            return
        return insert_permission(service, file_ids[0], value, perm_type, role)
    except errors.HttpError, error:
        print 'An error occured: %s' % error
    return None

#def give_folder_perm_by_id(service, folder_id, value, perm_type, role):
#def give_folder_perm(service, folder_name, value, perm_type, role):


def print_files_in_folder(service, folder_id):
    """Print files belonging to a folder.

    Args:
    service: Drive API service instance.
    folder_id: ID of the folder to print files from.
    """
    page_token = None
    while True:
        try:
            param = {}
            if page_token:
                param['pageToken'] = page_token
            children = service.children().list(
                folderId=folder_id, **param).execute()

            for child in children.get('items', []):
#                print 'File Id: %s' % child['id']
                show_file(service.files().get(fileId=child['id']).execute())

            page_token = children.get('nextPageToken')
            if not page_token:
                break
        except errors.HttpError, error:
            print 'An error occurred: %s' % error
            break

def print_files_in_folder_by_name(service, folder_name):
    """Print files belonging to a folder.

    Args:
    service: Drive API service instance.
    folder_name: name of the folder to print files from.
    """

    try:
        folder_ids = list()
        folder_ids = get_file_ids_for_filename(service, folder_name)
        if  len(folder_ids) > 1:
            print "There are multiple files and folders named: " + folder_name
            print "Cannot show lists. Please use unique folder name."
            return
        if len(folder_ids) == 0:
            print "We could not find folder named: " + folder_name
            print "Please check your folder name"
            return
    except errors.HttpError, error:
        print 'An error occurred: %s' % error
        
    page_token = None
    while True:
        try:
            param = {}
            if page_token:
                param['pageToken'] = page_token
            children = service.children().list(
                folderId=folder_ids[0], **param).execute()

            for child in children.get('items', []):
#                print 'File Id: %s' % child['id']
#                print str(child)
                show_file( service.files().get(fileId=child['id']).execute())

            page_token = children.get('nextPageToken')
            if not page_token:
                break

        except errors.HttpError, error:
            print 'An error occurred: %s' % error
            break




def print_file(service, file_id):
    """Print a file's metadata.

    Args:
    service: Drive API service instance.
    file_id: ID of the file to print metadata for.
    """
    try:
        file = service.files().get(fileId=file_id).execute()

        print 'Title: %s' % file['title']
        print 'MIME type: %s' % file['mimeType']
    except errors.HttpError, error:
        print 'An error occurred: %s' % error





def show_help(args):
    print "Usage: {}"
    print "No argument is required yet"

def show_commands():
    print "show_all"
    print "           : Lists all files and folders in your Google Drive"
    print "\n"

    print "show_files"
    print "           : Lists all files in your Google Drive"
    print "\n"

    print "show_folder"
    print "           : Lists all folders in your Google Drive"
    print "\n"

    print "ls_folder \"<folder name>\""
    print "           : Lists files and folders in your folder. Takes folder name as"
    print "           : argument. If two or more folder w/ same name exists, returns error"
    print "\n"

    print "ls_folder_by_id <folder ID>"
    print "           : Lists files and folders in folder of given ID"
    print "\n"

    print "show_ids \"<file/folder name>\""
    print "           : Shows the ID of given file/folder name. If mutiple file exists"
    print "           : returns multiple IDs"
    print "\n"

    print "show_perms \"<file/folder name>\""
    print "           : Shows permission status of file/folder. Takes file/folder name"
    print "           : If two or more file/folder w/ same name exists, returns error"
    print "\n"

    print "show_perms_by_id <file/folder ID>"
    print "           : Shows permission status of file/folder. Takes ID as argument."
    print "\n"

    print "give_perm \"<file/folder name>\" <email> <user|group|anyone> <owner|writer|reader>"
    print "           : Gives given user a permission to file/folder. Takes file/folder name as argument"
    print "\n"

    print "give_perm_by_id <file/folder ID> <email> <user|group|anyone> <owner|writer|reader>"
    print "           : Gives given user a permission to file/folder. Takes file/folder ID as argument."
    print "\n"

    print "remove_perm \"<file/folder name>\" \"<user name>\""
    print "           : Removes given user's permission from file. Takes file/folder name as argument."
    print "\n"

    print "remove_perm_by_id <file/folder ID> <permission ID>"
    print "           : Removes given user's permission from file. Takes file/folder ID and permission ID as argument."
    print "\n"

    print "help       : Shows help"
    print "\n"

    print "exit       : Exits from the program"
