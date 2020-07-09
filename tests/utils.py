# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                                       #
#   MapServer REST API is a python wrapper around MapServer which       #
#   allows to manipulate a mapfile in a RESTFul way. It has been        #
#   developped to match as close as possible the way the GeoServer      #
#   REST API acts.                                                      #
#                                                                       #
#   Copyright (C) 2011-2020 Neogeo Technologies.                        #
#                                                                       #
#   This file is part of MapServer Rest API.                            #
#                                                                       #
#   MapServer Rest API is free software: you can redistribute it        #
#   and/or modify it under the terms of the GNU General Public License  #
#   as published by the Free Software Foundation, either version 3 of   #
#   the License, or (at your option) any later version.                 #
#                                                                       #
#   MapServer Rest API is distributed in the hope that it will be       #
#   useful, but WITHOUT ANY WARRANTY; without even the implied warranty #
#   of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the     #
#   GNU General Public License for more details.                        #
#                                                                       #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


import httplib
import json
import pyxml
import sys


default_encoding = "json"


def deduce_content_type(type):
    if type == "json":
        return "application/json"
    elif type == "xml":
        return "application/xml"


def APIRequest(method, url, data=None, encode=default_encoding, decode=default_encoding, content_type=None, expected_type=None,
               get_response=False):

    if encode == "json":
        data = json.dumps(data)
    elif encode == "xml":
        data = pyxml.dumps(data)

    if content_type is None:
        content_type = deduce_content_type(encode)

    surl = httplib.urlsplit(url)

    if encode and not url.endswith("." + encode):
        url = surl.path + "." + encode
    else:
        url = surl.path

    if surl.query:
        url += "?" + surl.query

    print(sys.stderr, method, surl.geturl().replace(surl.path, url))
    conn = httplib.HTTPConnection(surl.hostname, surl.port)
    conn.request(method, url, body=data, headers={"Content-Type": content_type})

    r = conn.getresponse()

    if expected_type is None:
        expected_type = deduce_content_type(decode)

    # TODO: enable this test once it is suported.
    # assert expected_type in r.getheader("Content-Type"), "received %s instead of %s" % (
    #     r.getheader("Content-Type"), expected_type)

    recv = r.read()

    try:
        if decode == "json":
            recv = json.loads(recv)
        elif decode == "xml":
            recv = pyxml.loads(recv)
    except Exception:
        pass

    print(sys.stderr, r.status, r.reason)
    assert 200 <= r.status < 300, recv

    return (recv, r) if get_response else recv
