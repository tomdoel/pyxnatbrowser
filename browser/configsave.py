import os
from configparser import ConfigParser

from browser.PropertyParser import PropertyParser
from browser.browserconfiguration import BrowserConfiguration
from database.restconfiguration import RestConfiguration


class ConfigSave(object):
    def __init__(self, file_name, default_configuration):
        self.default_configuration = default_configuration
        self.file_name = file_name
        self.cached_file_configuration = None
        self.root_section_name = "GIFT-Cloud Browser"
        self.requires_save = False
        self._load()

    def get_configuration(self):
        return self.configuration

    def _load(self):
        config = self._get_cached_file_configuration()
        section_map = {}
        settings = config.options(self.root_section_name)
        for setting in settings:
            section_map[setting] = config.get(self.root_section_name, setting)
        config_object = RestConfiguration()
        config_object.server_name = ConfigSave._get_optional(section_map, 'server_name', self.default_configuration)
        config_object.base_url = ConfigSave._get_optional(section_map, 'url', self.default_configuration)
        config_object.user_name = ConfigSave._get_optional(section_map, 'user_name', self.default_configuration)
        config_object.password = ConfigSave._get_optional(section_map, 'password', self.default_configuration)
        self.configuration = config_object
        if self.requires_save:
            self.save()

    def save(self):
        config_file = open(self.file_name, 'w')

        cached_config = self._get_cached_file_configuration()
        if not cached_config.has_section(self.root_section_name):
            cached_config.add_section(self.root_section_name)
        cached_config.set(self.root_section_name, 'server_name', self.configuration.server_name)
        cached_config.set(self.root_section_name, 'url', self.configuration.base_url)
        cached_config.set(self.root_section_name, 'user_name', self.configuration.user_name)
        cached_config.set(self.root_section_name, 'password', self.configuration.password)
        cached_config.write(config_file)

        config_file.close()
        self.requires_save = False

    @staticmethod
    def _get_optional(map, property_name, default_map):
        if property_name in map:
            return map[property_name]
        else:
            return default_map[property_name]

    def _get_cached_file_configuration(self):
        if self.cached_file_configuration is None:

            if os.path.exists(self.file_name):
                self.cached_file_configuration = self._load_from_ini_file()
            else:
                self.cached_file_configuration = self._load_from_properties()
                self.requires_save = True

            # Ensure the application section exists
            if not self.cached_file_configuration.has_section(self.root_section_name):
                self.cached_file_configuration.add_section(self.root_section_name)

        return self.cached_file_configuration

    def _load_from_ini_file(self):
        config = ConfigParser()
        config.read(self.file_name)
        return config

    def _set_if_exists(self, config, config_name, properties, property_name):
        if property_name in properties:
            config.set(self.root_section_name, config_name, properties[property_name])

    def _load_from_properties(self):
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
