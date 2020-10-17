#!/usr/bin/python
from classes import Menu, Gui
import os, sys

#create menu object
menu = Menu()

#give user sys args options - load gui or help then into terminal or just into terminal with no args
if "--help" in sys.argv:
    input("\nSee the help file in the menu for more information about the application \n\n"
          "Using --gui will launch the gui front end instead\nUsage: python main.py --gui \n\n- Press enter")
if '--gui' in sys.argv:
    Gui.make_gui()

#calls menu object
menu.menu()

