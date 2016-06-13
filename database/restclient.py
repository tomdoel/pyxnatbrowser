# https://github.com/tomdoel/pyxnatbrowser
# Author: Tom Doel www.tomdoel.com
# Distributed under the Simplified BSD License.

import json

import shutil
import urllib
from urllib.request import HTTPPasswordMgrWithDefaultRealm

from database.xnatproject import XnatProject
from database.xnatresource import XnatResource
from database.xnatnatscan import XnatNatScan
from database.xnatsession import XnatSession
from database.xnatsubject import XnatSubject
from database.restconfiguration import RestConfiguration


class RestClient:
    def __init__(self, config=RestConfiguration()):
        self.config = config
        self.session_cookie = None
        self.authenticated_base_url = None

        if not isinstance(config, RestConfiguration):
            raise TypeError("The rest client config object must be of type RestConfig")

    def get_project_map(self):
        struct_from_server = self._request_json('REST/projects?format=json&owner=true&member=true')
        project_map = {}

        if len(struct_from_server) > 0:
            object_list = struct_from_server['ResultSet']['Result']

            for object_from_server in object_list:
                new_project = XnatProject.create_from_server_object(self, object_from_server)
                project_map[new_project.project_id] = new_project

        return project_map

    def get_subject_map(self, project_id):

        struct_from_server = self._request_json('REST/projects/' + project_id + '/subjects?format=json&columns=DEFAULT')
        subject_map = {}

        if len(struct_from_server) > 0:
            object_list = struct_from_server['ResultSet']['Result']

            for server_object in object_list:
                new_subject = XnatSubject.create_from_server_object(self, server_object)
                subject_map[new_subject.subject_id] = new_subject

        return subject_map

    def get_session_map(self, project_id, subject_id):

        struct_from_server = self._request_json(
            'REST/projects/' + project_id + '/subjects/' + subject_id + '/experiments?format=json')
        session_map = {}

        if len(struct_from_server) > 0:
            object_list = struct_from_server['ResultSet']['Result']
            for server_object in object_list:
                new_session = XnatSession.create_from_server_object(self, server_object, subject_id)
                session_map[new_session.session_id] = new_session

        return session_map

    def get_scan_map(self, project_id, subject_id, session_id):

        struct_from_server = self._request_json(
            'REST/projects/' + project_id + '/subjects/' + subject_id + '/experiments/' + session_id +
            '/scans?format=json')
        scan_map = {}

        if len(struct_from_server) > 0:
            object_list = struct_from_server['ResultSet']['Result']
            for server_object in object_list:
                new_scan = XnatNatScan.create_from_server_object(self, server_object, project_id, subject_id,
                                                                 session_id)
                scan_map[new_scan.scan_id] = new_scan
        return scan_map

    def get_resource_list(self, project_id, subject_id, session_id, scan_id):

        struct_from_server = self._request_json(
            'REST/projects/' + project_id + '/subjects/' + subject_id + '/experiments/' + session_id + '/scans/' +
            scan_id + '/resources?format=json')
        resource_list = []

        if len(struct_from_server) > 0:
            object_list = struct_from_server['ResultSet']['Result']
            for server_object in object_list:
                resource_list.append(
                    XnatResource.create_from_server_object(self, server_object, project_id, subject_id, session_id,
                                                           scan_id))

        return resource_list

    def download_scan_to_zip_file(self, zip_file_name, project_id, subject_id, session_id, scan_id, resource_id):
        self._request_and_save_file(zip_file_name,
                                    'REST/projects/' + project_id + '/subjects/' + subject_id + '/experiments/' +
                                    session_id + '/scans/' + scan_id + '/resources/' + resource_id +
                                    '/files?format=zip')

    def get_subject_label_from_pseudoname(self, project_id, pseudoname):
        return_object = self._request_json(
            'REST/projects/' + project_id + '/pseudonyms/' + pseudoname + '?format=json&owner=true&member=true')

        if return_object is None:
            return None
        else:
            return return_object.items.data_fields.label

    def generate_preview_image(self, project_id, session_id):
        self._post_request(
            'data/projects/' + project_id + '/pipelines/WebBasedQCImageCreator/experiments/' + session_id)
        return None

    def get_preview_image(self, session_id, scan_id):
        try:
            return_object = self._request_file(
                'REST/experiments/' + session_id + '/scans/' + scan_id + '/resources/SNAPSHOTS/files?file_content=ORIGINAL&index=0')
        except urllib.error.HTTPError as err:
            if err.code == 404:
                return None
            else:
                raise

        if return_object is None:
            return None
        else:
            return return_object

    def _request_json(self, url):
        return self._request(url + '&MediaType=application/json&ContentType=json')

    def _request(self, url):
        if self.session_cookie is None:
            self._force_authentication()

        full_url = self.authenticated_base_url + url
        headers = {
            'Cookie': 'JSESSIONID=' + self.session_cookie
        }
        request = urllib.request.Request(full_url, None, headers)
        response = urllib.request.urlopen(request).read().decode('utf-8')
        return json.loads(response)

    def _request_file(self, url):
        if self.session_cookie is None:
            self._force_authentication()

        full_url = self.authenticated_base_url + url
        headers = {
            'Cookie': 'JSESSIONID=' + self.session_cookie
        }
        request = urllib.request.Request(full_url, None, headers)
        response = urllib.request.urlopen(request).read()
        return response

    def _post_request(self, url):
        if self.session_cookie is None:
            self._force_authentication()

        full_url = self.authenticated_base_url + url
        headers = {
            'Cookie': 'JSESSIONID=' + self.session_cookie
        }
        request = urllib.request.Request(full_url, None, headers, None, None, 'POST')
        response = urllib.request.urlopen(request).read().decode('utf-8')
        return response

    def _request_and_save_file(self, zip_file_name, url):

        if self.session_cookie is None:
            self._force_authentication()

        full_url = self.authenticated_base_url + url
        headers = {
            'Cookie': 'JSESSIONID=' + self.session_cookie
        }
        request = urllib.request.Request(full_url, None, headers)

        # Download the zip file and save it to a local file
        with urllib.request.urlopen(request) as response, open(zip_file_name, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)

    def _force_authentication(self):

        base_url = self.config.base_url.strip()
        if not base_url.endswith('/'):
            base_url += '/'

        url = base_url + 'data/JSESSION'

        # create a password manager
        password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
        password_mgr.add_password(None, base_url, self.config.user_name, self.config.password)
        handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
        opener = urllib.request.build_opener(handler)

        self.session_cookie = opener.open(url).read().decode('utf-8')
        self.authenticated_base_url = base_url
