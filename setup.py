#!/usr/bin/env python

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages


long_description = open('README.md').read()

setup(
    name = "clog",
    version = "0.2",
    packages = find_packages(exclude=[]),
    include_package_data = True,
    description = "Command Log. Or Captain's Log.",
    long_description = long_description,
    install_requires = ['sqlalchemy','parsedatetime','unstdlib'],
    author = "Andrey Petrov",
    author_email = "andrey.petrov@shazow.net",
    url = "http://github.com/shazow/clog",
    license = "MIT",
    entry_points="""
    # -*- Entry points: -*-
    """,
    scripts=['bin/clog', 'bin/clogflow'],
)
