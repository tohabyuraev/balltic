#!/usr/bin/env python3
"""
Balltic - pretty simple package for solving problems of internal ballistics with Python.

It provides:

- Solve the problem in a thermodynamic setting
- Solve the problem in a gas-dynamic setting
- Visualize the solution in the form of graphs

"""

from setuptools import setup, find_packages

CLASSIFIERS = (
    'Intended Audience :: Science/Research',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Topic :: Scientific/Engineering',
    'Operating System :: OS Independent'
)

MAJOR = 0
MINOR = 0
MICRO = 1
VERSION = f'{MAJOR}.{MINOR}.{MICRO}'


with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="Balltic",
    version='0.0.1',
    description="Ballistics",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="BSD",
    author="Anthony Byuraev",
    author_email="anthony.byuraev@gmail.com",
    url="https://github.com/tohabyuraev/balltic",
    packages=find_packages(),
    classifiers=[_f for _f in CLASSIFIERS],
    python_requires='>=3.6'
)
