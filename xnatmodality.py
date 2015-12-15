# https://github.com/tomdoel/pyxnatbrowser
# Author: Tom Doel www.tomdoel.com
# Distributed under the Simplified BSD License.

from enum import Enum


class XnatModality(Enum):
    """ Enumeration describing XNAT compatible datatypes
    """

    MR = 0

    def __init__(self, value):
        if value == 0:
            self.Name = 'MR'
            self.XnatType = 'xnat:mrScanData'
        else:
            self.Name = None
            self.XnatType = None

    @staticmethod
    def get_modality_from_xnat_string(xnat_type):
        for enum in XnatModality:
            if xnat_type == enum.XnatType:
                return enum
        return None
