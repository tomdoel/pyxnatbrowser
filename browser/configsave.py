import os
from configparser import ConfigParser

from browser.PropertyParser import PropertyParser
from browser.browserconfiguration import BrowserConfiguration
from database.restconfiguration import RestConfiguration


class ConfigSave(object):
    def __init__(self, file_name, default_configuration):
        self.default_configuration = default_configuration
        self.file_name = file_name
        self.loaded_configuration = None
        self.root_section_name = "GIFT-Cloud Browser"
        self._load()

    def get_configuration(self):
        return self.configuration

    def _load(self):
        config = self.get_config_object()
        section_map = {}
        settings = config.options(self.root_section_name)
        for setting in settings:
            section_map[setting] = config.get(self.root_section_name, setting)
        config_object = RestConfiguration()
        config_object.server_name = ConfigSave.get_optional(section_map, 'server_name', self.default_configuration)
        config_object.base_url = ConfigSave.get_optional(section_map, 'url', self.default_configuration)
        config_object.user_name = ConfigSave.get_optional(section_map, 'user_name', self.default_configuration)
        config_object.password = ConfigSave.get_optional(section_map, 'password', self.default_configuration)
        self.configuration = config_object

    def save(self, configuration):
        config_file = open(self.file_name, 'w')

        root_section = "GIFT-Cloud Browser"
        config = self.get_config_object()
        if not config.has_section(self.root_section_name):
            config.add_section(self.root_section_name)
        config.set(root_section, 'server_name', configuration.server_name)
        config.set(root_section, 'url', configuration.base_url)
        config.set(root_section, 'user_name', configuration.user_name)
        config.set(root_section, 'password', configuration.password)
        config.write(config_file)

        config_file.close()

    @staticmethod
    def get_optional(map, property_name, default_map):
        if property_name in map:
            return map[property_name]
        else:
            return default_map[property_name]

    def load_from_properties(self):
        """
        Creates a new configuration object and attempts to read in values from an existing GiftCloudUploader properties file
        :return:
        """
        base = BrowserConfiguration.get_user_directory()
        properties_file = os.path.join(base, "GiftCloudUploader.properties")
        config = ConfigParser()
        config.add_section(self.root_section_name)
        if os.path.exists(properties_file):
            properties = PropertyParser(properties_file)
            self._set_if_exists(config, 'url', properties.properties, 'giftcloud_serverurl')
            self._set_if_exists(config, 'user_name', properties.properties, 'giftcloud_lastusername')
        return config

    def get_config_object(self):
        if self.loaded_configuration is None:

            if os.path.exists(self.file_name):
                self.loaded_configuration = self.load_from_ini_file()
            else:
                self.loaded_configuration = self.load_from_properties()

            # Ensure the application section exists
            if not self.loaded_configuration.has_section(self.root_section_name):
                self.loaded_configuration.add_section(self.root_section_name)

        return self.loaded_configuration

    def load_from_ini_file(self):
        config = ConfigParser()
        config.read(self.file_name)
        return config

    def _set_if_exists(self, config, config_name, properties, property_name):
        if property_name in properties:
            config.set(self.root_section_name, config_name, properties[property_name])

