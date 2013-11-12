Installation
============


Installing the package
----------------------

`django-proxylist-for-grab` can be easily installed using pip:

.. code-block:: bash

   $ pip install django-proxylist-for-grab


Configuration
-------------

After that you need to include `django-proxylist-for-grab` into your *INSTALLED_APPS*
list of your django settings file.

.. code-block:: python

   INSTALLED_APPS = (
     ...
     'proxylist',
     ...
   )


`django-proxylist-for-grab` has a list of variables that you can configure throught
django's settings file. You can see the entire list at Advanced Configuration.

Database creation
-----------------

You have two choices here:

Using south
~~~~~~~~~~~

We encourage you using `south` for your database migrations. If you
already use it you can migrate `django-proxylist-for-grab`:

.. code-block:: bash

   $ python manage.py migrate proxylist



Using syncdb
~~~~~~~~~~~~

If you don't want to use `south` you can make a plain *syncdb*:

.. code-block:: bash

   $ python manage.py syncdb


