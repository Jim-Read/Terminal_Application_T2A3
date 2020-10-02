#!/usr/bin/python
from classes import Menu, Gui
import os, sys


if "--help" in sys.argv:
    input("\nSee the help file in the menu for more information about the application \n\nUsing --gui will launch the gui front end instead\nUsage: python main.py --gui \n\n- Press enter")
if '--gui' in sys.argv:
    Gui.make_gui()



self = Menu()
self.menu()







self = Menu()
self.menu()

