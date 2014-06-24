# -*- coding: utf-8 -*-

import os
from distutils.core import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "pyee-topics",
    version = "0.0.12",
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
    long_description = read('README.rst')
)
