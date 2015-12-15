# https://github.com/tomdoel/pyxnatbrowser
# Author: Tom Doel www.tomdoel.com
# Distributed under the Simplified BSD License.

from tkinter import Frame, Scrollbar, VERTICAL, Label, Listbox, EXTENDED, RIGHT, Y, LEFT, BOTH, END

from observable import Observable


class LabeledListBox(Frame):
    def __init__(self, parent, selected_items, label_text):
        Frame.__init__(self, parent)

        self.list_objects = []
        self.selected_items_model = selected_items
        scrollbar = Scrollbar(self, orient=VERTICAL)
        Label(self, text=label_text).pack()
        self.listbox = Listbox(self, selectmode=EXTENDED, exportselection=0, yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.listbox.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.listbox.pack(side=LEFT, fill=BOTH, expand=1)
        self.listbox.bind('<<ListboxSelect>>', self._on_select)

    def _update_list(self, values, labels):
        self.list_objects = []
        old_selected_item_labels = [self.listbox.get(int(index)) for index in self.listbox.curselection()]
        self.listbox.delete(0, END)
        for value, label in zip(values, labels):
            self.list_objects.append(value)
            self.listbox.insert(END, label)

        for index, label in enumerate(labels):
            if label in old_selected_item_labels:
                self.listbox.selection_set(index)

    def _on_select(self, evt):
        selected_items = [self.list_objects[int(index)] for index in self.listbox.curselection()]
        self.selected_items_model.selected_items = selected_items


class SelectedItems(Observable):
    def __init__(self):
        Observable.__init__(self)
        self._selected_items = []

    @property
    def selected_items(self):
        return self._selected_items

    @selected_items.setter
    def selected_items(self, value):
        self._selected_items = value
        self._notify(value)