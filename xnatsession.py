# https://github.com/tomdoel/pyxnatbrowser
# Author: Tom Doel www.tomdoel.com
# Distributed under the Simplified BSD License.

from base import Base
from utilities import Utilities


class XnatSession(Base):
    """ Describes an XNAT subject
    """

    def __init__(self, rest_client, project_id, subject_id, session_id, session_label):
        super().__init__()
        self.rest_client = rest_client
        self.scan_map = None
        self.project_id = project_id
        self.subject_id = subject_id
        self.session_id = session_id
        self.session_label = session_label

    @staticmethod
    def create_from_server_object(rest_client, server_object, subject_id):
        project_id = Utilities.get_optional_dict_value(server_object, 'project')
        session_id = Utilities.get_optional_dict_value(server_object, 'ID')
        session_label = Utilities.get_optional_dict_value(server_object, 'label')
        return XnatSession(rest_client, project_id, subject_id, session_id, session_label)

    def get_scan_map(self):
        self._populate_scan_map_if_necessary()
        return self.scan_map

    def count_scans(self):
        self._populate_scan_map_if_necessary()
        return self.scan_map.Count

    def _populate_scan_map_if_necessary(self):
        if self.scan_map is None:
            self.scan_map = self.rest_client.get_scan_map(self.project_id, self.subject_id, self.session_id)
