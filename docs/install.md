# How to install MapServer Rest API

This document describes how to install and configure **MapServer Rest API**.

## Prerequisites

**MapServer Rest API** needs the following components:

* Python with following packages:

	* **web.py**

	* **pyyaml**

	* **nosetests** (Not mandatory but required to run tests)

* **GDAL/OGR** (>= 1.9.x with **Python** support)

* **MapServer** (>= 6.x with **MapScript-Python** support)


## Download

Get the newest source code by downloading the archive at [download](https://github.com/neogeo-technologies/mra) page.
Then extract the archive in a directory of your choice.
Or checkout the Git in some place.

## Installation

There is nothing to do more.

Configure your server, e.g. with **Apache**, just create a virtual directory and the following aliases:

    WSGIPythonPath /path/to/mra/src/mra
    WSGIScriptAlias /mra /path/to/mra/src/mra/server.py
    Alias /static /path/to/mra/static
    <Directory /home/mra/static>
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
Check the alias is working: [http://localhost/mra](http://localhost/mra)


## Settings

All settings are done in the `mra/src/mra/mra.yaml` file, which should be rather easy to adapt to your configuration. 
If you have checked out the svn repository, just rename the `mra.yaml.sample` in `mra.yaml`. 
That way, your own configuration won't be discarded by a further update.

* **storage**

	* **root**

		All default storage paths are relative to mra's root which is described here

		`root: "/my/full/path/to/mra/root"`

	However, you can specify specific directories for any of those sub-directories. They will default to `root/sub_directory_name`

    * **services**
    * **available**
    * **resources**
	* **styles**
    * **data**
    * **fonts** and **fontset**

* **mapserver**

	* **url**

		URL that should be used to access your mapserver.

		`url: "http://127.0.0.1/cgi-bin/mapserv?"`

	* **wms\_version**, **wfs\_version**, **wcs\_version**

		Default version to use for WMS, WFS and WCS.

* **debug**

	* **web\_debug** [`True`|`False`]

		`web_debug` allows for easy debuging in the the browser, should be deactivated in production.

	* **raise\_all** [`True`|`False`]

		Exceptions are transformed into web errors. This can be prevented by setting `raise_all` to `True`.

* **logging**

	* **format**

		Format of the debug log. Here is a typical message:

		`format: "%(asctime)s %(levelname)7s: (%(funcName)s:%(lineno)s) %(message)s"`

	* **file**

		Path to the log file, which can be located anywhere on your disk.

		`file: "./mra.log"`

	* **level** [`DEBUG`|`INFO`|`WARNING`|`ERROR`]

		Level of debugging output.

	* **web\_logs** [`True`|`False`]
		
		To add the logs to the generated output of the webapp.

* **plugins**

	* **loadpaths**

		The paths in this lists will be loaded as plugins. 
		A plugin can be a python package, if that is the case it should define the `__all__` attribute to indicate which modules should be handled as plugins. (An example can be found in `/plugins)

		    loadpaths: [
			   "/my/full/path/to/plugins"
    		]

Finally check MapServer Rest API is working correctly: [http://localhost/mra](http://localhost/mra)

## Enjoy!

You are ready to use **MapServer Rest API**.
Please now refer to the **MapServer Rest API** Reference documentation.