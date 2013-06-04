=================================
How to install MapServer Rest API
=================================

This document describes how to install and configure **MapServer Rest API**.

Prerequisites
=============

**MapServer Rest API** needs the following components:

* 	Python with following packages:

	*	web.py

	*	pyyaml

	*	nosetests (Not mandatory but required to run tests)

*	GDAL/OGR (>= 1.9.x with Python support)

*	MapServer (>= 6.x with MapScript-Python support)


Download
========
Get the newest source code by downloading the archive at `download`_ page.
Then extract the archive in a directory of your choice. Or checkout the Git in some place.

.. _download: https://github.com/neogeo-technologies/mra

Installation
============
There is nothing to do more.
Just create a virtual directory and the following aliases: ::

	WSGIPythonPath /path/to/mra/src/mra
	WSGIScriptAlias /mra /path/to/mra/src/mra/server.py
	Alias /static /path/to/mra/src/static
	<Directory /home/mra/src/static>
	    Order deny,allow
	    Allow from all
	</Directory>
	AddType text/html .py .js
	<Directory /home/mra/src/mra>
	    SetHandler wsgi-script
	    Options ExecCGI FollowSymlinks
	    Order deny,allow
	    Allow from all
	</Directory>


You must reload Apache to make the change take effect.
Check the alias is working:
	
	http://localhost/mra


Settings
========
All settings are done in the ``mra/src/mra/mra.yaml`` file, which should be rather easy to adapt to your configuration. 
If you have checked out the svn repository, just rename the ``mra.yaml.sample`` in ``mra.yaml``. 
That way, your own configuration won't be discarded by a further update.

*	**storage**

	*	**mapfiles**

		Path to the directory containing your mapfiles, which can be located anywhere on your disk. 
		The MapServerRestAPI will scan this directory recursively to find all the mapfiles.

		``mapfiles: "/path/to/your/mapfiles/directory"``

	*	**resources**
		
		Path to the directory containing your data, which can be located anywhere on your disk.

		``resources: "/path/to/your/data/directory"``

*	**mapserver**

	*	**url**

		URL that should be used to access your mapserver.

		``url: "http://127.0.0.1/cgi-bin/mapserv?"``

	*	**wms_version**, **wfs_version**, **wcs_version**

		Default version to use for WMS, WFS and WCS.

*	**debug**

	*	**web_debug** [True | False]

		web_debug allows for easy debuging in the the browser, should be deactivated in production.

	*	**raise_all** [True | False]

		Exceptions are transformed into web errors.
		This can be prevented by setting raise_all to True.

*	**logging**

	*	**format**

		Format of the debug log. Here is a typical message:

		``format: "%(asctime)s %(levelname)7s: (%(funcName)s:%(lineno)s) %(message)s"``

	*	**file**

		Path to the log file, which can be located anywhere on your disk.

		``file: "./mra.log"``

	*	**level** [DEBUG | INFO | WARNING | ERROR]

		Level of debugging output.

	*	**web_logs** [False | True]
		
		To add the logs to the generated output of the webapp.

*	**testing**
	
    *	**active** [True | False]

    	Additions to the API for testing, should be deactivated in production.
    
    *	**model**

    	Mapfile to use to create new test files.

Finally check MapServer Rest API is working correctly: 

	http://localhost/mra/maps

Enjoy!
======

You are ready to use **MapServer Rest API**.

Please now refer to the **MapServer Rest API** Reference documentation.