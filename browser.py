#!/usr/bin/python

# https://github.com/tomdoel/pyxnatbrowser
# Author: Tom Doel www.tomdoel.com
# Distributed under the Simplified BSD License.

import tkinter

from mainframe import MainFrame
from xnatdatabase import XnatDatabase
from restclient import RestClient


class Browser:
    def __init__(self, config):
        rest_client = RestClient(config)
        xnat_database = XnatDatabase(rest_client, config)
        root = tkinter.Tk()
        root.wm_title("XNAT Browser")
        self.mainframe = MainFrame(root, xnat_database)
        root.mainloop()
