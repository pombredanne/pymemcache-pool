#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='pymemcache-pool',
      version='1.0',
      description='',
      author='Stephen Huenneke',
      author_email='stephen@runscope.com',
      url='http://github.com/Runscope/pymemcache-pool',
      packages=find_packages(),
      zip_safe=False,
      include_package_data=True,
      platforms='any',
      install_requires=[
          'gevent==1.0',
          'greenlet==0.4.2',
          'pymemcache>=1.0.1',
          'wsgiref==0.1.2'
      ],
      )
