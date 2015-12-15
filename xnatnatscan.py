# https://github.com/tomdoel/pyxnatbrowser
# Author: Tom Doel www.tomdoel.com
# Distributed under the Simplified BSD License.

from base import Base
from xnatmodality import XnatModality
from utilities import Utilities


class XnatNatScan(Base):
    """ Describes an XNAT scan, which might for example be a series of images, packaged as a resource
    """

    def __init__(self, rest_client, project_id, subject_label, session_label, id_tag, modality):
        super().__init__()
        self.rest_client = rest_client
        self.project_id = project_id
        self.subject_label = subject_label
        self.session_label = session_label
        self.scan_id = id_tag
        self.modality = modality

    @staticmethod
    def create_from_server_object(rest_client, server_object, project_id, subject_label, session_label):
        id_tag = Utilities.get_optional_property(server_object, 'ID')
        modality = XnatModality.get_modality_from_xnat_string(
                Utilities.get_optional_property(server_object, 'xsiType'))
        return XnatNatScan(rest_client, project_id, subject_label, session_label, id_tag, modality)

    def get_resources(self):
        self._populate_resource_list_if_necessary()
        return self.resource_list

    def count_images(self):
        self._populate_resource_list_if_necessary()
        number_of_images = 0
        for resource in self.resource_list:
            number_of_images = number_of_images + resource.FileCount
        return number_of_images

    def _populate_resource_list_if_necessary(self):
        if self.resource_list is None:
            self.resource_list = self.rest_client.get_resource_list(self.project_id, self.subject_label,
                                                                    self.session_label,
                                                                    self.scan_id)
