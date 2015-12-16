# https://github.com/tomdoel/pyxnatbrowser
# Author: Tom Doel www.tomdoel.com
# Distributed under the Simplified BSD License.

from tkinter import PanedWindow
from tkinter.constants import BOTH
from tkinter import messagebox

from labeledchecklistbox import LabeledCheckListBox
from labeledlistbox import LabeledListBox, SelectedItems


class ProjectList(LabeledListBox):
    def __init__(self, parent, selected_projects, xnat_database):
        LabeledListBox.__init__(self, parent, selected_projects, 'Project:')
        self.xnat_database = xnat_database
        self.selected_projects = selected_projects
        self.project_map = {}
        self._update_items()

    def _update_items(self):
        self.project_map = self.xnat_database.get_project_map()
        project_list = []
        project_text = []
        for project in self.project_map.values():
            project_list.append(project)
            project_text.append(project.project_name)
        self._update_list(project_list, project_text)


class SubjectList(LabeledListBox):
    def __init__(self, parent, selected_projects, selected_subjects, mat_nat_database):
        LabeledListBox.__init__(self, parent, selected_subjects, 'Subject:')
        self.mat_nat_database = mat_nat_database
        self.selected_projects = selected_projects
        self.selected_subjects = selected_subjects
        selected_projects.add_listener(self._project_selection_changed)

    def _update_items(self, project_list):
        visible_subjects = []
        visible_subjects_labels = []
        for project in project_list:
            subject_map = project.get_subject_map()
            for subject in subject_map.values():
                visible_subjects.append(subject)
                visible_subjects_labels.append(project.project_name + ':' + subject.subject_label)
        self._update_list(visible_subjects, visible_subjects_labels)

    def _project_selection_changed(self, value):
        self._update_items(value)


class ScanList(LabeledCheckListBox):
    def __init__(self, parent, selected_projects, selected_subjects, selected_scans, mat_nat_database):
        LabeledCheckListBox.__init__(self, parent, selected_scans, 'Scan:')
        self.mat_nat_database = mat_nat_database
        self.selected_projects = selected_projects
        self.selected_subjects = selected_subjects
        selected_subjects.add_listener(self._subject_selection_changed)

    def _update_items(self, subject_list):
        visible_scans = []
        visible_scans_labels = []
        for subject in subject_list:
            session_map = subject.get_session_map()
            for session in session_map.values():
                scan_map = session.get_scan_map()
                for scan in scan_map.values():
                    visible_scans.append(scan)
                    visible_scans_labels.append(subject.subject_label + ':' + scan.scan_id)
        self._update_list(visible_scans, visible_scans_labels)

    def _subject_selection_changed(self, value):
        self._update_items(value)


class MainFrame:
    def __init__(self, root, database):
        self.database = database
        self.selected_projects = SelectedItems()
        self.selected_subjects = SelectedItems()
        self.selected_scans = SelectedItems()

        master_paned_window = PanedWindow(root)
        master_paned_window.pack(fill=BOTH, expand=1)

        self.projects = ProjectList(master_paned_window, self.selected_projects, database)
        master_paned_window.add(self.projects)

        self.subjects = SubjectList(master_paned_window, self.selected_projects, self.selected_subjects, database)
        master_paned_window.add(self.subjects)

        self.scans = ScanList(master_paned_window, self.selected_projects, self.selected_subjects, self.selected_scans,
                              database)
        master_paned_window.add(self.scans)

        self.selected_scans.add_listener(self._scan_selection_changed)

    def _scan_selection_changed(self, scans):
        if len(scans) > 0:
            result = messagebox.askyesno("Download scan", "Do you want to download these scan?")
            if result:
                for scan in scans:
                    self.database.download_scan(scan.project_id, scan.subject_id, scan.scan_id)
