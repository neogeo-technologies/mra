#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                                       #
#   MapServer REST API is a python wrapper around MapServer which       #
#   allows to manipulate a mapfile in a RESTFul way. It has been        #
#   developped to match as close as possible the way the GeoServer      #
#   REST API acts.                                                      #
#                                                                       #
#   Copyright (C) 2011-2013 Neogeo Technologies.                        #
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

import xml.etree.ElementTree as etree
from xml.etree.ElementTree import Element
from xml.sax.saxutils import escape

# Here we have the Entries, it wraps either a list or a dict.
# Its not trivial because we want to inherit from a list or
# from a dict, but we want both instances to inherit from Entries.
# Also we want the factory to be Entries and not a function.
class Entries(object):
    def __new__(clazz, obj, *args, **kwargs):
        class _Entries(Entries, type(obj)):
            def __init__(self, *args, **kwargs):
                # Try to be as transparent as possible.
                self.tag_name = kwargs.pop("tag_name", None)
                self.key_name = kwargs.pop("key_name", "key")
                type(obj).__init__(self, *args, **kwargs)

            # Now define get_hints, the ifs are not in it because we want
            # the exception to be raised at instanciation.
            if isinstance(obj, list):
                def get_hints(self):
                    return (xml_list, self.tag_name) if self.tag_name else (xml_list, ())
            elif isinstance(obj, dict):
                def get_hints(self):
                    return (xml_dict, (self.tag_name, self.key_name)) if self.tag_name else (xml_dict, ())
            else:
                raise TypeError("Entries must be given a list or a dict as first argument.")

        # We need to call __new__ on the parent of our _Entries
        return type(obj).__new__(_Entries, *args, **kwargs)


def href(link, element=None):
    """Builds an atom:link object for the link."""

    if element == None:
        element = Element("atom:link")

    element.tag = "atom:link"
    element.attrib = {
            "xmlns:atom":"http://www.w3.org/2005/Atom",
            "rel":"alternate",
            "href":link,
            "type":"application/xml",
            }

    return element

def singular(name):
    """Tries to return name in its singular form if possible else it just returns name."""
    if name.endswith("ies"):
        return name[:-3] + "y"
    elif name.endswith("s"):
        return name[:-1]
    return name

def default_xml_dict_mapper(obj_name, key_name="key"):
    """Maps to xml_dict and tries to deduce the entry naming from obj_name.
    If obj_name is plural then entries's tag will the singular and a key_name
    attribute will hold the key, otherwises the tag will be the key.
    """
    singular_name = singular(obj_name)
    if singular_name != obj_name:
        return xml_dict, [singular_name, key_name]
    else:
        return xml_dict, None

def default_xml_list_mapper(obj_name, entry_name="entry"):
    """Always maps to xml_list but tries to name its entries after the
    singular of obj_name if possible. If not they are named after entry_name.
    """
    singular_name = singular(obj_name)
    if singular_name != obj_name:
        return xml_list, singular_name
    else:
        return xml_list, entry_name

def default_xml_mapper(obj, obj_name,
                       dict_mapper=default_xml_dict_mapper,
                       list_mapper=default_xml_list_mapper):
    """Returns a function to transform the object into xml.

    If obj is an instance of the pyxml helper class 'entries' it is
    handled according to what is described in help(entries).

    In some cases the mapping is left to another function, as follows:
    type(obj) in [dict] -> dict_mapper
    type(obj) in [list, tuple] -> list_mapper

    Otherwise the name is checked for known special cases such as "href",
    and otherwise it is assumed to be a string.
    """
    if obj == None:
        return None, None
    elif isinstance(obj, Entries):
        return obj.get_hints()
    elif obj_name == "href":
        return xml_href, None
    elif isinstance(obj, dict):
        return dict_mapper(obj_name)
    elif isinstance(obj, list) or isinstance(obj, tuple):
        return list_mapper(obj_name)
    elif any(isinstance(obj, t) for t in (basestring, int, float)):
        # Those we are sure we want to map as strings.
        return xml_string, None
    elif hasattr(obj, "__str__"):
        # Those we render as strings, but we are not sure.
        # Just add the type to the case above it is justified!
        print "xml_mapper: Warning: We are trying to map %s as a string." % (type(obj))
        return xml_string, None
    else:
        raise NotImplementedError("Can't map %s object." % type(obj))

