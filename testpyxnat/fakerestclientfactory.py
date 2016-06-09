# https://github.com/tomdoel/pyxnatbrowser
# Author: Tom Doel www.tomdoel.com
# Distributed under the Simplified BSD License.

from testpyxnat.fakerestclient import FakeRestClient


class FakeRestClientFactory:
    @staticmethod
    def create_rest_client(config):
        return FakeRestClient()
