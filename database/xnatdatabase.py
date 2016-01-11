# https://github.com/tomdoel/pyxnatbrowser
# Author: Tom Doel www.tomdoel.com
# Distributed under the Simplified BSD License.

import os
import tempfile
import uuid
import zipfile

import shutil
from enum import Enum

from database.observable import Observable


class XnatDatabase(object):
    def __init__(self, rest_client, config, application_folder):
        self.application_folder = application_folder
        self.config = config
        self.rest_client = rest_client
        self.project_map = None
        self.downloaded_cache = {}

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
            # Get the download status cache
            if project_id not in self.downloaded_cache:
                self.downloaded_cache[project_id] = {}
            if subject_id not in self.downloaded_cache[project_id]:
                self.downloaded_cache[project_id][subject_id] = {}
            if scan_id not in self.downloaded_cache[project_id][subject_id]:
                self.downloaded_cache[project_id][subject_id][scan_id] = ScanCacheRecord(self, self.config.server_name,
                                                                                         project_id, subject_id,
                                                                                         scan_id)

            status_cache = self.downloaded_cache[project_id][subject_id][scan_id]
            status_cache.set_downloading()

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

            # Update the cache
            status_cache.set_downloaded()

    def delete_scan(self, project_id, subject_id, scan_id):
        scan_directory = self.get_scan_directory(self.config.server_name, project_id, subject_id, scan_id)
        shutil.rmtree(scan_directory)
        XnatDatabase.remove_empty_directories(self.get_data_directory_and_create_if_necessary())

    def get_application_directory_and_create_if_necessary(self):
        if not os.path.exists(self.application_folder):
            os.makedirs(self.application_folder)
        return self.application_folder

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

    def is_scan_downloaded(self, project_id, subject_id, scan_id):

        if project_id not in self.downloaded_cache:
            self.downloaded_cache[project_id] = {}
        if subject_id not in self.downloaded_cache[project_id]:
            self.downloaded_cache[project_id][subject_id] = {}
        if scan_id not in self.downloaded_cache[project_id][subject_id]:
            self.downloaded_cache[project_id][subject_id][scan_id] = ScanCacheRecord(self, self.config.server_name,
                                                                                     project_id, subject_id,
                                                                                     scan_id)

        return self.downloaded_cache[project_id][subject_id][scan_id].is_downloaded_from_file_system()

    def get_scan_download_model(self, project_id, subject_id, scan_id):

        if project_id not in self.downloaded_cache:
            self.downloaded_cache[project_id] = {}
        if subject_id not in self.downloaded_cache[project_id]:
            self.downloaded_cache[project_id][subject_id] = {}
        if scan_id not in self.downloaded_cache[project_id][subject_id]:
            self.downloaded_cache[project_id][subject_id][scan_id] = ScanCacheRecord(self, self.config.server_name,
                                                                                     project_id, subject_id,
                                                                                     scan_id)

        return self.downloaded_cache[project_id][subject_id][scan_id]

    def clear_all_download_model_listeners(self):
        for project_caches in self.downloaded_cache.values():
            for subject_caches in project_caches.values():
                for scan_cache in subject_caches.values():
                    scan_cache.clear_all()

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
    def remove_empty_directories(base_path):
        if not os.path.isdir(base_path):
            return

        file_names = os.listdir(base_path)
        if len(file_names) == 0:
            os.rmdir(base_path)
        else:
            for file_name in file_names:
                full_file_name = os.path.join(base_path, file_name)
                if os.path.isdir(full_file_name):
                    XnatDatabase.remove_empty_directories(full_file_name)


class ScanCacheRecord(Observable):
    def __init__(self, database, server_name, project_id, subject_id, scan_id):
        Observable.__init__(self)
        self.scan_id = scan_id
        self.subject_id = subject_id
        self.server_name = server_name
        self.database = database
        self.project_id = project_id
        self.cached_num_local_files = None
        self.cached_num_resource_files = None
        self.status = ProgressStatus.undefined
        self._compute_cache_values_if_undefined()

    def get_number_of_server_files(self):
        if self.cached_num_resource_files is None:
            self._populate_num_server_files()
        return self.cached_num_resource_files

    def get_number_of_downloaded_files(self):
        if self.cached_num_local_files is None:
            self._populate_num_local_files()
        return self.cached_num_local_files

    def is_downloaded_from_file_system(self):
        self._compute_cache_values_if_undefined()
        return self.cached_num_local_files >= self.cached_num_resource_files

    def force_cache_reload(self):
        self._populate_num_server_files()
        self._populate_num_local_files()

    def set_downloading(self):
        if self.status is not ProgressStatus.in_progress:
            self.status = ProgressStatus.in_progress
            self._notify(self.status)

    def set_downloaded(self):
        if self.status is not ProgressStatus.complete:
            self._populate_num_local_files()
            self.status = ProgressStatus.complete
            self._notify(self.status)

    def _compute_cache_values_if_undefined(self):
        if self.cached_num_resource_files is None:
            self._populate_num_server_files()
        if self.cached_num_local_files is None:
            self._populate_num_local_files()

    def _populate_num_server_files(self):
        project = self.database.get_project(self.project_id)

        if project is None:
            self.cached_num_resource_files = None
            return

        resource = project.get_resource_for_series_uid(self.subject_id, self.scan_id)
        if resource is None:
            self.cached_num_resource_files = 0
        else:
            self.cached_num_resource_files = resource.file_count

    def _populate_num_local_files(self):
        data_directory = self.database.get_data_directory_and_create_if_necessary()
        scan_directory = os.path.join(data_directory, self.server_name, self.project_id, self.subject_id, self.scan_id)
        if not os.path.exists(scan_directory):
            self.cached_num_local_files = 0
            return

        # Get file list excluding system files
        file_names = [f for f in os.listdir(scan_directory) if not f.startswith('.')]
        self.cached_num_local_files = len(file_names)

    def _update_status(self):
        if self.is_downloaded_from_file_system():
            new_state = ProgressStatus.complete
        elif self.status == ProgressStatus.in_progress:
            new_state = ProgressStatus.in_progress
        else:
            new_state = ProgressStatus.not_started

        if self.status is not new_state:
            self.status = new_state
            self._notify(self.status)


class ProgressStatus(Enum):
    not_started = 0
    in_progress = 1
    complete = 2
    undefined = 3
