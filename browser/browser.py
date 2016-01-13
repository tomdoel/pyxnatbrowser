#!/usr/bin/python

# https://github.com/tomdoel/pyxnatbrowser
# Author: Tom Doel www.tomdoel.com
# Distributed under the Simplified BSD License.

import tkinter

from browser.browserconfiguration import BrowserConfiguration
from browser.configsave import ConfigSave
from browser.mainframe import MainFrame


class Browser:
    def __init__(self, default_config):
        root = tkinter.Tk()
        root.wm_title("XNAT Browser")
        self.mainframe = MainFrame(root, default_config)
        root.mainloop()
