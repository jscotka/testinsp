from unittest import TestCase
from testinsp.network import Interfaces
from pprint import pprint

class Network(TestCase):

    def test_network(self):
        interfaces = Interfaces()
        interfaces.initalize()
        pprint(interfaces.data_storage)