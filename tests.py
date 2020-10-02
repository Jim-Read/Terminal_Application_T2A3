# #from unittest import Testcase
# from classes import Astronaut, Iss
# import unittest

# class TestMathFunctions(unittest.TestCase):

#     def test_working_get_astro_api(self):
#         astro = Astronaut.get_astro()
#         try:
#             self.assertIsNotNone(astro, msg="The Astronaut API is currently UP!")
#         except:
#             self.assertIsNone(astro, msg="The Astronaut API is not up")


#     def test_working_get_iss_api(self):
#         iss = Iss.iss_current_co_ords()
#         try:
#             self.assertIsNotNone(iss, msg="The ISS API is currently UP!")
#         except:
#             self.assertIsNone(iss, msg="The ISS API is not up")




from rich.progress import Progress

import time



with Progress() as progress:

    task1 = progress.add_task("[red]Getting Resources...", total=1000)
    task2 = progress.add_task("[green]Building Resources...", total=1000)
    task3 = progress.add_task("[cyan]Finalizing...", total=1000)

    while not progress.finished:
        progress.update(task1, advance=8)
        progress.update(task2, advance=7)
        progress.update(task3, advance=5)
        time.sleep(0.02)