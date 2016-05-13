timeseries
==========

.. image:: https://travis-ci.org/cs207-project/TimeSeries.svg?branch=master
    :target: https://travis-ci.org/cs207-project/timeseries-package
.. image:: https://coveralls.io/repos/github/cs207-project/TimeSeries/badge.svg?branch=master 
	:target: https://coveralls.io/github/cs207-project/TimeSeries?branch=master


This package delivers Persistent TimeSeries Database for CS207 final project.

Project Description
====================


========================================
1.1 Database Persistence
========================================


We used heap files to make our timeserise database persistent. The heap file are either created or loaded from local folder every time the persistent database server is launched, and based on which all db operations (insert, upsert, select, delete, augmented select, etc.) are performed and persisted real-time.

Specifically, we mainly have 4 types of binary files working together to ensure the database running smoothly and bug-free:

- ``ts_heap``:   where are actual ``timeseries`` data is stored
- ``metadata_heap``:   where all timeseries ``metadata`` (other fields except for ``ts`` in ``schema``) is sctored
- ``xxx_metadata_met``:   where the configuration information (e.g. ``ts_length``, ``schema``              for ``ts_heap``, ``metadata_heap``) is stored; this can be used to validate database upon loading;
- ``{field_name}.idx``: where all the index data is stored

Here we use python module ``struct`` to perform conversions between Python values and C structs represented as Python strings and use ``pickle`` to achieve Python object serialization.

====================
1.2 Index
====================
We designed four types of indices for different types of metadata and apply them according to values types or our functional goals:

-  PKIndex
    - Implemented using python dictionary with ``key`` = ``primary_key`` and ``value`` = ``offset``
    - Used only to store primary keys

-  Bitmap Index
    - Implemented using python dictionary with all possible disctinctive values of the given field as ``key`` s and bitmap vectors over the ``timeseries`` as ``values``.
    - Used to store low-cardinality fields, in our case they are: ``order``, ``order``, ``blarg`` and ``vp``.


-  Binary Tree Index
    - Implemented using ``AVL Tree`` (self-balancing binary search tree) with repeated values stored in a list.
    - Used to store high-cardinality or numerical fields, in our case they are: ``mean``, ``std``, ``vp_x``.

-  VPTree Index
    - Implemented using ``VPTree`` constructed using ``knn`` algorithm
    - Specially revered for timeseries similarity search (see more in the "Extra Credit: VPTree" section)

====================
1.3 Vantage Point
====================
In addition to the basic requirement of representing vantage points in this persistent database and do vantage point searches, we implemented vptree representation and used KNN for initialisation. Refer to "Extra Credit" section / sample codes / test cases for it's mechanism  and user instruction.


====================
1.4 Rest API
====================
structure
---------------

We adopted ``aiohttp`` when implementing REST api to support asynchronous client.
``/web/web_appication.py`` is the code according to ``aiohttp`` implementation.
``WebApplication`` object contains ``aiohttp web.Application()`` instance as its property ``self.app``,
so it is runnable by calling ``WebApplication.run()`` as it calls ``aiohttp web.run_app(app)``.
Another file ``/go_web.py`` helps us to run this ``WebApplication``. Note that it requires TSDB_server to be run beforehand.
This can be achieved by running ``go_server.py`` and then ``go_web.py``.

We defined each client functionality in ``WebApplication`` by assigning one function to one router.
The functions can be accessed through web by following rule ::

	# =================================
	# CS 207 Final Project
	# TSDB RESTful API Implementation
	# =================================

	# Followings are the rule for router

	localhost:8080/tsdb                     root page
	localhost:8080/tsdb/select              select
	localhost:8080/tsdb/augmented_select    augmented select
	localhost:8080/tsdb/find_similar        timeSeries similarity search
	localhost:8080/tsdb/insert_ts           insert
	localhost:8080/tsdb/add_trigger         add trigger
	localhost:8080/tsdb/remove_trigger      remove trigger
	localhost:8080/tsdb/add_metadata        upsert metadata
	localhost:8080/tsdb/delete_ts		delete


