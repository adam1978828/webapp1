#!/usr/bin/env python
"""

"""

from django.conf import settings
import datetime
import tempfile
import requests

__author__ = "Oleg Tegelman"
__copyright__ = "Copyright 2015, KIT-XXI"
__credits__ = ["Oleg Tegelman"]

__license__ = ""
__version__ = "0.0.1"
__maintainer__ = "KIT-XXI"
__email__ = "support@kit-xxi.com.ua"
__status__ = "Production"


class JasperRestApi(object):
    REPORT_FORMATS = {
        'pdf': {'format': '.pdf', 'name': 'PDF'},
        'html': {'format': '.html', 'name': 'HTML'},
        'xls': {'format': '.xls', 'name': 'XLS'},
        'xlsx': {'format': '.xlsx', 'name': 'XLSX'},
        'rtf': {'format': '.rtf', 'name': 'RTF'},
        'csv': {'format': '.csv', 'name': 'CSV'},
        'xml': {'format': '.xml', 'name': 'XML'},
        'docx': {'format': '.docx', 'name': 'DOCX'},
        'odt': {'format': '.odt', 'name': 'ODT'},
        'ods': {'format': '.ods', 'name': 'ODS'},
        'jrprint': {'format': '.jrprint', 'name': 'JRPRINT'}
    }

    def __init__(self, **kwargs):
        self.j_username = kwargs.get('j_username', getattr(settings, 'JASPER_USERNAME', None))
        self.j_password = kwargs.get('j_password', getattr(settings, 'JASPER_PASSWORD', None))
        self.j_host = kwargs.get('j_host', getattr(settings, 'JASPER_HOST', 'http://localhost'))
        self.j_port = kwargs.get('j_port', getattr(settings, 'JASPER_PORT', '8082'))
        self.j_context_name = kwargs.get('j_context_name', getattr(settings, 'JASPER_CONTEXT_NAME', 'jasperserver'))

        self.use_enc_key = kwargs.get('use_enc_key', getattr(settings, 'JASPER_USE_ENC_KEY', False))
        self.get_enc_key_on_init = kwargs.get('get_enc_key_on_init', getattr(settings, 'JASPER_USE_ENC_KEY_ON_INIT', False))
        self.auth_cookies_exp = kwargs.get('auth_cookies_exp', getattr(settings, 'JASPER_AUTH_COOKIE_EXP', 86400))
        self.auto_login = kwargs.get('auto_login', getattr(settings, 'JASPER_AUTO_LOGIN', True))
        self.cache_report_params = kwargs.get('cache_report_params', getattr(settings, 'JASPER_CACHE_REPORT_PARAMS', True))
        self.cache_report_timeout = kwargs.get('cache_report_timeout', getattr(settings, 'JASPER_CACHE_REPORT_TIMEOUT', 14400))

        self.server_url = '{0}:{1}/{2}/'.format(self.j_host, self.j_port, self.j_context_name) if self.j_host and self.j_port else None
        self.enc_key = None
        self._auth_cookies = None
        self.auth_cookies_refresh_dt = None
        self.report_cache = dict()

        if self.get_enc_key_on_init:
            self.get_encryption_key()

        if self.auto_login:
            self.login()

    @property
    def auth_cookies(self):
        if self._auth_cookies and (datetime.datetime.now() - self.auth_cookies_refresh_dt).seconds > self.auth_cookies_exp:
            self._auth_cookies = None

        if not self._auth_cookies and self.auto_login:
            self.login()

        return self._auth_cookies

    def get_encryption_key(self):
        return NotImplemented()

    def login(self, request_type='POST'):
        login_url = self.server_url + 'rest/login{0}'.format('?' if request_type == 'GET' else '')
        params = {'j_username': self.j_username, 'j_password': self.j_password}

        if request_type == 'GET':
            req = requests.get(login_url, params=params)
        else:
            req = requests.post(login_url, data=params)

        self._auth_cookies = req.cookies
        self.auth_cookies_refresh_dt = datetime.datetime.now()

        return True

    def get_report_input_controls(self, report_path):
        if not self.auth_cookies:
            raise Exception('NOT AUTHENTICATED!')

        cached_params = self.get_report_params_from_cache(report_path)

        if cached_params[1]:
            controls_url = self.server_url + 'rest_v2/reports/{0}/inputControls'.format(report_path)
            req = requests.get(controls_url, cookies=self.auth_cookies, headers={'accept': 'application/json'})

            params = req.json() if req.text else None
            self.put_report_params_to_cache(report_path, params)
        else:
            params = cached_params[0]

        return params

    def put_report_params_to_cache(self, report_path, params):
        if self.cache_report_params:
            self.report_cache[report_path] = {'params': params, 'dt': datetime.datetime.now()}

    def get_report_params_from_cache(self, report_path):
        if not self.cache_report_params:
            return None, True
        if report_path in self.report_cache and (datetime.datetime.now() - self.report_cache[report_path]['dt']).seconds < self.cache_report_timeout:
            return self.report_cache[report_path]['params'], False
        else:
            return None, True

    def build_report(self, report_path, output_type='html', input_controls=None, save_to_file=False):
        if not self.auth_cookies:
            raise Exception('NOT AUTHENTICATED!')

        controls_url = self.server_url + 'rest_v2/reports/{0}{1}'.format(report_path, self.REPORT_FORMATS[output_type]['format'])
        req = requests.get(controls_url, params=input_controls, cookies=self.auth_cookies, headers={'accept': 'application/json'})

        if req.status_code == 200:
            if save_to_file:
                tmp_file = tempfile.TemporaryFile()
                for chunk in req.iter_content(chunk_size=1024):
                    if chunk:
                        tmp_file.write(chunk)
                tmp_file.flush()
                tmp_file.seek(0)
                content = tmp_file.read()
            else:
                content = req.text

            return content, req.headers._store['content-type'][1]
        else:
            return req.json()