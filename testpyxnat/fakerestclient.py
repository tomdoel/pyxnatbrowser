# https://github.com/tomdoel/pyxnatbrowser
# Author: Tom Doel www.tomdoel.com
# Distributed under the Simplified BSD License.

from database.xnatnatscan import XnatNatScan
from database.xnatproject import XnatProject
from database.xnatresource import XnatResource
from database.xnatsession import XnatSession
from database.xnatsubject import XnatSubject


class FakeRestClient:
    def get_project_map(self):
        project_map = {}
        for project_number in [1, 2, 3]:
            project_map['Project_ID_' + str(project_number)] = XnatProject(self, "Project_ID_" + str(project_number), "Project_Name_" + str(project_number), "Project_Secondary_ID_" + str(project_number), "Project_Description_" + str(project_number))
        return project_map

    def get_subject_map(self, project_id):
        subject_map = {}
        prefix = "P" + project_id + "_"
        for subject_number in [1, 2, 3]:
            subject_map["Subject_ID_" + str(str(subject_number))] = XnatSubject(self, project_id, prefix + "Subject_ID_" + str(subject_number), prefix + "Subject_Label_" + str(subject_number))
        return subject_map

    def get_session_map(self, project_id, subject_id):
        session_map = {}
        prefix = "P" + project_id + "_" + "S" + subject_id + "_"
        for session_number in [1, 2, 3]:
            session_map[prefix + "Session_ID_" + str(session_number)] = XnatSession(self, project_id, subject_id, prefix + "Session_ID_" + str(session_number), prefix + "Subject_Label_" + str(session_number))
        return session_map

    def get_scan_map(self, project_id, subject_id, session_id):
        scan_map = {}
        prefix = "P" + project_id + "_" + "S" + subject_id + "_" + "S" + session_id + "_"
        for scan_number in [1, 2, 3]:
            scan_map[prefix + "Scan_ID_" + str(scan_number)] = XnatNatScan(self, project_id, subject_id, session_id, prefix + "Scan_ID_" + str(scan_number), "MR")
        return scan_map

    def get_resource_list(self, project_id, subject_id, session_id, scan_id):
        resource_list = []
        resource_list.append(XnatResource(self, project_id, subject_id, session_id, scan_id, "DICOM", 10, "FORMAT"))
        return resource_list

    def download_scan_to_zip_file(self, zip_file_name, project_id, subject_id, session_id, scan_id, resource_id):
        None

    def get_subject_label_from_pseudoname(self, project_id, pseudoname):
        return project_id + "_PPID_" + pseudoname


