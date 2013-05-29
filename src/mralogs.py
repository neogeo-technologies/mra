#!/usr/bin/env python
# -*- coding: utf-8 -*-
## mralogs.py for  in /home/wapiflapi
##
## Made by Wannes Rombouts
## Login   <wapiflapi@epitech.net>
##
## Started on  Thu May  2 15:46:05 2013 Wannes Rombouts
## Last update Mon May 27 11:22:40 2013 Wannes Rombouts
##

import string
import inspect
import logging
import functools

def setup(log_level, log_file=None, format="%(asctime)s %(levelname)7s: %(message)s"):
    log_level = getattr(logging, log_level.upper())
    logging.basicConfig(filename=log_file, format=format, level=log_level)

class Reccord(logging.Handler):
    """A logging.Handler class which stores the records.
    You'll probably want to iterate on this class to get the results.
    """

    def __init__(self, level=logging.DEBUG, logger=""):
        """Sets up a logging.Handler class which stores the records.
        level is the logging level and defaults to loggong.DEBUG, logger
        is by default the root loger.
        """

        logging.Handler.__init__(self)
        self.level = level
        self.records = []

        self.logger = logger
        # Add our self to the logger.
        logging.getLogger(self.logger).addHandler(self)

    def flush(self):
        pass

    def emit(self, record):
        self.records.append(record)

    def clear(self):
        """Clears the stored records."""
        self.records = []

    def __iter__(self):
        """Returns an iterator on the stored records."""
        return iter(self.records)

    def __del__(self):
        logger.removeHandler(logging.getLogger(self.logger))
        logging.Handler.__del__(self)

def short_str(obj, length=15, delta=5, tail="..."):
    """Returns a short version of str(obj) of length +/- delta.
    It tries to cut on characters from string.punctuation.
    If cut tail is appended. (defaults to '...')
    """
    s = str(obj)
    if len(s) < length:
        return s
    return s[:length+1-delta+min(s[length-delta:length+delta].find(c) for c in string.punctuation)] + tail


def logIn(level="debug", filter=(lambda *a, **kw:True)):
    """Decorator factory used to log when the function is called.
    The log level can be specified using level.
    filter can be used to specify a function that should be used to
    check if we want to log or not. It will be passed the same arguments
    as the decorated function.
    """
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            if filter(*args, **kwargs):
                arguments = inspect.getcallargs(getattr(f, "original_function", f), *args, **kwargs)
                getattr(logging, level, "error")("function '%s' was called with args: %s" %
                                                 (f.__name__, dict([(a, short_str(v)) for a, v
                                                                    in arguments.iteritems()])))
            return f(*args, **kwargs)
        wrapper.original_function = f
        return wrapper
    # If someone used @logIn instead of @logIn() we are nice to him:
    if callable(level):
        f, level = level, "debug"
        return decorator(f)
    return decorator

def logOut(level="debug", filter=(lambda *a, **kw:True)):
    """Decorator factory used to log when the function returns.
    The log level can be specified using level.
    filter can be used to specify a function that should be used to
    check if we want to log or not. It will be passed the same arguments
    as the decorated function, except for the fact the return value shall
    be inserted as first argument.
    """
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            ret = f(*args, **kwargs)
            if filter(ret, *args, **kwargs):
                getattr(logging, level, "error")("function '%s' returned: %s" % (f.__name__, short_str(ret)))
            return ret
        wrapper.original_function = f
        return wrapper
    # If someone used @logOut instead of @logIn() we are nice to him:
    if callable(level):
        f, level = level, "debug"
        return decorator(f)
    return decorator

def logBoth(level="debug"):
    """Helper decorator, same as applying both @logIn and @logOut"""
    def decorator(f):
        return logOut(level)(logIn(level)(f))
    # If someone used @logBoth instead of @logBoth() we are nice to him:
    if callable(level):
        f, level = level, "debug"
        return decorator(f)
    return decorator
