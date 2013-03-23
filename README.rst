Sphinx ReVIEW builder
=============================

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

  % sphinx-build -b review -d build/doctrees   source build/review

or you can add this command line to your Makefile.

Repository
==========

https://bitbucket.org/r_rudi/sphinxcontrib-reviewbuilder

License
========

LGPL v2.

Same as ReVIEW original. See LICENSE file.
