#!/usr/bin/python
from browser.browser import Browser
from testpyxnat.fakerestclientfactory import FakeRestClientFactory

default_config = {}
default_config['server_name'] = 'Fake server'
default_config['base_url'] = 'https://fake-server.com'
default_config['user_name'] = 'fake-username'
default_config['password'] = 'fake-password'
app = Browser(default_config, FakeRestClientFactory(), "Fake Browser")


