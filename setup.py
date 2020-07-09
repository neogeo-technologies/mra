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


import os.path
from setuptools import setup


version = '1.1.0'


def parse_requirements(filename):
    with open(filename) as f:
        lines = (line.strip() for line in f)
        return [line for line in lines if line and not line.startswith('#')]


dirname = os.path.dirname(__file__)
reqs_filename = os.path.join(dirname, 'requirements.txt')

reqs = [str(req) for req in parse_requirements(reqs_filename)]


setup(
    name="MapServer Rest API",
    version=version,
    description="A RESTFul interface for MapServer",
    author="Neogeo Technologies",
    author_email="contact@neogeo.fr",
    license="GPLv3",
    url="https://github.com/neogeo-technologies/mra",
    classifiers=[
        "Operating System :: OS Independent",
        "Development Status :: Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GPLv3",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Scientific/Engineering :: GIS",
        ],
    install_requires=reqs,
    scripts=[
        os.path.join(dirname, 'src/server.py'),
        ]
    )