When we access to a certain function, for instance, we access to `select` function by passing arguments through URL, ::

	localhost:8080/tsdb/select?query={"additional":{"sort_by":"-order"}}

Then corresponding handler will be called, parse the arguments
and call corresponding function in ``tsdb_client``. Then the rest of work will be done as client part in previous Milestones.

For ``GET Request`` cases (such as `select`), after the client got response from server, it will print out the result on web
by ``web.Response(body=text)``. For the example we saw above with ``select``, the web browser will show up lists of TimeSeries instances in ordered way in json format.

For testing
---------------

To test the web_application, it has to be run with tsdb_server, so we adopted ``Python Subprocess``.
Then it turned out that the coverage cannot count in function calls in subprocess,
therefore, we implemented additional version of web_application, which is ``web_for_coverage.py``.
Basically what each functions do is the same with ``web_application.py``,
but in this case, we directly call handler file and pass the result got from server to Python Requests.
Then ``test_web_for_coverage.py`` will take the Requests and check if it returned TSDBStatus.OK or ``<Response 200>``.

====================
1.5 Extra Credit
====================
Fast FFT Using Cython with fftw Integrated
---------------------------------------------
For the first extra feature, we implemented "FFT Using Cython with fftw Integrated", so that now we are able to do our computation in corr.py by C and therefore achieve higher speed when executing related database operations.

For more implementation details, please refer to our project folder ``/procs``.

VPTREE (Text Corpus Similarity Search Supported)
------------------------------------------------------------

In addition to simple vptree construction, we implemented an improved version using ``knn`` algorithm to speed up the vpnode search process. And except for time series data, we also used our implementation to test on natural language corpus. See the example attached below to learn how to use our tool!

* [**VPTREE EXAMPLE**] (vp_tree/VPTREE_DEMO.ipynb)


====================
1.7 To do
====================

- We tried transaction and rollback on fail by implementing file (partial) locks, however, due to time limitation, we wouldn't be able to present reliable interface and enough exception handling so we decide to move this part of of our final submission to ensure the rest part of projects functions well. We will explore more in the vacation for proof of concept.

User Guide
====================
========================================
2.1 Setting up environment
========================================


To make it runnable, some packages have to be installed beforehand. If you are using ``brew``, ::

	brew install swig


Then, under the ``/proc`` folder, there is ``setup.py``. Go to this folder and run the following ::

	python setup.py build_ext --inplace

Then the environment is set.

(For more information for environment setting, refer to https://docs.python.org/2/distutils/configfile.html)


========================================
2.2 Installation
========================================

To install the package, go to the project root folder and execute::

	python setup.py install

================================================
2.3 Starting Server and Populating Database
================================================

First, under the root folder, simply type::

	python go_persistent_server.py

and this will help you launch the persistent server. Then, to populate the database with initial timeseries dataset, start another terminal (this could be done in mac system by pressing ``command`` + ``T``), go to the same root folder, and execute::

	python go_client.py


========================================
2.4 Try It Out!
========================================
For user, we provide two easy way to test out our database:

- with the server on (see steps in ``2.3``), you can either go to root folder, and type::

	python go_web.py

and go to the web application interface as prompt to access db through http request;


- Or you could refer to our demo to get more customised options for more db operations:
[Database function demonstration] (docs/Web_service_demo.ipynb)

========================================
2.5 Support Documentation
========================================

REST api
---------------

* ``/web/web_application.py`` has main REST api implementation and docs as well.
* ``/web/web_for_coverage.py`` is basically similar interface with ``web_application.py`` but directly send request so that it can be tested and covered by coverage.
* ``/test/test_web_application.py`` is not counted in coverage, but it shows how each functions can be accessed through web URL and triggering corresponding handlers.
* ``/test/test_web_for_coverage.py`` has test cases and documents demonstrating how each functions can be called and used through sending back requests.

Timeseries package includes two modules: 'timeseries' and 'pype'.

Discussions
========================

========================================
What difficulty have we encountered?
========================================



========================================
What we learned?
========================================