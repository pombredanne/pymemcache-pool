#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='pymemcache-pool',
      version='0.1',
      description='',
      author='Stephen Huenneke',
      author_email='stephen@runscope.com',
      url='http://github.com/Runscope/pymemcache-pool',
      packages=find_packages(),
      zip_safe=False,
      include_package_data=True,
      platforms='any',
      install_requires=[
          'gevent==0.13.8',
          'greenlet==0.4.0',
          'pymemcache==1.0.1',
          'wsgiref==0.1.2'
      ],
      )
