# https://github.com/tomdoel/pyxnatbrowser
# Author: Tom Doel www.tomdoel.com
# Distributed under the Simplified BSD License.

from base import Base
from utilities import Utilities


class XnatSession(Base):
    """ Describes an XNAT subject
    """

    def __init__(self, rest_client, project_id, subject_label, label, session_id):
        super().__init__()
        self.rest_client = rest_client
        self.scan_map = None
        self.project_id = project_id
        self.subject_label = subject_label
        self.label = label
        self.session_id = session_id

    @staticmethod
    def create_from_server_object(rest_client, server_object, project_id, subject_label):
        label = Utilities.get_optional_dict_value(server_object, 'label')
        session_id = Utilities.get_optional_dict_value(server_object, 'ID')
        return XnatSession(rest_client, project_id, subject_label, label, session_id)

    def get_scan_map(self):
        self._populate_scan_map_if_necessary()
        return self.scan_map

    def count_scans(self):
        self._populate_scan_map_if_necessary()
        return self.scan_map.Count

    def _populate_scan_map_if_necessary(self):
        if self.scan_map is None:
            self.scan_map = self.rest_client.get_scan_map(self.project_id, self.subject_label, self.label)
