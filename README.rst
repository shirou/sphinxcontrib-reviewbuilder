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

  % make review

or you can add this command line to your Makefile.

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
