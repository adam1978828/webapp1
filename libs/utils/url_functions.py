__author__ = 'D.Kalpakchi'

from urlparse import urlparse, ParseResult


def construct_url(string):
    if isinstance(string, basestring):
        url = urlparse(string)
        url = url._replace(scheme=url.scheme or 'http')
        url = url._replace(netloc=url.netloc or url.path or None)
        url = url._replace(path='' if url.netloc == url.path else url.path)
        try:
            return url.geturl()
        except Exception, e:
            print e
            return ''
    else:
        return ''