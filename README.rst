==========
timeseries
==========

.. image:: https://travis-ci.org/cs207-project/TimeSeries.svg?branch=master
    :target: https://travis-ci.org/cs207-project/timeseries-package
.. image:: https://coveralls.io/repos/github/cs207-project/TimeSeries/badge.svg?branch=master 
	:target: https://coveralls.io/github/cs207-project/TimeSeries?branch=master


This package delivers Persistent TimeSeries Database for CS207 final project.





1. Persistent DB what you did (a para on the architecture of the persistence, your additional part, and REST api)
=================================================================================================================
______

2. Additional Part : FFT implementation
=======================================


**1) Environment Setting**

To make it runnable, some packages have to be installed beforehand. If you are using ``brew``, ::
	
	brew install swig
	

Then, under the ``/proc`` folder, there is ``setup.py``. Go to this folder and run the following ::
	
	python setup.py build_ext --inplace
	
Then the environment is set.

(For more information for environment setting, refer at https://docs.python.org/2/distutils/configfile.html)



______



3. REST api
===========

**1) structure**

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


When we access to a certain function, for instance, we access to `select` function by passing arguments through URL, ::

	localhost:8080/tsdb/select?query={"additional":{"sort_by":"-order"}}

Then corresponding handler will be called, parse the arguments
and call corresponding function in ``tsdb_client``. Then the rest of work will be done as client part in previous Milestones.

For ``GET Request`` cases (such as `select`), after the client got response from server, it will print out the result on web
by ``web.Response(body=text)``. For the example we saw above with ``select``, the web browser will show up lists of TimeSeries instances in ordered way in json format.

______

**2) For testing**

To test the web_application, it has to be run with tsdb_server, so we adopted ``Python Subprocess``.
Then it turned out that the coverage cannot count in function calls in subprocess,
therefore, we implemented additional version of web_application, which is ``web_for_coverage.py``.
Basically what each functions do is the same with ``web_application.py``,
but in this case, we directly call handler file and pass the result got from server to Python Requests.
Then ``test_web_for_coverage.py`` will take the Requests and check if it returned TSDBStatus.OK or ``<Response 200>``.

______


4. How to install our project

5. Where to find the docs (for the rest api, running the server, populating the database)
The stuff in https://iacs-cs207.github.io/cs207/ProjectExpectations.html
1) REST api
/web/web_application.py


Timeseries package includes two modules: 'timeseries' and 'pype'.

Note
====

This project has been set up using PyScaffold 2.5.5. For details and usage
information on PyScaffold see http://pyscaffold.readthedocs.org/.
