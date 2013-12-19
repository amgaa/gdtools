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
def show_files(files):
    print "Title       Owner       id    "
    for f in files:
        show_file(f)

def show_file(f):
    print "{:30s}|{:16s}|{:36s}".format(f["title"][:30].encode('utf8'), \
                                              f["ownerNames"][0][:16].encode('utf8'),\
                                              f["id"] )

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


def show_help(args):
    print "Usage: {}"
    print "No argument is required yet"

def show_commands():
    print "get_info"
#    print "show_info_by_id <file_id>"
    print "show_perms_by_id <file_id>"
    print "show_perms <file_name>"
    print "give_perm_by_id <file_id> <email> <user|group|anyone> <owner|writer|reader>"
    print "give_perm <filename> <email> <user|group|anyone> <owner|writer|reader>"
    print "show_ids <filename>"
    print "help"
    print "exit"
