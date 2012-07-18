#!/usr/bin/env python

from setuptools import setup

setup (
     name = "autonetkit",
     version = "0.0.1",
     description = 'Automated network configuration',
     long_description = 'Automated network configuration',

     # simple to run 
     entry_points = {
         'console_scripts': [
             'autonetkit = autonetkit.console_script:main',
         ],
     },

     author = 'Simon Knight',
     author_email = "simon.knight@adelaide.edu.au",
     url = "http://autonetkit.org",
     packages = ['autonetkit'],

     #TODO: need better way to include nested templates, especially for quagga
     # refer http://stackoverflow.com/q/3712033

     package_data = {'autonetkit': [
         'templates/*.mako' ,
         'templates/ios2/*',
         ]},

     download_url = (""),

     install_requires = ['netaddr', 'mako', 'networkx>=1.7'],

     classifiers = [
         "Programming Language :: Python",
         "Development Status :: 3 - Alpha",
         "Intended Audience :: Science/Research",
         "Intended Audience :: System Administrators",
         "Intended Audience :: Telecommunications Industry",
         "License :: Other/Proprietary License",
         "Operating System :: POSIX :: Linux",
         "Operating System :: MacOS :: MacOS X",
         "Operating System :: Microsoft :: Windows",
         "Topic :: Scientific/Engineering :: Mathematics",
         "Topic :: System :: Networking",
         "Topic :: System :: Software Distribution",
         ],     
 
)
