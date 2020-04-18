# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

long_desc = '''
Sphinx ReVIEW builder. ReVIEW is a easy-to-use digital publishing
system for books and ebooks.

ReVIEW: https://github.com/kmuto/review
'''

requires = ['Sphinx>=2.4', 'setuptools']

setup(
    name='sphinxcontrib-reviewbuilder',
    version='0.0.9',
    url='http://github.com/shirou/sphinxcontrib-reviewbuilder',
    download_url='http://pypi.python.org/pypi/sphinxcontrib-reviewbuilder',
    license='LGPL',
    author='WAKAYAMA Shirou',
    author_email='shirou.faw@gmail.com',
    description='Sphinx reviewbuilder extension',
    long_description=long_desc,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Documentation',
        'Topic :: Utilities',
    ],
    platforms='any',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires,
    namespace_packages=['sphinxcontrib'],
)
