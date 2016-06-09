#!/usr/bin/python

# https://github.com/tomdoel/pyxnatbrowser
# Author: Tom Doel www.tomdoel.com
# Distributed under the Simplified BSD License.
import tkinter

from browser.mainframe import MainFrame


class Browser:
    def __init__(self, default_config, rest_client_factory, title):
        root = tkinter.Tk()
        root.wm_title(title)
        self.mainframe = MainFrame(root, default_config, rest_client_factory)
        root.mainloop()
