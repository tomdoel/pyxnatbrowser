# https://github.com/tomdoel/pyxnatbrowser
# Author: Tom Doel www.tomdoel.com
# Distributed under the Simplified BSD License.
from sys import stdout
from tkinter import Frame, Scrollbar, VERTICAL, Label, Listbox, EXTENDED, RIGHT, Y, LEFT, BOTH, END, Checkbutton, Text, \
    IntVar
from tkinter.ttk import Progressbar

from observable import Observable
from xnatdatabase import ProgressStatus


class LabeledCheckListBox(Frame):
    def __init__(self, parent, selected_items_model, unselected_items_model, label_text):
        Frame.__init__(self, parent)

        scrollbar = Scrollbar(self, orient=VERTICAL)
        Label(self, text=label_text).pack()
        self.check_list_box = CheckListBox(self, scrollbar, selected_items_model, unselected_items_model)
        scrollbar.config(command=self.check_list_box.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.check_list_box.pack(side=LEFT, fill=BOTH, expand=1)

    def refresh_checks(self):
        self.check_list_box.refresh_checks()

    def _update_list(self, scan_records):
        self.check_list_box.update_list(scan_records)


class CheckListBox(Text):
    def __init__(self, parent, scrollbar, selected_items_model, unselected_items_model):
        Text.__init__(self, parent, yscrollcommand=scrollbar.set)

        self.selected_items_model = selected_items_model
        self.unselected_items_model = unselected_items_model
        self.list_objects = []
        self.check_buttons = {}
        self.next_index = 0
        self.checked_indices = None
        self.unchecked_indices = None

    def update_list(self, scan_records):
        self.delete(1.0, END)  # Clears the list entries

        self.list_objects = []
        self.check_buttons = {}
        self.next_index = 0
        self.checked_indices = None
        self.unchecked_indices = None
        for scan_record in scan_records:
            self.list_objects.append(scan_record.scan)
            new_checkbutton = ProgressCheckButton(self, scan_record.label, self.next_index, scan_record)
            self.window_create("end", window=new_checkbutton)
            self.insert("end", "\n")
            self.check_buttons[self.next_index] = new_checkbutton
            new_checkbutton.add_listener(self._checkbox_changed)
            self.next_index += 1

        self._populate_cache()

    def refresh_checks(self):
        for index, checkbutton in self.check_buttons.items():
            checkbutton.refresh_check()
        self._populate_cache()

    def _populate_cache(self):
        self.checked_indices = []
        self.unchecked_indices = []
        for index, checkbutton in self.check_buttons.items():
            if checkbutton.is_checked():
                self.checked_indices.append(index)
            else:
                self.unchecked_indices.append(index)

    def _checkbox_changed(self, index, value):
        self._populate_cache()
        selected_items = [self.list_objects[int(index)] for index in self.checked_indices]
        unselected_items = [self.list_objects[int(index)] for index in self.unchecked_indices]

        # Update the selection models - these will trigger notifications via their setter methods
        self.selected_items_model.selected_items = selected_items
        self.unselected_items_model.selected_items = unselected_items


class ProgressCheckButton(Frame, Observable):
    def __init__(self, parent, label, index, status_model):
        Frame.__init__(self, parent)
        Observable.__init__(self)
        self.index = index
        self.status_model = status_model
        self.var = IntVar()
        self.var.set(self.status_model.is_checked())
        self.progress_var = IntVar()
        self.progress_status = ProgressStatus.undefined
        self.check_button = Checkbutton(self, text=label, variable=self.var, command=self._check_changed)
        self.progress_bar = Progressbar(self, orient='horizontal', mode='indeterminate', variable=self.progress_var)
        self.check_button.pack(side=LEFT, fill="both", expand=True)
        self.status_model.model.add_listener(self._progress_status_changed)

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
