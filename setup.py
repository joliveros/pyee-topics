# -*- coding: utf-8 -*-

from distutils.core import setup

setup(
    name = "pyee-topics",
    version = "0.0.11",
    packages = ["pyee"],
    description = "A port of node.js's EventEmitter to python with mqtt topics support.",
    author = "Joseph Piron (Joshua Holbrook)",
    author_email = "joseph.piron@gmail.com (josh.holbrook@gmail.com)",
    url = "https://github.com/eagleamon/pyee-topics",
    keywords = ["events", "emitter", "node.js", "node", "eventemitter", "event_emitter", "mqtt", "patterns", "topics"],
    classifiers = [
        "Programming Language :: Python",
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7", #only one tested
        "Topic :: Other/Nonlisted Topic"
    ],
    long_description = """\
pyee
======

pyee supplies an event_emitter object that acts similar to the `EventEmitter`
that comes with node.js.

Example
-------

::

    In [1]: from pyee import EventEmitter

    In [2]: ee = EventEmitter()

    In [3]: @ee.on('a/#/c')
       ...: def event_handler():
       ...:     print 'BANG BANG'
       ...:

    In [4]: ee.emit('a/b/c')
    BANG BANG

    In [5]:

Easy-peasy.

There is the possibility to use mqtt topic patterns to match events

For more, visit <https://github.com/jesusabdullah/pyee> .

"""
)
