=====================================================
MapServer Rest API - Rest Configuration API Reference
=====================================================



Formats and representations
===========================

The following table defines the ``content-type`` values for each format you can use.

+-------------+---------------------------------------------------------------+
| Format      | Content-type                                                  |
+=============+===============================================================+
| XML         | ``application/xml`` (or ``text/xml``)                         |
+-------------+---------------------------------------------------------------+
| JSON        | ``application/json``                                          |
+-------------+---------------------------------------------------------------+
| HTML        | ``text/html``                                                 |
+-------------+---------------------------------------------------------------+
| SLD         | ``application/vnd.ogc.sld+xml``                               |
+-------------+---------------------------------------------------------------+
| MAP         | ``text/plain``                                                |
+-------------+---------------------------------------------------------------+


Status codes
============

The following table sets out the main ``status-code`` you can obtain.

+-------------+---------------------------------------------------------------+
| Status-code | Definition                                                    |
+=============+===============================================================+
| 200         | The request was fulfilled                                     |
+-------------+---------------------------------------------------------------+
| 201         | The request was fulfilled and resulted in a new resource      |
|             | being created                                                 |
+-------------+---------------------------------------------------------------+
| 403         | The server understood the request, but is refusing to fulfill |
|             | it                                                            |
+-------------+---------------------------------------------------------------+
| 404         | The server has not found anything matching the URI given      |
+-------------+---------------------------------------------------------------+
| 405         | The method is not allowed by the server                       |
+-------------+---------------------------------------------------------------+
| 500         | The server encountered an unexpected condition which          |
|             | prevented it from fulfilling the request                      |
+-------------+---------------------------------------------------------------+
| 501         | The server does not support the functionality required to     |
|             | fulfill the request.                                          |
+-------------+---------------------------------------------------------------+

See `HTTP specification`_ for more information about status codes.

.. _HTTP specification: http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html


Maps
====

``Maps`` includes all mapfiles.

The Mapfile is the heart of MapServer. 
It defines the relationships between objects, points MapServer to where data are located and defines how things are to be drawn.

See `Mapfile specification`_ for more information about the Mapfile.

.. _Mapfile specification: http://www.mapserver.org/mapfile/


Operations
----------

``/maps.<format>``
^^^^^^^^^^^^^^^^^^

| Replace ``<format>`` by the format extension of your choice.

+--------+---------------------------------+-------------+--------------------+
| Method | Action                          | Return Code | Formats            |
+========+=================================+=============+====================+
| GET    | List all mapfiles               | 200         | XML, JSON, HTML    |
+--------+---------------------------------+-------------+--------------------+
| POST   | Create a new mapfile            | 201 with    | XML, JSON          |
|        |                                 | ``location``|                    |
|        |                                 | header      |                    |
+--------+---------------------------------+-------------+--------------------+
| PUT    |                                 | 405         |                    |
+--------+---------------------------------+-------------+--------------------+
| DELETE |                                 | 405         |                    |
+--------+---------------------------------+-------------+--------------------+


*Exceptions:*

*	POST for a mapfile already exist: 409 Conflict


``/maps/<map>.<format>``
^^^^^^^^^^^^^^^^^^^^^^^^

| Replace ``<format>`` by the format extension of your choice.

+--------+---------------------------------+-------------+--------------------+
| Method | Action                          | Return Code | Formats            |
+========+=================================+=============+====================+
| GET    | List all mapfiles               | 200         | MAP, XML, JSON,    |
|        |                                 |             | HTML               |
+--------+---------------------------------+-------------+--------------------+
| POST   |                                 | 405         |                    |
+--------+---------------------------------+-------------+--------------------+
| PUT    | *TODO: Modify mapfile <map>*    |             |                    |
+--------+---------------------------------+-------------+--------------------+
| DELETE | Delete mapfile <map>            |             |                    |
+--------+---------------------------------+-------------+--------------------+

*Exceptions:*

*	GET for a mapfile does not exist: 404 Not Found
*	*TODO: PUT that changes name of mapfile: 403 Forbidden*
*	*TODO: DELETE against a mapfile that is non-empty: 403 Forbidden*


Workspaces
==========

A workspace is a grouping of data stores and coverage stores.

Operations
----------

``/maps/<map>/workspaces.<format>``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| Replace ``<map>`` by the name of your mapfile.
| Replace ``<format>`` by the format extension of your choice.

