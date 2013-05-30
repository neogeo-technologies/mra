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

import web

import json
import pyxml
import pyhtml

import inspect
import functools

import os.path
import itertools

import mralogs


class KeyExists(KeyError):
    pass

# web.py doesn't allow to set a custom message for all errors, as it does
# for NotFound, we attempt to fix that here, but only handle those we use...

def Created(location):
    web.ctx.status = "201 Created"
    web.header("Location", location)


class BadRequest(web.webapi.HTTPError):
    """`400 Bad Request` error."""
    def __init__(self, message="bad request"):
        self.message = message
        status = '404 Bad Request'
        headers = {'Content-Type': 'text/html'}
        web.webapi.HTTPError.__init__(self, status, headers, message)

class NotFound(web.webapi.HTTPError):
    """`404 Not Found` error."""
    def __init__(self, message="not found"):
        self.message = message
        status = '404 Not Found'
        headers = {'Content-Type': 'text/html'}
        web.webapi.HTTPError.__init__(self, status, headers, message)

class Unauthorized(web.webapi.HTTPError):
    """`401 Unauthorized` error."""
    def __init__(self, message="unauthorized"):
        self.message = message
        status = "401 Unauthorized"
        headers = {'Content-Type': 'text/html'}
        web.webapi.HTTPError.__init__(self, status, headers, message)


class Forbidden(web.webapi.HTTPError):
    """`403 Forbidden` error."""
    def __init__(self, message="forbidden"):
        self.message = message
        status = "403 Forbidden"
        headers = {'Content-Type': 'text/html'}
        web.webapi.HTTPError.__init__(self, status, headers, message)


class Conflict(web.webapi.HTTPError):
    """`409 Conflict` error."""
    def __init__(self, message="conflict"):
        self.message = message
        status = "409 Conflict"
        headers = {'Content-Type': 'text/html'}
        web.webapi.HTTPError.__init__(self, status, headers, message)


class NotAcceptable(web.webapi.HTTPError):
    """`406 Not Acceptable` error."""
    def __init__(self, message="not acceptable"):
        self.message = message
        status = "406 Not Acceptable"
        headers = {'Content-Type': 'text/html'}
        web.webapi.HTTPError.__init__(self, status, headers, message)

class NotImplemented(web.webapi.HTTPError):
    """`501 Not Implemented` error."""
    def __init__(self, message="not implemented"):
        self.message = message
        status = "501 Not Implemented"
        headers = {'Content-Type': 'text/html'}
        web.webapi.HTTPError.__init__(self, status, headers, message)


# The folowing helpers are for managing exceptions and transforming them into http errors:

class exceptionManager(object):
    def __init__(self, exceptions):
        self.exceptions = exceptions

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type in self.exceptions:
            return not self.handle(exc_type, exc_value, traceback)


class exceptionsToHTTPError(exceptionManager):
    def __init__(self, message=None, exceptions=None, **kwargs):
        if message != None:
            self.message = message
        self.msg_args = kwargs
        exceptionManager.__init__(self, exceptions or self.exceptions)

    def handle(self, exc_type, exc_value, traceback):
        msg = self.message.format(exception=exc_value.message, **self.msg_args)
        raise self.HTTPError(message=msg)

class nargString(list):
    """
    This object only implements format, which it redirects to one
    of the strings given to its __init__ according to how many
    arguments are given to format.
    """

    def __init__(self, *args):
        list.__init__(self, args)

    def format(self, *args, **kwargs):
        if len(args) + len(kwargs) >= len(self):
            raise TypeError("To many arguments for string formatting.")
        return self[len(args) + len(kwargs)].format(*args, **kwargs)


class mightFailLookup(exceptionsToHTTPError):
    def __init__(self, name=None, message=None, exceptions=None, **kwargs):
        if len(kwargs) == 1:
            kwargs["container_type"], kwargs["container"] = kwargs.popitem()
        if name:
            kwargs["name"] = name
        exceptionsToHTTPError.__init__(self, message, exceptions, **kwargs)


class mightNotFound(mightFailLookup):
    exceptions = (KeyError, IndexError)
    HTTPError = NotFound
    message = nargString("Oops. We don't know what wasn't found...",
                         "'{exception}' not found.",
                         "'{exception}' not found in '{container}'.",
                         "'{exception}' not found in {container_type} {container}.",
                         "{name} '{exception!s}' not found in {container_type} '{container}'.")

