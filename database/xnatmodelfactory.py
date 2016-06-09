from tkinter import messagebox

from browser.labeledlistbox import ListModel, SelectedItemsModel
from browser.progresslistbox import ProgressListBoxModelFactory
from database.observable import Observable


class XnatModelFactory:
    def __init__(self, database):
        self.project_list_model = ProjectListModel(database)
        self.subject_list_model = SubjectListModel(self.project_list_model, database)
        self.scan_list_model = ScanListModel(self.project_list_model, self.subject_list_model, database)


class ProjectListModel(ListModel):
    def __init__(self, xnat_database):
        ListModel.__init__(self)
        self.xnat_database = xnat_database
        self.project_map = {}
        # try:
        self._update_items()
        # except:
        #     print("Error contacting the server.")

    def _update_items(self):
        self.project_map = self.xnat_database.get_project_map()
        project_list = []
        project_text = []
        for project in self.project_map.values():
            project_list.append(project)
            project_text.append(project.project_name)
        self.list_items_model.set_list_values(project_list, project_text)


class SubjectListModel(ListModel):
    def __init__(self, project_model, xnat_database):
        ListModel.__init__(self)
        self.xnat_database = xnat_database
        project_model.list_items_model.add_listener(self._project_list_changed)
        project_model.selected_items_model.add_listener(self._project_selection_changed)

    def _update_items(self, project_list):
        visible_subjects = []
        visible_subjects_labels = []
        for project in project_list:
            subject_map = project.get_subject_map()
            for subject in subject_map.values():
                visible_subjects.append(subject)
                visible_subjects_labels.append(project.project_name + ':' + subject.subject_label)
        self.list_items_model.set_list_values(visible_subjects, visible_subjects_labels)

    def _project_selection_changed(self, value):
        self._update_items(value)

    def _project_list_changed(self, value):
        self._update_items(value)


class ScanListModel(ProgressListBoxModelFactory):
    def __init__(self, project_model, subject_model, database):
        ProgressListBoxModelFactory.__init__(self)

        self._database = database
        self._selected_scans = SelectedItemsModel()
        self._unselected_scans = SelectedItemsModel()
        self._subject_model = subject_model

        subject_model.list_items_model.add_listener(self._subject_list_changed)
        subject_model.selected_items_model.add_listener(self._subject_selection_changed)

        self._selected_scans.add_listener(self._scan_selection_changed)
        self._unselected_scans.add_listener(self._scan_unselection_changed)

    def _update_items(self, subject_list):
        subject_list = self._subject_model.selected_items_model.selected_items
        scan_records = []
        self._database.clear_all_download_model_listeners()
        for subject in subject_list:
            session_map = subject.get_session_map()
            for session in session_map.values():
                scan_map = session.get_scan_map()
                for scan in scan_map.values():
                    scan_records.append(ScanRecordModel(scan, subject.subject_label + ':' + scan.scan_id,
                                                        self._database.get_scan_download_model(subject.project_id,
                                                                                                 subject.subject_id,
                                                                                                 scan.scan_id)))
        self.get_list_model().set_list_items(scan_records)

    def _subject_selection_changed(self, value):
        self._update_items(value)

    def _subject_list_changed(self, value):
        self._update_items([]) #ToDo: this is the list of selected subjects

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


class ScanRecordModel(Observable):
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

    def get_label(self):
        return self.scan.scan_id