def xml(obj, obj_name=None, parent=None,
        xml_mapper=default_xml_mapper,
        dict_mapper=default_xml_dict_mapper,
        list_mapper=default_xml_list_mapper):
    """Returns an xml element representing the obj or if parent is not None
    appends the element that would normaly be returned to the parent and
    returns the parent. If a new element is returned it's tag is set to
    obj_name. The mapping is done according to the xxx_mappers.
    """

    # Findout the object's name.
    if obj_name == None:
        obj_name = parent.tag if parent != None else "object"

    # Create the parent if it's not provided.
    if parent == None:
        parent = etree.Element(tag=obj_name)

    mapper, hint = xml_mapper(obj, obj_name, dict_mapper, list_mapper)
    if not mapper:
        return None

    mapper(parent, obj, hint, xml_mapper, dict_mapper, list_mapper)

    return parent

def xml_href(parent, obj, hint=None, xml_mapper=default_xml_mapper,
             dict_mapper=default_xml_dict_mapper, list_mapper=default_xml_list_mapper):
    """Adds obj to parent as if it is a href."""
    href(str(obj), parent)

def xml_string(parent, obj, _=None, xml_mapper=default_xml_mapper,
             dict_mapper=default_xml_dict_mapper, list_mapper=default_xml_list_mapper):
    """Adds obj to parent as if it is a string."""
    parent.text = escape(str(obj))

def xml_dict(parent, obj, hint=None, xml_mapper=default_xml_mapper,
             dict_mapper=default_xml_dict_mapper, list_mapper=default_xml_list_mapper):
    """Adds obj to parent as if it is a dictionary.
    The entries are of the form: <key>value</key> or <hint[0] hint[1]=key>value</hint[0]>
    """
    for k, v in obj.iteritems():
        if hint:
            child = etree.Element(tag=hint[0], attrib={hint[1]:k})
        else:
            child = etree.Element(tag=k, attrib={})
        xml(v, parent=child, xml_mapper=xml_mapper, dict_mapper=dict_mapper, list_mapper=list_mapper)
        parent.append(child)

def xml_list(parent, obj, hint, xml_mapper=default_xml_mapper,
             dict_mapper=default_xml_dict_mapper, list_mapper=default_xml_list_mapper):
    """Adds obj to parent as if it is a list.
    The entries are of the form: <hint>value</hint>
    """
    for v in obj:
        child = etree.Element(tag=hint, attrib={})
        xml(v, parent=child, xml_mapper=xml_mapper, dict_mapper=dict_mapper, list_mapper=list_mapper)
        parent.append(child)

def dump(obj, fp, encoding=None, *args, **kwargs):
    """Writes the xml represention of obj to the file-like object fp."""
    fp.write(etree.tostring(xml(obj, *args, **kwargs), encoding))

def dumps(obj, encoding=None, *args, **kwargs):
    """Returns the xml representation of obj as a string."""
    return etree.tostring(xml(obj, *args, **kwargs), encoding)

def obj(xml):
    """Returns the object represented by the xml.
    Basicaly this is done recursivly in four checks:
    If an object has no children its text is considered to be a string.
    If all childs of an object have the same tag and have exactly one attribute
    in common then that object is considered to represent a dictionary mapping that
    attribute's value to the contents.
    Otherwise if all the tags of the children are unique then it is also considered
    a dictionary but mapping the tags and the conntents.
    If none of the above the object is considered to be a list.
    """

    children = xml.getchildren()

    if xml.text and not children:
        return xml.text.strip()

    tags = set(c.tag for c in children)

    # TODO: check this and make it better.
    if singular(xml.tag) != xml.tag and len(tags) == 1 and xml.tag.startswith(next(iter(tags))):
        common_keys = set.intersection(*(set(c.attrib) for c in children)) if children else []
        if not common_keys:
            return list(obj(c) for c in children)

    if len(tags) == 1:
        common_keys = set.intersection(*(set(c.attrib) for c in children)) if children else []
        if len(common_keys) == 1:
            return dict((c.attrib[next(iter(common_keys))], obj(c)) for c in children)

    if len(tags) == len(children):
        return dict((c.tag, obj(c)) for c in children)
    else:
        return list(obj(c) for c in children)


def loads(s, retname=False, *args, **kwargs):
    """Returns an object coresponding to what is described in the xml."""
    try:
        xml = etree.fromstring(s)
    # Python 2.6 has no xml.etree.ElementTree.ParseError.
    except BaseException:
        raise ValueError("No XML object could be decoded.")
    o = obj(xml, *args, **kwargs)
    return (o, xml.tag) if retname else o

def load(fp, retname=False, *args, **kwargs):
    """Returns an object coresponding to what is described in the xml
    read from the file-like object fp.
    """
    try:
        xml = etree.parse(fp)
    # Python 2.6 has no xml.etree.ElementTree.ParseError.
    except BaseException:
        raise ValueError("No XML object could be decoded.")
    o = obj(xml, *args, **kwargs)
    return (o, xml.tag) if retname else o

