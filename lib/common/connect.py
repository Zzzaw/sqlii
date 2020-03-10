import chardet
import urllib.request

from lib.data.settings import *
from lib.common.exception import *
from lib.common import logger


def getPage(**kwargs):

    url = kwargs.get('url', None)
    get = kwargs.get("get", None)
    post = kwargs.get("post", None)
    method = kwargs.get("method", None)
    headers = kwargs.get("headers", None)

    if "://" not in url:
        url = "http://%s" % url
    if get:
        if '?' in url:
            url = "%s%s%s" % (url, '&', get)
        else:
            url = "%s?%s" % (url, get)
    headers = headers if headers else {'USER-AGENT': USER_AGENT}

    try:
        request = urllib.request.Request(url=url, method=method, data=post, headers=headers)
        response = urllib.request.urlopen(request)
    except urllib.error.HTTPError as ex:
        raise ConnectionException(ex.msg)

    page = response.read()
    res_headers = response.getheaders()
    code = response.code

    #decode page
    encoding = chardet.detect(page)['encoding']

    if encoding:
        try:
            page = page.decode(encoding)
        except (UnicodeDecodeError, LookupError):
            raise DecodeError('Could not decode page using ' + encoding)
    else:
        page = page.decode('utf-8')

    if code != 200:
        errMsg = 'respon code: ' + str(code)
        raise ConnectionException(errMsg)

    return page, res_headers, code

