# -*- coding: utf-8 -*-
import fnmatch
import re
import tarfile
from Crypto.PublicKey import RSA
__author__ = 'D.Ivanets'


tar = tarfile.open("FDGGWS_Certificate_WS1909530135._.1.tar.gz")
names = tar.getnames()
authfile = fnmatch.filter(names, '*.auth.txt')[0]
authtext = tar.extractfile(authfile).read()
username, password = re.search(
    r'.*Username: (WS.*\._\.1) Password: (.*)$', authtext).groups()
print username, password

key_p_file = fnmatch.filter(names, '*.key.pw.txt')[0]
key_pass = tar.extractfile(key_p_file).read()
print key_pass


# test for key file
key_file = fnmatch.filter(names, '*.key')[0]
new_key = RSA.importKey(
    tar.extractfile(key_file).read(), passphrase=key_pass).exportKey('PEM')

# pem file:
pem_file = tar.extractfile(fnmatch.filter(names, '*.pem')[0]).read()
tar.close()
