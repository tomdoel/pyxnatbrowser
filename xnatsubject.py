# https://github.com/tomdoel/pyxnatbrowser
# Author: Tom Doel www.tomdoel.com
# Distributed under the Simplified BSD License.

from base import Base
from utilities import Utilities


class XnatSubject(Base):
    """ Describes an XNAT subject
    """

    def __init__(self, rest_client, project_id, subject_id, subject_label):
        super().__init__()
        self.rest_client = rest_client
        self.session_map = None
        self.project_id = project_id
        self.subject_id = subject_id
        self.subject_label = subject_label

    @staticmethod
    def create_from_server_object(rest_client, server_object):
        project_id = Utilities.get_optional_dict_value(server_object, 'project')
        subject_id = Utilities.get_optional_dict_value(server_object, 'ID')
        subject_label = Utilities.get_optional_dict_value(server_object, 'label')
        return XnatSubject(rest_client, project_id, subject_id, subject_label)

    def get_session_map(self):
        self._populate_session_map_if_necessary()
        return self.session_map

    def find_scan(self, scan_id):
        self._populate_session_map_if_necessary()
        for session in self.session_map.values():
            for scan in session.get_scan_map().values():
                if scan.scan_id == scan_id:
                    return scan
        return None

    def count_scans(self):
        self._populate_session_map_if_necessary()
        scan_count = 0
        for session in self.session_map.values():
            scan_count = scan_count + session.count_scans
        return scan_count
        
    def _populate_session_map_if_necessary(self):
        if self.session_map is None:
            self.session_map = self.rest_client.get_session_map(self.project_id, self.subject_id)
