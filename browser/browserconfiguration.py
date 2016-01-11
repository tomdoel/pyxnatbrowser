# https://github.com/tomdoel/pyxnatbrowser
# Author: Tom Doel www.tomdoel.com
# Distributed under the Simplified BSD License.
import os


class BrowserConfiguration(object):

    @staticmethod
    def get_user_directory():
        if os.name == 'nt':
            return os.environ['USERPROFILE']
        else:
            return os.environ['HOME']

    @staticmethod
    def get_application_directory_name():
        return "GiftCloudBrowser"

    @staticmethod
    def get_application_directory_and_create_if_necessary():
        home_directory = BrowserConfiguration.get_user_directory()
        application_directory = os.path.join(home_directory, BrowserConfiguration.get_application_directory_name())
        if not os.path.exists(application_directory):
            os.makedirs(application_directory)
        return application_directory

    @staticmethod
    def get_properties_filename():
        application_directory = BrowserConfiguration.get_application_directory_and_create_if_necessary()
        return os.path.join(application_directory, 'GiftCloudBrowserProperties.ini')

