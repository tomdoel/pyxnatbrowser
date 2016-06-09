# https://github.com/tomdoel/pyxnatbrowser
# Author: Tom Doel www.tomdoel.com
# Distributed under the Simplified BSD License.

from database.restclient import RestClient


class RestClientFactory:
    @staticmethod
    def create_rest_client(config):
        return RestClient(config)
