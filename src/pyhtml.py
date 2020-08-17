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


"""
    HTML interface of the REST API.

"""


import io
from cgi import escape
import pyxml
import urllib.parse
from xml.sax.saxutils import unescape


def should_be_url(s):
    """This is used to find out if it might be a good idea to
    consider a string is a URL.

    """
    parsed = urllib.parse.urlparse(s)
    return parsed.scheme and parsed.netloc


__dump_xml_max_element_id = 0


def dump_xml(xml, fp, indent=0, indent_depth=2, reinit=True):
    """Recursive function that transforms an ElementTree to html
    written to the file like stream fp.
    indent can be used to specify the amount of indentation wanted.

    """
    def new_id():
        """Gets a new unique element ID."""
        global __dump_xml_max_element_id
        __dump_xml_max_element_id += 1
        return __dump_xml_max_element_id

    def line(fmt, *args):
        """Writes a line to fp with corect indentation."""
        fp.write(('%s' + fmt + '\n') % tuple([indent * ' '] + list(args)))

    if reinit:
        # We need to reset element ID if we where nto called recursivly.
        global __dump_xml_max_element_id
        __dump_xml_max_element_id = 0

    if xml.text:
        if should_be_url(xml.text):
            line('<a href="%s">%s</a>', escape(unescape(xml.text), quote=True), escape(unescape(xml.text)))
        else:
            line('<pre>%s</pre>', escape(unescape(xml.text)))
    elif 'href' in xml.attrib:
        line('<a href="%s">%s</a>', escape(xml.attrib['href'], quote=True), escape(xml.attrib['href']))
    else:
        line('<table class="table table-condensed table-bordered table-hover table-striped" style="margin:0 0 0.2em 0">')
        indent += indent_depth

        for child in xml:
            id = new_id()
            line('<tr>')
            indent += indent_depth
            if 'href' in child.attrib:
                line('<td class="key" id="value_%d" onClick="toggle(\'entry_%d\')">href</td>', id, id)
            else:
                line('<td class="key" id="value_%d" onClick="toggle(\'entry_%d\')">%s%s</td>', id, id,
                     escape(child.tag), '' if not child.attrib else escape(" %s" % (child.attrib)))

            line('<td><div id="entry_%d">', id)
            dump_xml(child, fp, indent=indent + indent_depth, reinit=False)
            line('</div></td>')
            indent -= indent_depth
            line('</tr>')

        indent -= indent_depth
        line('</table>')


def dump(obj, fp, indent=0, *args, **kwargs):
    """Writes the html represention of obj to the file-like object fp.
    This uses pyxml to first transform the object into xml.
    *args and **kwargs are forwarded to pyxml.xml()

    """
    xml = pyxml.xml(obj, *args, **kwargs)
    dump_xml(xml, fp, indent)


def dumps(obj, *args, **kwargs):
    """Returns the html representation of obj as a string."""
    stream = io.StringIO()
    dump(obj, stream, *args, **kwargs)
    stream.flush()
    return stream.getvalue()