class mightConflict(mightFailLookup):
    exceptions = (KeyExists,)
    HTTPError = Conflict
    message = nargString("Oops. We don't know what wasn't found...",
                         "'{exception}' already exists.",
                         "'{exception}' already exists in '{container}'.",
                         "'{exception}' already exists in {container_type} {container}.",
                         "{name} '{exception}' already exists in {container_type} '{container}'.")

class URLMap(object):
    """Helper class to build url maps for web.py.

    urlmap = URLMap()

    There are two ways of defining a mapping:
        >>> urlmap.XXX( *args)
        >>> urlmap(XXX, *args)

    If you call urlmap with something else than a basestring as first
    argument then the value of XXX.__name__ is used.

    *args defines the path to be used. See help(URLMap.__call__) for
    further information.
    """

    def __init__(self, var="/([^/]+)", endvar="/((?:[^.^/]+\.?(?=.*\..*[^/]$))*[^.^/]+)"):
        """Instanciates a URLMap object.
        The argument var is used instead of () when it is passed to the
        mapper. It should be a regex defining the default 'variable' component.
        """
        self.map = []
        self.var = var
        self.endvar = endvar

    def __call__(self, page, *args, **kwargs):
        """Stores a new mapping from the constructed path to page.
        The path is constructed by joining all the *args after handling them
        as follow. If a component is () then it is replaced by the default
        for a variable component as defined by URLMap's __init__. If it is
        a list then a regex is generated to allow for any of the values in the
        list. Else the value is used. The final values of the components are
        always separated by a "/" in the final path.
        """
        components = []
        for i, arg in enumerate(args):
            if arg == () and i == len(args) - 1:
                # Special case if last component is a variable.
                components.append(self.endvar)
            elif arg == ():
                components.append(self.var)
            elif isinstance(arg, list):
                components.append("/(?:%s)" % "|".join(arg))
            else:
                components.append("/%s" % arg)


        format = kwargs.get("format", True)
        if format:
            components.append(format if isinstance(format, basestring) else "(?:(\.[^/^.]+)?|/$)$")

        url = "".join(components) + "$"
        self.map.extend((url, page if isinstance(page, basestring) else page.__name__))

    def __getattr__(self, name):
        """Maps all attributes to a wrapper function calling self(name, *args, **kwargs),
        see help(URLMap.__call__).
        """
        def wrapper(*args, **kwargs):
            return self(name, *args, **kwargs)
        return wrapper

    def __iter__(self):
        """Returns an iterator to the lists of maps defined so far.
        Also cleans that list because it should only be called once
        anyway, if you don't want it to be cleared you can simply
        use iter(self.map).
        """
        map = self.map
        self.map = []
        return iter(map)

# Available for use if you don't want your own instance.
urlmap = URLMap()

def default_renderer(format, authorized, content, name_hint):
    if format == "xml":
        return pyxml.dumps(content, obj_name=name_hint)
    elif format == "sld":
        return str(content)
    elif format == "html":
        url = web.ctx.path + web.ctx.query
        if url.endswith(".html"):
            url = url[:-5]
        urls = [(x, "%s.%s" % (url, x)) for x in authorized if x != 'html']
        templates = os.path.join(os.path.dirname(__file__), 'templates/')
        render = web.template.render(templates)
        return render.response(web.ctx.home, web.ctx.path.split("/"), urls, pyhtml.dumps(content, obj_name=name_hint, indent=4))
    elif format == "json":
        return json.dumps(content)
    else:
        return str(content)


