# https://github.com/tomdoel/pyxnatbrowser
# Author: Tom Doel www.tomdoel.com
# Distributed under the Simplified BSD License.
from enum import Enum
from sys import stdout
from tkinter import Frame, Scrollbar, VERTICAL, Label, Listbox, EXTENDED, RIGHT, Y, LEFT, BOTH, END, Checkbutton, Text, \
    IntVar
from tkinter.ttk import Progressbar

from database.observable import Observable
from database.xnatdatabase import ProgressStatus


class LabeledProgressListBox(Frame):
    def __init__(self, parent, list_model_factory, label_text):
        Frame.__init__(self, parent)

        scrollbar = Scrollbar(self, orient=VERTICAL)
        Label(self, text=label_text).pack()
        self.check_list_box = ProgressListBox(self, scrollbar, list_model_factory)
        scrollbar.config(command=self.check_list_box.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.check_list_box.pack(side=LEFT, fill=BOTH, expand=1)


class ProgressListBox(Text):
    def __init__(self, parent, scrollbar, list_model_factory):
        Text.__init__(self, parent, yscrollcommand=scrollbar.set)

        self._list_model_factory = list_model_factory
        self._list_model = list_model_factory.get_list_model()
        self._list_model.add_listener(self._list_items_changed)

    def _list_items_changed(self):
        self.delete(1.0, END)  # Clears the list entries
        for list_item in self._list_model.get_list_items():
            list_item_model = self._list_model_factory.get_list_item_model(list_item)
            new_checkbutton = ProgressListBoxItem(self, list_item_model)
            self.window_create("end", window=new_checkbutton)
            self.insert("end", "\n")


class ProgressListBoxModelFactory:
    def __init__(self):
        self._list_model = ProgressListBoxModel()

    def get_list_model(self):
        return self._list_model

    def get_list_item_model(self, list_item):
        return ProgressListBoxItemModel(list_item.get_label())


class ProgressListBoxModel(Observable):
    def __init__(self):
        Observable.__init__(self)

        self._list_items = []

    def get_list_items(self):
        return self._list_items

    def set_list_items(self, list_items):
        self._list_items = list_items
        self._notify()


class ProgressListBoxItemModel(Observable):
    def __init__(self, label):
        Observable.__init__(self)

        self._label = label
        self._progress_status = ProgressStatus.undefined
        self._check_status = False

    def get_progress_status(self):
        return self._progress_status

    def get_check_status(self):
        return self._check_status

    def get_label(self):
        return self._label

    def set_progress_status(self, progress_status):
        if self._progress_status is not progress_status:
            self._progress_status = progress_status
            self._notify()

    def set_check_status(self, check_status):
        if self._check_status is not check_status:
            self._check_status = check_status
            self._notify()

    def manual_set_checked(self, check_status):
        self.set_check_status(check_status)


class ProgressListBoxItem(Frame, Observable):
    def __init__(self, parent, model):
        Frame.__init__(self, parent)
        Observable.__init__(self)
        self._model = model

        # Create variables and initialise to zero
        self._checked_var = IntVar()
        self._progress_var = IntVar()
        self._checked_var.set(0)
        self._progress_var.set(0)
        self._current_gui_checked_state = CheckStatus.undefined
        self._current_gui_progress_state = ProgressStatus.undefined

        self.check_button = Checkbutton(self, text=model.get_label(), variable=self._checked_var, command=self._user_check_changed)
        self.progress_bar = Progressbar(self, orient='horizontal', mode='indeterminate', variable=self._progress_var)
        self.check_button.pack(side=LEFT, fill="both", expand=True)

        self._update()
        self._model.add_listener(self._model_changed)

    def _model_changed(self):
        self.update()

    def _update(self):
        # Update check status
        model_check_state = self._model.get_check_status()
        if model_check_state is not self._current_gui_checked_state:
            self._current_gui_checked_state = model_check_state
            # if self.status_model.is_checked_force_reload():
            if model_check_state:
                self.check_button.select()
            else:
                self.check_button.deselect()

        # Update progress status
        model_progress_state = self._model.get_progress_status
        if not model_progress_state == self._current_gui_progress_state:
            self._current_gui_progress_state = model_progress_state
            if model_progress_state == ProgressStatus.in_progress:
                self.progress_bar.pack(side=RIGHT, fill="both", expand=True)
            else:
                self.progress_bar.pack_forget()

    def _user_check_changed(self):
        new_checked = self._checked_var.get()
        if new_checked is not self._model.get_check_status():
            self._model.manual_set_checked(new_checked)
        #     self.model.set_checked(new_checked)
        # if new_checked is not self.status_model.is_checked():
        #     self._notify(self.index, new_checked)

    # def update_list(self, scan_records):
    #     self.delete(1.0, END)  # Clears the list entries
    #
    #     self.list_objects = []
    #     self.check_buttons = {}
    #     self.next_index = 0
    #     self.checked_indices = None
    #     self.unchecked_indices = None
    #     for scan_record in scan_records:
    #         self.list_objects.append(scan_record.scan)
    #         node_checkbox_model = ProgressCheckButtonModel(scan_record.label)
    #         new_checkbutton = ProgressCheckButton(self, node_checkbox_model, self.next_index, scan_record)
    #         self.window_create("end", window=new_checkbutton)
    #         self.insert("end", "\n")
    #         self.check_buttons[self.next_index] = new_checkbutton
    #         new_checkbutton.add_listener(self._checkbox_changed)
    #         self.next_index += 1
    #
    #     self._populate_cache()
    #
    # def refresh_checks(self):
    #     for index, checkbutton in self.check_buttons.items():
    #         checkbutton.refresh_check()
    #     self._populate_cache()
    #
    # def _populate_cache(self):
    #     self.checked_indices = []
    #     self.unchecked_indices = []
    #     for index, checkbutton in self.check_buttons.items():
    #         if checkbutton.is_checked():
    #             self.checked_indices.append(index)
    #         else:
    #             self.unchecked_indices.append(index)
    #
    # def _checkbox_changed(self, index, value):
    #     self._populate_cache()
    #     selected_items = [self.list_objects[int(index)] for index in self.checked_indices]
    #     unselected_items = [self.list_objects[int(index)] for index in self.unchecked_indices]
    #
    #     # Update the selection models - these will trigger notifications via their setter methods
    #     self.selected_items_model.selected_items = selected_items
    #     self.unselected_items_model.selected_items = unselected_items


class ProgressCheckButtonModel(Observable):
    def __init__(self, label, status_model):
        self.label = label
        self.status_model = status_model
        self.status_model.model.add_listener(self._progress_status_changed)

    def get_label(self):
        return self.label

    def get_checked(self):
        return self.status_model.is_checked()

    def set_checked(self, checked):
        return self.label

    def _progress_status_changed(self, new_status):
        self._notify(self.index, new_status)


class ProgressCheckButton(Frame, Observable):
    def __init__(self, parent, model, index, status_model):
        Frame.__init__(self, parent)
        Observable.__init__(self)
        self.model = model
        self.index = index
        self.status_model = status_model
        self.var = IntVar()
        self.var.set(model.get_checked())
        self.progress_var = IntVar()
        self.progress_status = ProgressStatus.undefined
        self.check_button = Checkbutton(self, text=model.get_label, variable=self.var, command=self._check_changed)
        self.progress_bar = Progressbar(self, orient='horizontal', mode='indeterminate', variable=self.progress_var)
        self.check_button.pack(side=LEFT, fill="both", expand=True)

        self.model.add_listener(self._model_changed)

    def _model_changed(self, new_status):
        model_state = self.model.get_checked()
        gui_state = self.var.get()
        if model_state is not gui_state:
            self.model.set_checked(gui_state)

    def refresh_check(self):
        if self.status_model.is_checked_force_reload():
            self.check_button.select()
        else:
            self.check_button.deselect()

    def is_checked(self):
        return self.var.get()

    def _progress_status_changed(self, new_status):
        self._refresh_progress()

    def _refresh_progress(self):
        status = self.status_model.get_status()
        if not status == self.progress_status:
            if status == ProgressStatus.in_progress:
                self.progress_bar.pack(side=RIGHT, fill="both", expand=True)
            else:
                self.progress_bar.pack_forget()

    def _check_changed(self):
        new_checked = self.var.get()
        if new_checked is not self.model.get_checked():
            self.model.set_checked(new_checked)
        if new_checked is not self.status_model.is_checked():
            self._notify(self.index, new_checked)


class SelectedItems(Observable):
    def __init__(self):
        Observable.__init__(self)
        self._selected_items = []

    @property
    def selected_items(self):
        return self._selected_items

    @selected_items.setter
    def selected_items(self, value):
        if self.selected_items != value:
            self._selected_items = value
            self._notify(value)


class CheckStatus(Enum):
    off = 0
    on = 1
    undefined = 2
