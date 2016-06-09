# https://github.com/tomdoel/pyxnatbrowser
# Author: Tom Doel www.tomdoel.com
# Distributed under the Simplified BSD License.

from tkinter import Frame, Scrollbar, VERTICAL, Label, Listbox, EXTENDED, RIGHT, Y, LEFT, BOTH, END, Checkbutton

from database.observable import Observable


class LabeledListBox(Frame):
    def __init__(self, parent, list_model, label_text):
        Frame.__init__(self, parent)

        self._list_model = list_model
        self._list_objects = []
        self._selected_items = []
        scrollbar = Scrollbar(self, orient=VERTICAL)
        Label(self, text=label_text).pack()
        self.listbox = Listbox(self, selectmode=EXTENDED, exportselection=0, yscrollcommand=scrollbar.set, borderwidth=0, highlightthickness=0)
        scrollbar.config(command=self.listbox.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.listbox.pack(side=LEFT, fill=BOTH, expand=1)
        self.listbox.bind('<<ListboxSelect>>', self._on_select)
        self._list_model.list_items_model.add_listener(self._list_items_changed)
        self._list_model.selected_items_model.add_listener(self._selected_items_changed)
        self._update_list_items()

    def _list_items_changed(self, values):
        self._update_list_items()

    def _selected_items_changed(self, values):
        self._update_selected_items()

    def _update_list_items(self):
        values, labels = self._list_model.list_items_model.get_list_values()
        if not values == self._list_objects:
            self._list_objects = []
            self._selected_items = []
            self.listbox.delete(0, END)
            for value, label in zip(values, labels):
                self._list_objects.append(value)
                self.listbox.insert(END, label)
            self._update_selected_items()

    def _update_selected_items(self):
        selected_items = self._list_model.selected_items_model.selected_items
        if not selected_items == self._selected_items:
            self._selected_items = selected_items
            for index, list_item in enumerate(self._list_objects):
                if list_item in selected_items:
                    self.listbox.selection_set(index)

    def _on_select(self, evt):
        visible_selected_indices = self.listbox.curselection()
        for index, list_item in enumerate(self._list_objects):
            if index in visible_selected_indices:
                self._list_model.selected_items_model.select(list_item)
            else:
                self._list_model.selected_items_model.deselect(list_item)


class ListModel:
    def __init__(self):
        self._selected_items_model = SelectedItemsModel()
        self._list_items_model = ListItemsModel()

    @property
    def selected_items_model(self):
        return self._selected_items_model

    @property
    def list_items_model(self):
        return self._list_items_model


class ListItemsModel(Observable):
    def __init__(self):
        Observable.__init__(self)

        self._values = []
        self._labels = []

    def set_list_values(self, values, labels):
        self._values = values
        self._labels = labels
        self._notify(values)

    def get_list_values(self):
        return self._values, self._labels


class SelectedItemsModel(Observable):
    def __init__(self):
        Observable.__init__(self)
        self._selected_items = []

    def select(self, item):
        if item not in self.selected_items:
            self.selected_items.append(item)
            self._notify(self.selected_items)

    def deselect(self, item):
        if item in self.selected_items:
            self.selected_items.remove(item)
            self._notify(self.selected_items)

    @property
    def selected_items(self):
        return self._selected_items

    @selected_items.setter
    def selected_items(self, value):
        if self.selected_items != value:
            self._selected_items = value
            self._notify(value)