class HTTPCompatible(object):
    """Decorator factory used to transform the output of a backend function
    to be suited for the web.

    Renders the ouput according to a renderer function.
    Sets correct Content-Type according to the format.
    Maps exceptions to coresponding HTTP error codes.
    """

    return_logs = False

    known_mimes = {
        "xml"  : "application/xml",
        "sld"  : "application/vnd.ogc.sld+xml",
        "html" : "text/html",
        "json" : "application/json",
        }

    def __init__(self, authorize=set(), forbid=set(), authorized=set(["xml", "json", "html"]),
                 default="html", renderer=default_renderer, render=None,
                 parse_format=True, trim_nones=True,
                 name_hint="MapServerRESTAPI_Response"):
        """Decorator factory used to transform the output of a backend function
        to be suited for the web. see help(HTTPCompatible) for more information.

        authorize and forbid are filters that allow for easy modification of
        authorized, which is used to check if the request format is OK.

        default indicates which format should be used if not specified by the client.
        renderer is the function called for formating. render can be set to True or
        False to prevent HTTPCompatible from guessing if we want output or not
        based on the name of the decorated function. (By default only GETs will
        have rendered output.)

        parse_format (defaults to True) tells HTTPCompatible if it should parse the format
        or put it back with the normal arguments.

        name_hint is used if the output format requires the outer-most level to have a name.
        """

        self.default = default
        self.renderer = renderer

        self.name_hint=name_hint
        self.parse_format = parse_format

        if not isinstance(authorize, set):
            authorize = set(authorize)
        if not isinstance(forbid, set):
            forbid = set(forbid)
        if not isinstance(authorized, set):
            authorized = set(authorized)

        # Computes authorized formats, makes sure default is one of them.
        self.authorized = authorize | (authorized - forbid)

        # Should we trim trailing Nones ?
        self.trim_nones = trim_nones

        self.render = render

    def __call__(self, f):
        """Returns a wrapper around f in order to make its return value suitable
        for the web.
        """

        if self.render == None:
            # We must guess if we want to render or not.
            self.render = f.__name__ in ["GET"]

        @functools.wraps(f)
        def wrapper(*args, **kwargs):

            args = list(args)

            # If the last argument is a string starting with "." we use it as format
            # Else we use the default value, and remove None if it was specified.
            if args and isinstance(args[-1], basestring) and args[-1].startswith("."):
                page_format = args.pop()[1:]
                if not self.parse_format and args:
                    # Recover from regex that splited the format off anyway.
                    # TODO: only if the full url ends with args[-1].format
                    args[-1] = "%s.%s" % (args[-1], page_format)
                    page_format = self.default
            else:
                page_format = self.default
                # Remove None if it was forcing default.
                if args and args[-1] == None:
                    del args[-1]

            # TODO: look at web.ctx.env.get("Accept") and take it into account.
            # Send a NotAcceptable error if we can't agree with the client.

            # Trim trailing Nones.
            if self.trim_nones:
                while args and args[-1] == None:
                    del args[-1]

            # Check format against authorized.
            if page_format not in self.authorized:
                raise NotFound()

            # Insert the format in the argument list where it is expected by f.
            # Also we don"t want to pass format to a function which doesn"t expect it,
            specs = inspect.getargspec(f)
            if "format" in specs.args:
                fmtidx = specs.args.index("format")
                if fmtidx < len(args):
                    args.insert(fmtidx, page_format)
                else:
                    kwargs["format"] = page_format

            # Start recording the logs if needed.
            # Only do this in case we are in a format that allows this.
            add_debug = self.return_logs and page_format in ["xml", "json", "html"] and web.config.debug
            if add_debug:
                reccord = mralogs.Reccord()
                content = {}

            # We generaly do not care about un-handled exceptions because
            # web.py will handle them according to web.config.debug
            try:
                content = f(*args, **kwargs)
            except BaseException as e:
                raise

            # We want to make sure we don't end up doing str(None)
            if content == None:
                content = ""

            name_hint = self.name_hint
            # Lets add the logs to the content.
            if add_debug:
                msgs = [{"asctime":msg.asctime,
                         "filename":msg.filename,
                         "funcName":msg.funcName,
                         "lineno":msg.lineno,
                         "levelname":msg.levelname,
                         "message":msg.message,
                         } for msg in reccord]
                name_hint = "debug_data"
                content = {self.name_hint:content, "_logs":msgs}

            if self.render and self.renderer:
                result = self.renderer(page_format, self.authorized, content, name_hint)
            else:
                result = content

            # Deduce content type from format.
            web.header("Content-Type", self.known_mimes.get(page_format, "text/plain"))
            return result

        self.original_function = f
        return wrapper


def get_data(name=None, mandatory=[], forbidden=[]):
    data = web.data()

    if not 'CONTENT_TYPE' in web.ctx.env:
        raise web.badrequest('You must specify a Content-Type.')

    ctype = web.ctx.env.get('CONTENT_TYPE')

    try:
        if 'text/xml' in ctype or  'application/xml' in ctype:
            data, dname = pyxml.loads(data, retname=True)
            if name and dname != name: data = None
        elif 'application/json' in ctype:
            data = json.loads(data)
            if name: data = data.get(name, None)
        else:
            raise web.badrequest('Content-type \'%s\' is not allowed.' % ctype)
    except ValueError:
        raise web.badrequest('Could not decode input data.' % mandatory)

    if name and data == None:
        raise web.badrequest('The object you are sending does not contain a \'%s\' entry.' % name)

    if not all(x in data for x in mandatory):
        raise web.badrequest('The following elements are missing, %s' % [x for x in mandatory if x not in data])
    if any(x in data for x in forbidden):
        raise web.badrequest('You are not allowed to send any of %s' % [x for x in forbidden if x in data])

    return data
