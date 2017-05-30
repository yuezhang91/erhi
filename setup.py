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
        'flask-restful>=0.3.5'
    ],
)
