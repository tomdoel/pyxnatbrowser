# https://github.com/tomdoel/pyxnatbrowser
# Author: Tom Doel www.tomdoel.com
# Distributed under the Simplified BSD License.

import os
import tempfile
import uuid
import zipfile

import shutil


class XnatDatabase(object):

    def __init__(self, rest_client, config):
        self.config = config
        self.rest_client = rest_client
        self.project_map = None

    def get_project_map(self):
        self._populate_project_map_if_necessary()
        return self.project_map
        
    def get_project(self, project_id):
        self._populate_project_map_if_necessary()
        if project_id in self.project_map.keys():
            return self.project_map[project_id]
        else:
            return None

    def download_scan(self, project_id, subject_id, scan_id):
        project = self.get_project(project_id)

        if project is not None:
            resource = project.get_resource_for_series_uid(subject_id, scan_id)

            uid = uuid.uuid4()

            temp_dir = XnatDatabase.get_temp_dir()

            zip_dir = os.path.join(temp_dir, 'zipped')
            if not os.path.exists(zip_dir):
                os.makedirs(zip_dir)

            unzip_dir = os.path.join(temp_dir, 'unzipped')
            if not os.path.exists(unzip_dir):
                os.makedirs(unzip_dir)

            zip_file_name = os.path.join(zip_dir, str(uid) + '.zip')

            # download a zip file containing the scan files
            resource.download_scan_to_zip_file(zip_file_name)
            z = zipfile.ZipFile(zip_file_name, "r")

            # Extract the zip file into a temporary folder
            unzipped_file_names = [os.path.join(unzip_dir, file_name) for file_name in z.namelist()]
            z.extractall(unzip_dir)

            # Remove the downloaded zip file
            os.remove(zip_file_name)
            os.rmdir(zip_dir)

            scan_directory = self.get_scan_directory(self.config.server_name, project_id, subject_id, scan_id)

            # Move the files to the local database
            for file_name in unzipped_file_names:
                head, tail = os.path.split(file_name)
                if not os.path.exists(os.path.join(scan_directory, tail)):
                    shutil.move(file_name, scan_directory)

            # Remove any remaining files and directories
            shutil.rmtree(temp_dir)

    def get_application_directory_and_create_if_necessary(self):
        home_directory = XnatDatabase.get_user_directory()
        application_directory = os.path.join(home_directory, self.config.application_directory)
        if not os.path.exists(application_directory):
            os.makedirs(application_directory)
        return application_directory

    def get_data_directory_and_create_if_necessary(self):
        application_directory = self.get_application_directory_and_create_if_necessary()
        data_directory = os.path.join(application_directory, 'Data')
        if not os.path.exists(data_directory):
            os.makedirs(data_directory)
        return data_directory

    def get_scan_directory(self, server_name, project_id, subject_id, scan_id):
        data_directory = self.get_data_directory_and_create_if_necessary()
        scan_directory = os.path.join(data_directory, server_name, project_id, subject_id, scan_id)
        if not os.path.exists(scan_directory):
            os.makedirs(scan_directory)
        return scan_directory
                      
    def _populate_project_map_if_necessary(self):
        if self.project_map is None:
            self.project_map = self.rest_client.get_project_map()

    @staticmethod
    def get_temp_dir():
        """
        Creates a temporary directory; the caller must delete this directory
        :return:
        """
        return tempfile.mkdtemp()

    @staticmethod
    def get_user_directory():
        if os.name == 'nt':
            return os.environ['USERPROFILE']
        else:
            return os.environ['HOME']
