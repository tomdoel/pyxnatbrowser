# https://github.com/tomdoel/pyxnatbrowser
# Author: Tom Doel www.tomdoel.com
# Distributed under the Simplified BSD License.

class RestConfiguration(object):

    def __init__(self):
        self.__applicationDirectory = None
        self.__serverName = None
        self.__baseUrl = None
        self.__userName = None
        self.__password = None

    @property
    def base_url(self):
        return self.__baseUrl

    @base_url.setter
    def base_url(self, value):
        self.__baseUrl = value

    @property
    def server_name(self):
        return self.__serverName

    @server_name.setter
    def server_name(self, value):
        self.__serverName = value

    @property
    def user_name(self):
        return self.__userName

    @user_name.setter
    def user_name(self, value):
        self.__userName = value

    @property
    def application_directory(self):
        return self.__applicationDirectory

    @application_directory.setter
    def application_directory(self, value):
        self.__applicationDirectory = value

    @property
    def password(self):
        return self.__password

    @password.setter
    def password(self, value):
        self.__password = value
