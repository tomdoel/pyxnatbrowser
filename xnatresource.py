# https://github.com/tomdoel/pyxnatbrowser
# Author: Tom Doel www.tomdoel.com
# Distributed under the Simplified BSD License.

from base import Base
from utilities import Utilities


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

    @staticmethod
    def create_from_server_object(rest_client, server_object, project_id, subject_id, session_id, scan_id):
        resource_label = Utilities.get_optional_dict_value(server_object, 'label')
        file_count = int(float(Utilities.get_optional_dict_value(server_object, 'file_count')))
        file_format = Utilities.get_optional_dict_value(server_object, 'format')
        return XnatResource(rest_client, project_id, subject_id, session_id, scan_id, resource_label, file_count,
                            file_format)

    def download_scan_to_zip_file(self, zip_file):
        self.rest_client.download_scan_to_zip_file(zip_file, self.project_id, self.subject_id, self.session_id,
                                                   self.scan_id, self.resource_label)
