from nose.tools import *
import itasca

def test_get_version():
    assert type(itasca.get_version()) == str
