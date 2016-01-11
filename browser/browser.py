#!/usr/bin/python

# https://github.com/tomdoel/pyxnatbrowser
# Author: Tom Doel www.tomdoel.com
# Distributed under the Simplified BSD License.

import tkinter

from browser.browserconfiguration import BrowserConfiguration
from browser.configsave import ConfigSave
from browser.mainframe import MainFrame
from database.xnatdatabase import XnatDatabase
from database.restclient import RestClient


class Browser:
    def __init__(self, default_config):
        root = tkinter.Tk()
        root.wm_title("XNAT Browser")
        application_folder = BrowserConfiguration.get_application_directory_and_create_if_necessary()
        config_save = ConfigSave(BrowserConfiguration.get_properties_filename(), default_config)
        config = config_save.load()
        rest_client = RestClient(config)
        xnat_database = XnatDatabase(rest_client, config, application_folder)
        self.mainframe = MainFrame(root, xnat_database, config, config_save)
        root.mainloop()
