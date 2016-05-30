# -*- coding: utf-8 -*-
import fnmatch
import os
import re
import tarfile
import uuid
from Crypto.PublicKey import RSA
from django.conf import settings

__author__ = 'D.Ivanets'


def save_file(path, data):
    """
    Can save any file from request.FILES to the path
    :param path: String, path to file with name
    :param data: request.FILES object
    """
    fd = open(path, u'wb')
    for chunk in data.chunks():
        fd.write(chunk)
    fd.close()


def process_archive(data):
    """
    This function accepts file data object, temporary saves it as an archive,
        get username, password, .pem and .key files,
        decrypt key file using pass phrase
        and saves it in settings.LINKPOINT_KEYS_DIR directory
    :param data: Binary data object with archive content
    :return:
    """
    # Checking, if the archive has a correct format amd saving it into the settings.TEMP_DIR dir.
    assert fnmatch.fnmatch(data.name, u'*.tar.gz'), u'Archive should be in *.tar.gz format.'

    # Creating temp archive file to use it tarfile.open()
    temp_archive_path = os.path.join(settings.TEMP_DIR, data.name)
    save_file(temp_archive_path, data)
    pay_id = uuid.uuid1().hex
    path = os.path.join(settings.LINKPOINT_KEYS_DIR, pay_id)
    os.makedirs(path)

    # Opening archive for reading.
    tar = tarfile.open(temp_archive_path)
    names = tar.getnames()
    try:
        assert fnmatch.filter(names, u'*.auth.txt'), u'No *.auth.txt file in archive'
        assert fnmatch.filter(names, u'*.key.pw.txt'), u'No *.key.pw.txt file in archive'
        assert fnmatch.filter(names, u'*.key'), u'No *.key file in archive'
        assert fnmatch.filter(names, u'*.pem'), u'No *.pem file in archive'

        # Reading username and password
        file_with_credentials = fnmatch.filter(names, u'*.auth.txt')[0]
        username, password = re.search(ur'.*Username: (WS.*\._\.1) Password: (.*)$',
                                       tar.extractfile(file_with_credentials).read()).groups()
        assert username and password, u'*.auth.txt file should follow does not contain username or password strings'

        # decrypting and saving key file
        key_pass = tar.extractfile(fnmatch.filter(names, u'*.key.pw.txt')[0]).read()
        assert key_pass, u'*.key.pw.txt file should not be empty'
        new_key = RSA.importKey(tar.extractfile(fnmatch.filter(names, u'*.key')[0]).read(),
                                passphrase=key_pass).exportKey(u'PEM')
        f = open(os.path.join(path, u'%s.key' % username), u'w')
        f.write(new_key)
        f.close()

        # saving pem file
        pem_file = tar.extractfile(fnmatch.filter(names, u'*.pem')[0]).read()
        f = open(os.path.join(path, u'%s.pem' % username), u'w')
        f.write(pem_file)
        f.close()
    finally:
        tar.close()
        os.remove(temp_archive_path)

    return pay_id, username, password