+--------+---------------------------------+-------------+--------------------+
| Method | Action                          | Return Code | Formats            |
+========+=================================+=============+====================+
| GET    | List all workspaces             | 200         | XML, JSON, HTML    |
+--------+---------------------------------+-------------+--------------------+
| POST   | *TODO: Create a new workspace*  |             |                    |
+--------+---------------------------------+-------------+--------------------+
| PUT    |                                 | 405         |                    |
+--------+---------------------------------+-------------+--------------------+
| DELETE |                                 | 405         |                    |
+--------+---------------------------------+-------------+--------------------+


``/maps/<map>/workspaces/<ws>.<format>``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For current version of MapServer Rest API, a ``workspace`` corresponds to a mapfile.
And so, only one workspace can be available.
Thus, in order to not confuse the two concepts, the workspace is set to 'default' value.


``/maps/<map>/workspaces/default.<format>``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| Replace ``<map>`` by the name of your mapfile.
| Replace ``<format>`` by the format extension of your choice.

+--------+---------------------------------+-------------+--------------------+
| Method | Action                          | Return Code | Formats            |
+========+=================================+=============+====================+
| GET    | Return default workspace        | 200         | XML, JSON, HTML    |
+--------+---------------------------------+-------------+--------------------+
| POST   |                                 | 405         |                    |
+--------+---------------------------------+-------------+--------------------+
| PUT    |                                 | 405         |                    |
+--------+---------------------------------+-------------+--------------------+
| DELETE |                                 | 405         |                    |
+--------+---------------------------------+-------------+--------------------+


Data stores
===========

A ``data store`` is a source of spatial data that is vector based.
Only the case of PostGIS is currently implemented.

Operations
----------

``/maps/<map>/workspaces/<ws>/datastores.<format>``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| Replace ``<map>`` by the name of your mapfile.
| Replace ``<ws>`` by the name of your workspace.
| Replace ``<format>`` by the format extension of your choice.

+--------+---------------------------------+-------------+--------------------+
| Method | Action                          | Return Code | Formats            |
+========+=================================+=============+====================+
| GET    | List all data stores in         | 200         | XML, JSON, HTML    |
|        | workspace/mapfile <ws>          |             |                    |
+--------+---------------------------------+-------------+--------------------+
| POST   | Create new data store           | 201 with    | XML, JSON          |
|        |                                 | ``location``|                    |
|        |                                 | header      |                    |
+--------+---------------------------------+-------------+--------------------+
| PUT    |                                 | 405         |                    |
+--------+---------------------------------+-------------+--------------------+
| DELETE |                                 | 405         |                    |
+--------+---------------------------------+-------------+--------------------+

*Exceptions:*

*	POST for a data store already exist: 409 Conflict


``/maps/<map>/workspaces/<ws>/datastores/<ds>.<format>``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| Replace ``<map>`` by the name of your mapfile.
| Replace ``<ws>`` by the name of your workspace.
| Replace ``<ds>`` by the name of datastore available of your choice.
| Replace ``<format>`` by the format extension of your choice.

+--------+---------------------------------+-------------+--------------------+
| Method | Action                          | Return Code | Formats            |
+========+=================================+=============+====================+
| GET    | Return data store <ds>          | 200         | XML, JSON, HTML    |
+--------+---------------------------------+-------------+--------------------+
| POST   |                                 | 405         |                    |
+--------+---------------------------------+-------------+--------------------+
| PUT    | Modify data store <ds>          | 200         | XML, JSON          |
+--------+---------------------------------+-------------+--------------------+
| DELETE | Delete data store <ds>          | 200         |                    |
+--------+---------------------------------+-------------+--------------------+

*Exceptions:*

*	GET for a data store does not exist: 404 Not Found
*	PUT that changes name of data store: 403 Forbidden
*	DELETE against a data store that contains configured feature type: 403 Forbidden


``/maps/<map>/workspaces/<ws>/datastores/<ds>/file[.<extension>]``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Uploads a file from a local source. The body of the request is the file itself.

| Replace ``<map>`` by the name of your mapfile.
| Replace ``<ws>`` by the name of your workspace.
| Replace ``<ds>`` by the name of datastore available of your choice.

The ``<extension>`` parameter specifies the type of data store.
The following extensions are supported:

+-------------------+---------------------------------------------------------+
| Extension         | Datastore                                               |
+===================+=========================================================+
| shp               | OGR/ESRI Shapefile                                      |
+-------------------+---------------------------------------------------------+

