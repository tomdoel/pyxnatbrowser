# https://github.com/tomdoel/pyxnatbrowser
# Author: Tom Doel www.tomdoel.com
# Distributed under the Simplified BSD License.
from sys import stdout
from tkinter import Frame, Scrollbar, VERTICAL, Label, Listbox, EXTENDED, RIGHT, Y, LEFT, BOTH, END, Checkbutton, Text, \
    IntVar
from tkinter.ttk import Progressbar

from observable import Observable


class LabeledCheckListBox(Frame):
    def __init__(self, parent, selected_items, unselected_items, label_text):
        Frame.__init__(self, parent)

        self.list_objects = []
        self.selected_items_model = selected_items
        self.unselected_items_model = unselected_items
        scrollbar = Scrollbar(self, orient=VERTICAL)
        Label(self, text=label_text).pack()
        self.check_list_box = CheckListBox(self, scrollbar)
        scrollbar.config(command=self.check_list_box.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.check_list_box.pack(side=LEFT, fill=BOTH, expand=1)

    def refresh_checks(self):
        self.check_list_box.refresh_checks()

    def _update_list(self, scan_records):
        self.list_objects = []
        self.check_list_box.clear()
        for scan_record in scan_records:
            self.list_objects.append(scan_record.scan)
            self.check_list_box.append(scan_record.label, scan_record)

        self.check_list_box.add_listener(self._on_select)

    def _on_select(self, selected_indices):
        selected_items = [self.list_objects[int(index)] for index in self.check_list_box.curselection()]
        unselected_items = [self.list_objects[int(index)] for index in self.check_list_box.curunselection()]
        self.selected_items_model.selected_items = selected_items
        self.unselected_items_model.selected_items = unselected_items


class CheckListBox(Text, Observable):
    def __init__(self, parent, scrollbar):
        Text.__init__(self, parent, yscrollcommand=scrollbar.set)
        Observable.__init__(self)
        self.checkbuttons = {}
        self.next_index = 0
        self.checked_indices = None
        self.unchecked_indices = None

    def clear(self):
        self.delete(1.0, END)
        self.next_index = 0
        self.checked_indices = None
        self.unchecked_indices = None

    def append(self, label, download_model):
        new_checkbutton = ProgressCheckButton(self, label, self.next_index, download_model)
        self.window_create("end", window=new_checkbutton)
        self.insert("end", "\n")
        self.checkbuttons[self.next_index] = new_checkbutton
        # if download_model.is_downloaded():
        #     new_checkbutton.select()
        new_checkbutton.add_listener(self._checkbox_changed)
        self.next_index += 1
        self.checked_indices = None
        self.unchecked_indices = None

    def refresh_checks(self):
        self.populate_cache()
        for index, checkbutton in self.checkbuttons.items():
            checkbutton.refresh_check()

    def populate_cache(self):
        self.checked_indices = []
        self.unchecked_indices = []
        for index, checkbutton in self.checkbuttons.items():
            if checkbutton.is_checked():
                self.checked_indices.append(index)
            else:
                self.unchecked_indices.append(index)

    def _checkbox_changed(self, index, value):
        self.populate_cache()
        self._notify(self.checked_indices)

    def curselection(self):
        if self.checked_indices is None or self.unchecked_indices is None:
            self.populate_cache()

        return self.checked_indices

    def curunselection(self):
        if self.checked_indices is None or self.unchecked_indices is None:
            self.populate_cache()

        return self.unchecked_indices


class ProgressCheckButton(Frame, Observable):
    def __init__(self, parent, label, index, download_model):
        Frame.__init__(self, parent)
        Observable.__init__(self)
        self.index = index
        self.download_model = download_model
        self.var = IntVar()
        self.progress_var = IntVar()
        self.check_button = Checkbutton(self, text=label, variable=self.var, command=self._check_changed)
        self.progress_bar = Progressbar(self, orient='horizontal', mode='determinate', variable=self.progress_var, maximum=download_model.get_number_of_server_files())
        self.check_button.pack(side=LEFT, fill="both", expand=True)
        self.progress_bar.pack(side=RIGHT, fill="both", expand=True)

        if self.download_model.is_downloaded():
            self.select()
        self.update_progress()
        # self.progress_bar.start()

    def refresh_check(self):
        if self.download_model.is_downloaded():
            self.select()
        else:
            self.deselect()

    def is_checked(self):
        return self.var.get()

    def update_progress(self):
        self.progress_var.set(self.download_model.get_number_of_downloaded_files())

    def _check_changed(self):
        self._notify(self.index, self.var.get())

    def select(self):
        self.check_button.select()

    def deselect(self):
        self.check_button.deselect()

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


