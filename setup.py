long_description = """
Python connectivity for Itasca software.

This library implements a connection via sockets between Python and
the numerical modeling software from Itasca Consulting Group.
Functions are provided to read and write files in the Itasca FISH
binary format.

www.itascacg.com/software

FLAC, FLAC3D, PFC2D, PFC3D, UDEC & 3DEC

See https://github.com/jkfurtney/itasca-python for more information.
"""

from distutils.core import setup
setup(
    name = 'itasca',
    packages = ['itasca'], # this must be the same as the name above
    version = __import__('itasca').__version__,
    description = "Python connectivity for Itasca software",
    long_description = long_description,
    author = 'Jason Furtney',
    requires = ['numpy'],
    author_email = 'jkfurtney@gmail.com',
    url = "https://github.com/jkfurtney/itasca-python",
    keywords = 'Itasca,FLAC,FLAC3D,PFC,UDEC,3DEC,PFC2D,PFC2D,FISH'.split(","),
    license          = "BSD",
    classifiers = [
        'Programming Language :: Python :: 2',
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: BSD License",
        'Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator',
        "Intended Audience :: Science/Research"
    ],
)