+--------+--------------------------+-------------+-----------+---------------+
| Method | Action                   | Return Code | Formats   | Parameters    |
+========+==========================+=============+===========+===============+
| GET    |                          | 405         |           |               |
+--------+--------------------------+-------------+-----------+---------------+
| POST   |                          | 405         |           |               |
+--------+--------------------------+-------------+-----------+---------------+
| PUT    | Uploads files to the     | 200         | See notes | ``configure`` |
|        | data stores <ds>         |             | below.    | See notes     |
|        |                          |             |           | below.        |
+--------+--------------------------+-------------+-----------+---------------+
| DELETE |                          | 405         |           |               |
+--------+--------------------------+-------------+-----------+---------------+

Data stores like Shapefile must be sent as a zip archive.
When uploading a zip archive the ``Content-type`` should be set to ``application/zip``

The ``configure`` parameter is used to control how the data store is configured upon file upload.
It can take one of the below values :

*	``none`` - Do not configure any feature types. This is the default value

*	*TODO: ``first`` - Only setup the first feature type available in the data store.*
	
*	*TODO: ``all` - Configure all feature types.*


Feature types
=============

A ``feature type`` is a data set that originates from a data store.

Operations
----------

``/maps/<map>/workspaces/<ws>/datastores/<ds>/featuretypes.<format>``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| Replace ``<map>`` by the name of your mapfile.
| Replace ``<ws>`` by the name of your workspace.
| Replace ``<ds>`` by the name of datastore available of your choice.
| Replace ``<format>`` by the format extension of your choice.

+--------+---------------------------------+-------------+--------------------+
| Method | Action                          | Return Code | Formats            |
+========+=================================+=============+====================+
| GET    | List all feature types in       | 200         | XML, JSON, HTML    |
|        | selected data store <ds>        |             |                    |
+--------+---------------------------------+-------------+--------------------+
| POST   | Create a new feature type       | 201 with    | XML, JSON          |
|        |                                 | ``location``|                    |
|        |                                 | header      |                    |
+--------+---------------------------------+-------------+--------------------+
| PUT    |                                 | 405         |                    |
+--------+---------------------------------+-------------+--------------------+
| DELETE |                                 | 405         |                    |
+--------+---------------------------------+-------------+--------------------+

*Exceptions:*

*	GET for a feature type that does not exist: 404 Not Found
*	POST for a feature type already exist: 409 Conflict


``/maps/<map>/workspaces/<ws>/datastores/<ds>/featuretypes/<ft>.<format>``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| Replace ``<map>`` by the name of your mapfile.
| Replace ``<ws>`` by the name of your workspace.
| Replace ``<ds>`` by the name of datastore available of your choice.
| Replace ``<ft>`` by the name of feature type available of your choice.
| Replace ``<format>`` by the format extension of your choice.

+--------+---------------------------------+-------------+--------------------+
| Method | Action                          | Return Code | Formats            |
+========+=================================+=============+====================+
| GET    | Return feature type <ft>        | 200         | XML, JSON, HTML    |
+--------+---------------------------------+-------------+--------------------+
| POST   |                                 | 405         |                    |
+--------+---------------------------------+-------------+--------------------+
| PUT    | Modify feature type <ft>        | 200         | XML, JSON          |
+--------+---------------------------------+-------------+--------------------+
| DELETE | Delete feature type <ft>        | 200         |                    |
+--------+---------------------------------+-------------+--------------------+

*Exceptions:*

*	GET for a feature type does not exist: 404 Not Found
*	PUT that changes name of feature type: 403 Forbidden
*	DELETE against a feature type which is used by a layer: 403 Forbidden


Coverage stores
===============

A ``coverage store`` is a source of spatial data that is raster based.

Operations
----------

``/maps/<map>/workspaces/<ws>/coveragestores.<format>``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| Replace ``<map>`` by the name of your mapfile.
| Replace ``<ws>`` by the name of your workspace.
| Replace ``<format>`` by the format extension of your choice.

+--------+---------------------------------+-------------+--------------------+
| Method | Action                          | Return Code | Formats            |
+========+=================================+=============+====================+
| GET    | List all coverage stores in     | 200         | XML, JSON, HTML    |
|        | workspace                       |             |                    |
+--------+---------------------------------+-------------+--------------------+
| POST   | Create new coverage store       | 201 with    | XML, JSON          |
|        |                                 | ``location``|                    |
|        |                                 | header      |                    |
+--------+---------------------------------+-------------+--------------------+
| PUT    |                                 | 405         |                    |
+--------+---------------------------------+-------------+--------------------+
| DELETE |                                 | 405         |                    |
+--------+---------------------------------+-------------+--------------------+

*Exceptions:*

*	POST for a coverage store already exist: 409 Conflict


``/maps/<map>/workspaces/<ws>/coveragestores/<cs>.<format>``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| Replace ``<map>`` by the name of your mapfile.
| Replace ``<ws>`` by the name of your workspace.
| Replace ``<cs>`` by the name of coverage store available of your choice.
| Replace ``<format>`` by the format extension of your choice.

+--------+---------------------------------+-------------+--------------------+
| Method | Action                          | Return Code | Formats            |
+========+=================================+=============+====================+
| GET    | Return coverage store <cs>      | 200         | XML, JSON, HTML    |
+--------+---------------------------------+-------------+--------------------+
| POST   |                                 | 405         |                    |
+--------+---------------------------------+-------------+--------------------+
| PUT    | Modify coverage store <ds>      | 200         | XML, JSON          |
+--------+---------------------------------+-------------+--------------------+
| DELETE | Delete coverage store <ds>      | 200         |                    |
+--------+---------------------------------+-------------+--------------------+

*Exceptions:*

*	GET for a coverage store does not exist: 404 Not Found
*	PUT that changes name of coverage store: 403 Forbidden
*	DELETE against a coverage store that contains configured coverage: 403 Forbidden


Coverages
=========

A ``coverage`` is a raster based data set which originates from a coverage store.

Operations
----------

``/maps/<map>/workspaces/<ws>/coveragestores/<cs>/coverages.<format>``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| Replace ``<map>`` by the name of your mapfile.
| Replace ``<ws>`` by the name of your workspace.
| Replace ``<cs>`` by the name of coverage store available of your choice.
| Replace ``<format>`` by the format extension of your choice.

+--------+---------------------------------+-------------+--------------------+
| Method | Action                          | Return Code | Formats            |
+========+=================================+=============+====================+
| GET    | List all coverages in selected  | 200         | XML, JSON, HTML    |
|        | coverages store <cs>            |             |                    |
+--------+---------------------------------+-------------+--------------------+
| POST   | Create a new coverage           | 201 With    | XML, JSON          |
|        |                                 | ``Location``|                    |
|        |                                 | header      |                    |
+--------+---------------------------------+-------------+--------------------+
| PUT    |                                 | 405         |                    |
+--------+---------------------------------+-------------+--------------------+
| DELETE |                                 | 405         |                    |
+--------+---------------------------------+-------------+--------------------+

*Exceptions:*

*	POST for a coverage already exist: 409 Conflict


``/maps/<map>/workspaces/<ws>/coveragestores/<cs>/coverages/<c>.<format>``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| Replace ``<map>`` by the name of your mapfile.
| Replace ``<ws>`` by the name of your workspace.
| Replace ``<cs>`` by the name of coverage store available of your choice.
| Replace ``<c>`` by the name of coverage available of your choice.
| Replace ``<format>`` by the format extension of your choice.

+--------+---------------------------------+-------------+--------------------+
| Method | Action                          | Return Code | Formats            |
+========+=================================+=============+====================+
| GET    | Return coverage <c>             | 200         | XML, JSON, HTML    |
+--------+---------------------------------+-------------+--------------------+
| POST   |                                 | 405         |                    |
+--------+---------------------------------+-------------+--------------------+
| PUT    | Create new coverage <c>         | 200         | XML, JSON          |
+--------+---------------------------------+-------------+--------------------+
| DELETE | Delete coverage <c>             | 200         |                    |
+--------+---------------------------------+-------------+--------------------+

*Exceptions:*

*	GET for a coverage does not exist: 404 Not Found
*	PUT that changes name of coverage: 403 Forbidden
*	DELETE against a coverage which is used by a layer: 403 Forbidden


Styles
======

A ``style`` describes how a resource (feature type or coverage) should be symbolized or rendered by a Web Map Service. 
Styles are specified with SLD and translated into the mapfile (with CLASS and STYLE blocs) to be applied.

Operations
----------

``/maps/<map>/styles.<format>``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| Replace ``<map>`` by the name of your mapfile.
| Replace ``<format>`` by the format extension of your choice.

+--------+---------------------------------+-------------+--------------------+
| Method | Action                          | Return Code | Formats            |
+========+=================================+=============+====================+
| GET    | Return all styles for map <map> | 200         | XML, JSON, HTML    |
+--------+---------------------------------+-------------+--------------------+
| POST   | Create a new style for map      | 201 With    | SLD (see note      |
|        |                                 | ``Location``| below)             |
|        |                                 | header      |                    |
+--------+---------------------------------+-------------+--------------------+
| PUT    |                                 | 405         |                    |
+--------+---------------------------------+-------------+--------------------+
| DELETE |                                 | 405         |                    |
+--------+---------------------------------+-------------+--------------------+

+--------+--------------------------+-------------+-----------+---------------+
| Method | Action                   | Return Code | Formats   | Parameters    |
+========+==========================+=============+===========+===============+
| GET    | Return all styles        | 200         |           |               |
+--------+--------------------------+-------------+-----------+---------------+
| POST   | Create a new style       | 201 With    | SLD (see  | name (see note|
|        |                          | ``Location``| note      | below)        |
|        |                          | header      | below)    |               |
+--------+--------------------------+-------------+-----------+---------------+
| PUT    |                          | 405         |           |               |
+--------+--------------------------+-------------+-----------+---------------+
| DELETE |                          | 405         |           |               |
+--------+--------------------------+-------------+-----------+---------------+

When executing a POST request with an SLD style, the Content-type header should be set to ``application/vnd.ogc.sld+xml``.

The ``name`` parameter specifies the name to be given to the style.

*Exceptions:*

*	POST for a style already exist: 409 Conflict


``/maps/<map>/styles/<s>.<format>``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| Replace ``<map>`` by the name of your mapfile.
| Replace ``<s>`` by the name of the style for layer of your choice.
| Replace ``<format>`` by the format extension of your choice.

+--------+---------------------------------+-------------+--------------------+
| Method | Action                          | Return Code | Formats            |
+========+=================================+=============+====================+
| GET    | Return style <s>                | 200         | SLD, HTML, XML,    |
|        |                                 |             | JSON               |
+--------+---------------------------------+-------------+--------------------+
| POST   |                                 | 405         |                    |
+--------+---------------------------------+-------------+--------------------+
| PUT    | Modify style <s>                | 200         | SLD (see note      |
|        |                                 |             | below)             |
+--------+---------------------------------+-------------+--------------------+
| DELETE | Delete style <s>                | 200         |                    |
+--------+---------------------------------+-------------+--------------------+

When executing a POST request with an SLD style, the Content-type header should be set to ``application/vnd.ogc.sld+xml``.

*Exception:*

*	GET for a style does not exist: 404 Not Found
*	*TODO: PUT that changes name of style: 403 Forbidden*
*	*DELETE against a coverage which is used by a layer: 403 Forbidden*


Layers
======

A ``layer`` is a published resource (feature type or coverage) from a mapfile.

Operations
----------

``/maps/<map>/layers.<format>``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| Replace ``<map>`` by the name of your mapfile.
| Replace ``<format>`` by the format extension of your choice.

+--------+---------------------------------+-------------+--------------------+
| Method | Action                          | Return Code | Formats            |
+========+=================================+=============+====================+
| GET    | List all layers provided by     | 200         | XML, JSON, HTML    |
|        | the mapfile <map>               |             |                    |
+--------+---------------------------------+-------------+--------------------+
| POST   | Create a layer                  | 201 With    | XML, JSON          |
|        |                                 | ``Location``|                    |
|        |                                 | header      |                    |
+--------+---------------------------------+-------------+--------------------+
| PUT    |                                 | 405         |                    |
+--------+---------------------------------+-------------+--------------------+
| DELETE |                                 | 405         |                    |
+--------+---------------------------------+-------------+--------------------+

*Exception:*

*	POST for a layer already exist: 409 Conflict


``/maps/<map>/layers/<l>.<format>``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| Replace ``<map>`` by the name of your mapfile.
| Replace ``<l>`` by the name of the layer of your choice.
| Replace ``<format>`` by the format extension of your choice.

+--------+---------------------------------+-------------+--------------------+
| Method | Action                          | Return Code | Formats            |
+========+=================================+=============+====================+
| GET    | Return layer <l>                | 200         | XML, JSON, HTML    |
+--------+---------------------------------+-------------+--------------------+
| POST   |                                 | 405         |                    |
+--------+---------------------------------+-------------+--------------------+
| PUT    | Modify layer <l>                | 200         | XML, JSON          |
+--------+---------------------------------+-------------+--------------------+
| DELETE | Delete layer <l>                | 200         |                    |
+--------+---------------------------------+-------------+--------------------+

*Exception:*

*	GET for a layer does not exist: 404 Not Found
*	PUT that changes name of layer: 403 Forbidden


``/maps/<map>/layers/<l>/styles.<format>``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| Replace ``<map>`` by the name of your mapfile.
| Replace ``<l>`` by the name of the layer of your choice.
| Replace ``<format>`` by the format extension of your choice.

+--------+---------------------------------+-------------+--------------------+
| Method | Action                          | Return Code | Formats            |
+========+=================================+=============+====================+
| GET    | Return all styles for layer <l> | 200         | XML, JSON, HTML    |
+--------+---------------------------------+-------------+--------------------+
| POST   | Add a new style to layer <l>    | 201 With    | XML, JSON          |
|        |                                 | ``Location``|                    |
|        |                                 | header      |                    |
+--------+---------------------------------+-------------+--------------------+
| PUT    |                                 | 405         |                    |
+--------+---------------------------------+-------------+--------------------+
| DELETE |                                 | 405         |                    |
+--------+---------------------------------+-------------+--------------------+

*Exception:*

*	POST for a style already exist: 409 Conflict


``/maps/<map>/layers/<l>/styles/<s>.<format>``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| Replace ``<map>`` by the name of your mapfile.
| Replace ``<l>`` by the name of the layer of your choice.
| Replace ``<s>`` by the name of the style of your choice.
| Replace ``<format>`` by the format extension of your choice.

+--------+---------------------------------+-------------+--------------------+
| Method | Action                          | Return Code | Formats            |
+========+=================================+=============+====================+
| GET    |                                 | 405         |                    |
+--------+---------------------------------+-------------+--------------------+
| POST   |                                 | 405         |                    |
+--------+---------------------------------+-------------+--------------------+
| PUT    |                                 | 405         |                    |
+--------+---------------------------------+-------------+--------------------+
| DELETE | Remove style <s> from layer <l> | 200         |                    |
+--------+---------------------------------+-------------+--------------------+


Layergroups
===========

A ``layergroup`` is a grouping of layers and styles that can be accessed as a single layer in a WMS GetMap request.

Operations
----------

``/maps/<map>/layergroups.<format>``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| Replace ``<map>`` by the name of your mapfile.
| Replace ``<format>`` by the format extension of your choice.

+--------+---------------------------------+-------------+--------------------+
| Method | Action                          | Return Code | Formats            |
+========+=================================+=============+====================+
| GET    | List all layer groups provided  | 200         | XML, JSON, HTML    |
|        | by the mapfile <map>            |             |                    |
+--------+---------------------------------+-------------+--------------------+
| POST   | Create a new layer group        | 201 With    | XML, JSON          |
|        |                                 | ``Location``|                    |
|        |                                 | header      |                    |
+--------+---------------------------------+-------------+--------------------+
| PUT    |                                 | 405         |                    |
+--------+---------------------------------+-------------+--------------------+
| DELETE |                                 | 405         |                    |
+--------+---------------------------------+-------------+--------------------+

*Exception:*

*	POST for a layer group already exist: 409 Conflict


``/maps/<map>/layergroups/<lg>.<format>``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| Replace ``<map>`` by the name of your mapfile.
| Replace ``<lg>`` by the name of the layer group of your choice.
| Replace ``<format>`` by the format extension of your choice.

+--------+---------------------------------+-------------+--------------------+
| Method | Action                          | Return Code | Formats            |
+========+=================================+=============+====================+
| GET    | Return layer group <lg>         | 200         | XML, JSON, HTML    |
+--------+---------------------------------+-------------+--------------------+
| POST   |                                 | 405         |                    |
+--------+---------------------------------+-------------+--------------------+
| PUT    | Add layer group <lg>            | 200         | XML, JSON          |
+--------+---------------------------------+-------------+--------------------+
| DELETE | Delete layer group <lg>         | 200         |                    |
+--------+---------------------------------+-------------+--------------------+

*Exception:*

*	GET for a layer group does not exist: 404 Not Found
*	PUT that changes name of layer group: 403 Forbidden
