# -*- coding: utf-8 -*-
"""Installer for the ftw.plop package."""

from setuptools import find_packages
from setuptools import setup


long_description = (
    open('README.rst').read() +
    '\n' +
    'Contributors\n' +
    '============\n' +
    '\n' +
    open('CONTRIBUTORS.rst').read() +
    '\n' +
    open('CHANGES.rst').read() +
    '\n')


setup(
    name='ftw.flamegraph',
    version='1.0a1',
    description="A statistical profiler for Plone which outputs a flamegraph",
    long_description=long_description,
    # Get more from https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 4.3",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords='Python Plone',
    author='Thomas Buchberger',
    author_email='t.buchberger@4teamwork.ch',
    url='https://pypi.python.org/pypi/ftw.plop',
    license='GPL version 2',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['ftw'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'six',
    ],
    extras_require={
        'test': [
            'plone.app.testing',
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
