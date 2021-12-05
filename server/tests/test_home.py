import pytest
import json
import copy
import sys
import os
print(sys.path)
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
print(sys.path)
from logger_utils import Logger

#Initiating logger object

logger_object = Logger("server/logs/test_home.log")
logger = logger_object.get_logger()


class TestAPIs(object):

    @pytest.fixture(scope="class", autouse=True)
    def create_prerequisites(self):
        logger.debug("I am in prerequite running before everything")

    def test_first(self):
        assert True
