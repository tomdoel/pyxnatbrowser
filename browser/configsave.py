import os
from configparser import ConfigParser

from database.restconfiguration import RestConfiguration


class ConfigSave(object):
    def __init__(self, file_name, default_configuration):
        self.default_configuration = default_configuration
        self.file_name = file_name

    def load(self):
        config_object = RestConfiguration()
        if not os.path.exists(self.file_name):
            section_map = {}
        else:
            config_file = open(self.file_name, 'r')
            root_section = "GIFT-Cloud Browser"
            config = ConfigParser.ConfigParser()
            section_map = config.read(root_section)
            config_file.close()
        config_object.server_name = ConfigSave.get_optional(section_map, 'server_name', self.default_configuration)
        config_object.base_url = ConfigSave.get_optional(section_map, 'base_url', self.default_configuration)
        config_object.user_name = ConfigSave.get_optional(section_map, 'user_name', self.default_configuration)
        config_object.password = ConfigSave.get_optional(section_map, 'password', self.default_configuration)
        return config_object

    def save(self, configuration):
        config_file = open(self.file_name, 'w')

        root_section = "GIFT-Cloud Browser"
        config = ConfigParser()
        config.add_section(root_section)
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
