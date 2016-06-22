# https://github.com/tomdoel/pyxnatbrowser
# Author: Tom Doel www.tomdoel.com
# Distributed under the Simplified BSD License.
import os

from database.base import Base
from database.utilities import Utilities


class XnatResource(Base):
    """ Describes an XNAT resource, which might for example be a collection of 2D images that together make up a volume
    """

    def __init__(self, rest_client, project_id, subject_id, session_id, scan_id, resource_label, file_count,
                 file_format):
        super().__init__()
        self.rest_client = rest_client
        self.project_id = project_id
        self.subject_id = subject_id
        self.session_id = session_id
        self.scan_id = scan_id
        self.resource_label = resource_label
        self.file_count = file_count
        self.file_format = file_format
        self.file_list = None

    @staticmethod
    def create_from_server_object(rest_client, server_object, project_id, subject_id, session_id, scan_id):
        resource_label = Utilities.get_optional_dict_value(server_object, 'label')
        file_count_str = Utilities.get_optional_dict_value(server_object, 'file_count')
        if not file_count_str:
            file_count = 0
        else:
            file_count = int(float(file_count_str))
        file_format = Utilities.get_optional_dict_value(server_object, 'format')
        return XnatResource(rest_client, project_id, subject_id, session_id, scan_id, resource_label, file_count,
                            file_format)

    def get_file_list(self):
        self._populate_file_list_if_necessary()
        return self.file_list

    def download_single_file(self, file_index, dir_name):
        self._populate_file_list_if_necessary()
        uri = self.file_list[file_index]['URI']
        file_name = os.path.basename(uri)
        full_file_name = os.path.join(dir_name, file_name)
        self.rest_client.download_single_file(full_file_name, uri)
        return full_file_name

    def download_scan_to_zip_file(self, zip_file):
        self.rest_client.download_scan_to_zip_file(zip_file, self.project_id, self.subject_id, self.session_id,
                                                   self.scan_id, self.resource_label)

    def _populate_file_list_if_necessary(self):
        if self.file_list is None:
            file_list = self.rest_client.get_file_list(self.project_id, self.subject_id, self.session_id, self.scan_id, self.resource_label)
            self.file_list = file_list['ResultSet']['Result']
