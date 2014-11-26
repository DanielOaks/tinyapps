TinyApps
========
This is a collection of small webapps, designed to run off a local webserver on your computer and provide nice organisation software, issue-tracking, etc.

Running
-------
Simply cd to the tinyapps directory and run::

    pip3 install -r requirements.txt
    ./tinyapps

It starts up a local webserver on port 8080: `http://localhost:8080/ <http://localhost:8080/>`_

CSS Styling
-----------
We use `Compass <http://compass-style.org/>`_ and SASS to make our CSS handling a whole lot easier.

Simply `install Compass <http://compass-style.org/install/>`_ from the docs, then cd to the tinyapps directory and run::

    compass watch

Compass will automatically regenerate CSS files as you edit the base SASS files in ``static/sass``

Contact
-------
The author of this project can be contacted at `daniel@danieloaks.net <mailto:daniel@danieloaks.net>`_

License
-------
This project is released under a BSD 2-clause license, as in the `license file <LICENSE>`_
