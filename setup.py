#!/usr/bin/env python

from setuptools import setup, find_packages


setup(
    name="erhi",
    version="0.0.1",

    # metadata for upload to PyPI
    author="Yue Zhang",
    author_email="deyomizy@gmail.com",
    description="The API server for Hier",
    license="Not licensed",
    keywords="API server Hier",
    url="https://github.com/FredSUEE/erhi",  # project home page, if any
    # could also include long_description, download_url, classifiers, etc.

    packages=find_packages(),

    install_requires=[
        'flask-restplus>=0.10.1',
        'flask-script>=0.4.0',
        'flask-mongoengine>=0.9.3',
        'flask-httpauth>=3.2.3',
        'pre-commit>=0.14.2',
        'flake8>=3.3.0',
        'passlib>=1.7.1'
    ],
)
