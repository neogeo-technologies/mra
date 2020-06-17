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

import sys
from distutils.core import setup

setup(
    name='MapServer Rest API',
    version='1.0.2',
    author='Neogeo Technologies',
    author_email='contact@neogeo-online.net',
    description='A RESTFul interface for MapServer',
    long_description=open('README.md', 'r').read(),
    keywords='neogeo mapserver rest restful',
    license="GPLv3",
    #url='',
    classifiers=[
        'Development Status :: Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GPLv3',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python3',
        'Natural Language :: English',
        'Topic :: Scientific/Engineering :: GIS',
        ],
    #packages=,
    #package_dir={'':'src'},
    #namespace_packages=['mra'],
    install_requires=[
        'web.py>=0.50,<0.60',
        'pyyaml',
        'gdal<2.5.0',
        ],
    scripts=[
        'src/server.py',
        ]
    )
