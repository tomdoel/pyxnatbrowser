# https://github.com/tomdoel/pyxnatbrowser
# Author: Tom Doel www.tomdoel.com
# Distributed under the Simplified BSD License.

from observable import Observable


class Base(Observable):

    def __init__(self):
        super(Observable, self).__init__()
