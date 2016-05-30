# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import base64
import os
import re
from django.conf import settings

from django.contrib import auth
from django.http import HttpResponseForbidden

__author__ = 'Denis Ivanets (denself@gmail.com)'


def http_base_auth_credentials_from_request_headers(request):
    """Checks if there is a basic auth header presents in request
     parses it and return username, password from there.
     Otherwise it returns None, None
     :return: username, password
     :rtype: tuple
    """

    # If required header exists, get info
    if 'HTTP_AUTHORIZATION' in request.META:
        auth_header = request.META['HTTP_AUTHORIZATION'].split()
        if len(auth_header) == 2:
            auth_type, code = auth_header

            if auth_type.lower() == 'basic':

                # Decode base64 encoded 'username:password'
                decoded = base64.b64decode(code)

                # Split username and password by first colon
                username, password = decoded.split(':', 1)
                return username, password
    return None, None


def http_base_auth_from_request(request):
    """Using http base auth check if there is a user of required type and
    if there is it returns it.
    :return: user
    :rtype: User
    """

    # Get credentials from request header
    username, password = http_base_auth_credentials_from_request_headers(request)

    # Authenticate user
    if username and password:
        user = auth.authenticate(username=username,
                                 password=password,
                                 user_type=[2])
        return user


def http_auth_require(func):
    """Used as decorator, perform http base authorization and attaches user
    to request
     >>> @http_auth_require
     ... def func(request):
     ...     print(request.user)
     :return: Wrapped function
     :rtype: function
    """
    def wrapper(request, *args, **kwargs):

        # Gets user from request headers
        request.user = http_base_auth_from_request(request)

        # If there were credentials, and user authenticated, process view.
        if request.user:
            return func(request, *args, **kwargs)
        # Else return response 403
        else:
            return HttpResponseForbidden('AUTH_ERROR')

    return wrapper


def save_file(file_object, file_path):
    """
    Saves files from the request.FILES.
    :param file_object: request.FILES.get(file_name, None)
    :param file_path: Path, where file gonna be saved
    :type file_path:
    """

    # Check if parent directory of file exists, if not, creates it.
    if isinstance(file_object, (list, tuple)):
        save_file(file_object[0], file_path)
        print 'file_object must be an object of file, not list or tuple'
    parent_dirs = os.path.dirname(file_path)
    if not os.path.exists(parent_dirs):
        os.makedirs(parent_dirs)

    # Writes bite-object into file chunk by chunk
    with open(file_path, 'wb') as destination:
        for chunk in file_object.chunks():
            destination.write(chunk)


def get_kiosk_hostname(kiosk):
    """Simple helper, creates acceptable kiosk hostname based on kiosk
    parameters
    :type kiosk: Model.Kiosk
    :return: Kiosk hostname
    :rtype: unicode
    """

    # Lambda-function, helps check, if this char acceptable.
    _acceptable_char = r'[0-9A-Za-z\-_\.]'
    _is_acceptable = lambda s: re.match(_acceptable_char, s)

    # Make kiosk name unicode format. Use 'Kiosk' if None or ''.
    name = unicode(kiosk.settings.alias or 'Kiosk')

    # Replace all separators by '_'. Also, removes ' \n\t'.
    name = '_'.join(name.split())

    # Remove all unacceptable characters.
    name = ''.join([c for c in name if _is_acceptable(c)])

    # Use special format for kiosk hostname.
    hostname = 'K_{:03d}-{}'.format(int(kiosk.id), name)

    # Hostname can not be longer that 64, but we use 32 only.
    hostname = hostname[:30] + '_k'

    return hostname


def get_recent_package(test=False):
    """Looks over packages folder and searches for the most recent version of
    kiosk app package
    :param test: Is test package required
    :type test: bool
    :return: Path to package archive and application version.
    """
    prod_re = re.compile(r'package_(\d+)\.(\d+)\.(\d+)\.tar\.gz')
    test_re = re.compile(r'package_(\d+)\.(\d+)\.(\d+)(_test)?\.tar\.gz')

    match_re = test_re if test else prod_re

    packages = {}
    for file_name in os.listdir(settings.INSTALLER_DIR):
        m = match_re.match(file_name)
        if m:
            version = tuple(int(n) for n in m.groups()[:3])
            packages[version] = file_name

    if not packages:
        raise IOError

    version = sorted(packages, reverse=True)[0]
    archive_name = packages[version]
    path = os.path.join(settings.INSTALLER_DIR, archive_name)
    return path, version

def save_disk_photo(images):
    for im in images:
        try:
            dest = os.path.join(unicode(settings.DISK_PHOTO_DIR), unicode(im))
            save_file(im, dest)
        except Exception, e:
            print e

def save_screenshots(images):
    for path, im in images.iteritems():
        if im is None:
            continue
        try:
            dest = os.path.join(unicode(path), unicode(im))
            save_file(im, dest)
        except Exception, e:
            print e

def __old_save_img(data, img_path):
    """
    Save photo | for compatibility with old kiosk versions (<=0.0.46)
    :param data:
    :param img_path:
    :return:
    """
    image = base64.b64decode(data)
    f = open(img_path, 'wb')
    f.write(image)
    f.close()