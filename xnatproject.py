# https://github.com/tomdoel/pyxnatbrowser
# Author: Tom Doel www.tomdoel.com
# Distributed under the Simplified BSD License.

from base import Base
from utilities import Utilities


class XnatProject(Base):
    """ Describes an XNAT project
    """

    def __init__(self, rest_client, name, project_id, secondary_id, description):
        super().__init__()

        self.rest_client = rest_client
        self.name = name
        self.project_id = project_id
        self.secondary_id = secondary_id
        self.description = description
        self.subject_map = None

    @staticmethod
    def create_from_server_object(rest_client, server_object):
        name = Utilities.get_optional_dict_value(server_object, 'name')
        project_id = Utilities.get_optional_dict_value(server_object, 'id')
        secondary_id = Utilities.get_optional_dict_value(server_object, 'secondary_id')
        description = Utilities.get_optional_dict_value(server_object, 'description')
        return XnatProject(rest_client, name, project_id, secondary_id, description)

    def get_subject_map(self):
        self._populate_subject_map_if_necessary()
        return self.subject_map

    def get_subject(self, patient_id):
        if patient_id is None:
            return None

        self._populate_subject_map_if_necessary()

        if ~self.subject_map.hasKey(patient_id):
            return None
        else:
            return self.subject_map[patient_id]

    def get_resource_for_series_uid(self, patient_id, series_uid):
        subject = self.get_subject(patient_id)
        if subject is not None:
            scan = subject.find_scan(series_uid)
            if scan is not None:
                resources = scan.get_resources()
                if len(resources) > 0:
                    resource = resources(1)
                    return resource

        resource = None
        return resource

    def _populate_subject_map_if_necessary(self):
        if self.subject_map is None:
            self.subject_map = self.rest_client.get_subject_map(self.project_id)
