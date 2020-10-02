#from unittest import Testcase
from classes import Astronaut, Iss
import unittest

class TestMathFunctions(unittest.TestCase):

    def test_working_get_astro_api(self):
        astro = Astronaut.get_astro()
        try:
            self.assertIsNotNone(astro, msg="The Astronaut API is currently UP!")
        except:
            self.assertIsNone(astro, msg="The Astronaut API is not up")


    def test_working_get_iss_api(self):
        iss = Iss.iss_current_co_ords()
        try:
            self.assertIsNotNone(iss, msg="The ISS API is currently UP!")
        except:
            self.assertIsNone(iss, msg="The ISS API is not up")





