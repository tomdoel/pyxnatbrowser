# https://github.com/tomdoel/pyxnatbrowser
# Author: Tom Doel www.tomdoel.com
# Distributed under the Simplified BSD License.

from tkinter import PanedWindow, Menu
from tkinter.constants import BOTH
from tkinter import messagebox

from browser.labeledchecklistbox import LabeledCheckListBox
from browser.labeledlistbox import LabeledListBox, SelectedItems
from database.observable import Observable
from browser import __version__


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
    def __init__(self, parent, selected_projects, selected_subjects, selected_scans, unselected_scans, database):
        LabeledCheckListBox.__init__(self, parent, selected_scans, unselected_scans, 'Scan:')

        self.database = database
        self.selected_projects = selected_projects
        self.selected_subjects = selected_subjects
        selected_subjects.add_listener(self._subject_selection_changed)

    def _update_items(self, subject_list):
        scan_records = []
        self.database.clear_all_download_model_listeners()
        for subject in subject_list:
            session_map = subject.get_session_map()
            for session in session_map.values():
                scan_map = session.get_scan_map()
                for scan in scan_map.values():
                    scan_records.append(DynamicScanRecord(scan, subject.subject_label + ':' + scan.scan_id,
                                                          self.database.get_scan_download_model(subject.project_id,
                                                                                                subject.subject_id,
                                                                                                scan.scan_id)))
        self._update_list(scan_records)

    def _subject_selection_changed(self, value):
        self._update_items(value)


class DynamicScanRecord(Observable):
    def __init__(self, scan, subject_label, model):
        Observable.__init__(self)

        self.scan = scan
        self.label = subject_label
        self.model = model

    def get_number_of_downloaded_files(self):
        return self.model.get_number_of_downloaded_files()

    def get_number_of_server_files(self):
        return self.model.get_number_of_server_files()

    def is_checked(self):
        return self.model.is_downloaded_from_file_system()

    def is_checked_force_reload(self):
        self.model.force_cache_reload()
        return self.model.is_downloaded_from_file_system()

    def get_status(self):
        return self.model.status


class MainFrame:
    def __init__(self, root, database):
        self.root = root
        self.database = database
        self.selected_projects = SelectedItems()
        self.selected_subjects = SelectedItems()
        self.selected_scans = SelectedItems()
        self.unselected_scans = SelectedItems()

        master_paned_window = PanedWindow(root)
        master_paned_window.pack(fill=BOTH, expand=1)

        self.projects = ProjectList(master_paned_window, self.selected_projects, database)
        master_paned_window.add(self.projects)

        self.subjects = SubjectList(master_paned_window, self.selected_projects, self.selected_subjects, database)
        master_paned_window.add(self.subjects)

        self.scans = ScanList(master_paned_window, self.selected_projects, self.selected_subjects, self.selected_scans,
                              self.unselected_scans, database)
        master_paned_window.add(self.scans)

        self.selected_scans.add_listener(self._scan_selection_changed)
        self.unselected_scans.add_listener(self._scan_unselection_changed)

        # Create a menu
        root_menu = Menu(root)
        root.config(menu=root_menu)

        xnat_menu = Menu(root_menu)
        root_menu.add_cascade(label="GIFT-Cloud", menu=xnat_menu)

        xnat_menu.add_command(label="About", command=self.menu_about)
        xnat_menu.add_separator()
        xnat_menu.add_command(label="Settings", command=self.menu_settings)
        xnat_menu.add_separator()
        xnat_menu.add_command(label="Quit", command=self.menu_exit)

    def menu_exit(self):
        self.root.quit()

    def menu_about(self):
        messagebox.showinfo("GIFT-Cloud Downloader", "Version " + __version__)

    def menu_settings(self):
        messagebox.showinfo("GIFT-Cloud Downloader", "Settings")

    def _scan_selection_changed(self, scans):
        if len(scans) > 0:
            for scan in scans:
                if not self.database.is_scan_downloaded(scan.project_id, scan.subject_id, scan.scan_id):
                    self.database.download_scan(scan.project_id, scan.subject_id, scan.scan_id)

    def _scan_unselection_changed(self, scans):
        scans_to_remove = []
        for scan in scans:
            if self.database.is_scan_downloaded(scan.project_id, scan.subject_id, scan.scan_id):
                scans_to_remove.append(scan)

        if len(scans_to_remove) > 0:
            result = messagebox.askyesno("Delete downloaded scan",
                                         "Do you want to delete these scans from your computer?")
            if result:
                for scan in scans_to_remove:
                    self.database.delete_scan(scan.project_id, scan.subject_id, scan.scan_id)

        self.scans.refresh_checks()
