Sphinx ReVIEW builder
=============================

.. image:: https://badge.fury.io/py/sphinxcontrib-reviewbuilder.svg
    :target: https://badge.fury.io/py/sphinxcontrib-reviewbuilder

.. image:: https://circleci.com/gh/shirou/sphinxcontrib-reviewbuilder.svg?style=svg
    :target: https://circleci.com/gh/shirou/sphinxcontrib-reviewbuilder

Sphinx to ReVIEW builder.

ReVIEW: https://github.com/kmuto/review

Setting
=======

Install
-------

::

   > pip install sphinxcontrib-reviewbuilder


Configure Sphinx
----------------

To enable this extension, add ``sphinxcontrib.reviewbuilder`` module to extensions
option at `conf.py`.

::

   # Enabled extensions
   extensions = ['sphinxcontrib.reviewbuilder']


How to use
=====================

::

  % make review

Repository
==========

https://github.com/shirou/sphinxcontrib-reviewbuilder


TODO
=======

- literal block includes highlight args


License
========

LGPL v2.

Same as ReVIEW original. See LICENSE file.
