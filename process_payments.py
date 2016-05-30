# -*- coding: utf-8 -*-
from datetime import datetime
from time import sleep

import requests


__author__ = 'D.Ivanets'

while True:
    try:
        # host = 'http://localhost:8080'
        host = 'http://66.6.127.167'
        r = requests.get('{}/kiosk_api/process_payments/'.format(host))
        assert r.text == '{}'
        print datetime.utcnow(), 'OK'
    except:
        print datetime.utcnow(), 'FAIL'
    sleep(30)
