import os
from setuptools import setup, find_packages

def get_long_description():
    with open(os.path.join(os.path.dirname(__file__), 'README.md')) as f:
        return f.read()

setup(
    name = 'itasca',
    version = __import__('itasca').get_version(),
    url = 'https://bitbucket.org/jkfurtney/itasca-python',
    author = 'Jason Furtney',
    author_email = 'jkfurtney@gmail.com',
    description = "Python conectivity for Itasca software",
    long_description = get_long_description(),
    keywords = 'itasca flac flac3d PFC',
    tests_require = ['nose'],
    install_requires = [],
    packages = find_packages(),
    include_package_data = True,
    classifiers = [
        'Programming Language :: Python :: 2',
    ],
    entry_points = { }
)
