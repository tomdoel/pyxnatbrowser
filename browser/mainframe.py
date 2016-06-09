# https://github.com/tomdoel/pyxnatbrowser
# Author: Tom Doel www.tomdoel.com
# Distributed under the Simplified BSD License.

from tkinter import PanedWindow, Menu
from tkinter import messagebox
from tkinter.constants import BOTH

from browser import __version__
from browser.browserconfiguration import BrowserConfiguration
from browser.configsave import ConfigSave
from browser.labeledlistbox import LabeledListBox
from browser.progresslistbox import LabeledProgressListBox
from browser.settingsmenu import SettingsMenu
from database.xnatdatabase import XnatDatabase
from database.xnatmodelfactory import XnatModelFactory


class MainFrame:
    def __init__(self, root, default_config, rest_client_factory):
        self._rest_client_factory = rest_client_factory
        self.root = root
        self.config_save = ConfigSave(BrowserConfiguration.get_properties_filename(), default_config)
        self.database_view = None
        self.reset_database()

        # Create the applicaiton menu
        self._menu = ApplicationMenu(root, self.config_save)

    def reset_database(self):
        if self.database_view is not None:
            self.database_view.close()
        self.database_view = DatabaseView(self.root, self.config_save, self._rest_client_factory)


class ApplicationMenu:
    def __init__(self, root, config_save):
        self.root = root
        self.config_save = config_save

        # Create a menu
        root_menu = Menu(root)
        root.config(menu=root_menu)

        xnat_menu = Menu(root_menu)
        root_menu.add_cascade(label="GIFT-Cloud", menu=xnat_menu)

        xnat_menu.add_command(label="About", command=self.menu_about)
        xnat_menu.add_separator()
        xnat_menu.add_command(label="Settings", command=self.menu_settings)
        xnat_menu.add_separator()
        xnat_menu.add_command(label="Quit", command=self.menu_exit)

    def menu_exit(self):
        self.root.quit()

    def menu_about(self):
        messagebox.showinfo("GIFT-Cloud Downloader", "Version " + __version__)

    def menu_settings(self):
        top = SettingsMenu(self, self.config_save)


class DatabaseView:
    def __init__(self, root, config_save, rest_client_factory):
        self.config = config_save.get_configuration()
        self.root = root
        application_folder = BrowserConfiguration.get_application_directory_and_create_if_necessary()
        self.database = XnatDatabase(rest_client_factory.create_rest_client(self.config), self.config, application_folder)
        self.database_models = XnatModelFactory(self.database)
        self.config_save = config_save

        self.master_paned_window = PanedWindow(root)
        self.master_paned_window.pack(fill=BOTH, expand=1)

        self._project_listbox = LabeledListBox(self.master_paned_window, self.database_models.project_list_model, 'Project:')
        self.master_paned_window.add(self._project_listbox)

        self._subject_listbox = LabeledListBox(self.master_paned_window, self.database_models.subject_list_model, 'Subject:')
        self.master_paned_window.add(self._subject_listbox)

        self._scan_listbox = LabeledProgressListBox(self.master_paned_window, self.database_models.scan_list_model, "Scans:")
        self.master_paned_window.add(self._scan_listbox)

    def close(self):
        self.master_paned_window.destroy()

