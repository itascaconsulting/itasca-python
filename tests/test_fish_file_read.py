import struct
from itasca import FishBinaryReader

# see create-test-data.f3dat to generate this test data
fish_file = FishBinaryReader("testdata.fish")

assert fish_file.read() == 1
assert fish_file.read() == 99.987
assert fish_file.read() == "James"
assert fish_file.read() == [99.5, 89.3]
assert fish_file.read() == [7.0, 8.0, 9.0]
print "FISH read test passed"
