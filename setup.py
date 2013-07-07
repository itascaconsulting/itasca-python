import os
from setuptools import setup, find_packages

long_description = """
Python connectivity for Itasca software.

This library implements a connection via sockets between Python and
the numerical modeling software from Itasca Consulting Group.

www.itascacg.com/software

FLAC, FLAC3D, PFC2D, PFC3D, UDEC & 3DEC

See https://github.com/jkfurtney/itasca-python for more information.
"""

setup(
    name = 'itasca',
    version = __import__('itasca').get_version(),
    url = "https://github.com/jkfurtney/itasca-python",
    author = 'Jason Furtney',
    author_email = 'jkfurtney@gmail.com',
    description = "Python conectivity for Itasca software",
    long_description = long_description,
    keywords = 'Itasca FLAC FLAC3D PFC UDEC 3DEC',
    license          = "BSD",
    tests_require = ['nose'],
    install_requires = ['numpy >= 1.0.2'],
    packages = find_packages(),
    include_package_data = True,
    classifiers = [
        'Programming Language :: Python :: 2',
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: BSD License",
        'Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator',
        "Intended Audience :: Science/Research"
    ],
    entry_points = { }
)
