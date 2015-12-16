# https://github.com/tomdoel/pyxnatbrowser
# Author: Tom Doel www.tomdoel.com
# Distributed under the Simplified BSD License.

from tkinter import Frame, Scrollbar, VERTICAL, Label, Listbox, EXTENDED, RIGHT, Y, LEFT, BOTH, END, Checkbutton, Text, \
    IntVar

from observable import Observable


class LabeledCheckListBox(Frame):
    def __init__(self, parent, selected_items, label_text):
        Frame.__init__(self, parent)

        self.list_objects = []
        self.selected_items_model = selected_items
        scrollbar = Scrollbar(self, orient=VERTICAL)
        Label(self, text=label_text).pack()
        self.check_list_box = CheckListBox(self, scrollbar)
        self.check_list_box.pack(side=LEFT, fill=BOTH, expand=1)
        scrollbar.config(command=self.check_list_box.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.check_list_box.pack(side=LEFT, fill=BOTH, expand=1)

    def _update_list(self, values, labels):
        self.list_objects = []
        self.check_list_box.clear()
        for value, label in zip(values, labels):
            self.list_objects.append(value)
            self.check_list_box.append(label)

        self.check_list_box.add_listener(self._on_select)

    def _on_select(self, selected_indices):
        selected_items = [self.list_objects[int(index)] for index in self.check_list_box.curselection()]
        self.selected_items_model.selected_items = selected_items


class CheckListBox(Text, Observable):
    def __init__(self, parent, scrollbar):
        Text.__init__(self, parent, yscrollcommand=scrollbar.set)
        Observable.__init__(self)
        self.checkbuttons = {}
        self.next_index = 0
        self.checked_indices = []

    def clear(self):
        self.delete(1.0, END)
        self.next_index = 0

    def append(self, label):
        new_checkbutton = CustomCheckButton(self, label, self.next_index)
        self.window_create("end", window=new_checkbutton)
        self.insert("end", "\n")
        self.checkbuttons[self.next_index] = new_checkbutton
        new_checkbutton.add_listener(self._checkbox_changed)
        self.next_index += 1

    def _checkbox_changed(self, index, value):
        self.checked_indices = []
        for index, checkbutton in self.checkbuttons.items():
            if checkbutton.var.get():
                self.checked_indices.append(index)
        self._notify(self.checked_indices)

    def curselection(self):
        return self.checked_indices


class CustomCheckButton(Checkbutton, Observable):
    def __init__(self, parent, label, index):
        var = IntVar()
        Checkbutton.__init__(self, parent, text=label, variable=var, command=self._check_changed)
        Observable.__init__(self)
        self.index = index
        self.var = var

    def _check_changed(self):
        self._notify(self.index, self.var.get())


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