from tkinter import Toplevel, Frame, Label, Entry, LEFT, RIGHT, StringVar, Button


class SettingsMenu(object):
    def __init__(self, config_save, config):
        self.config = config
        self.config_save = config_save
        self.window = Toplevel()
        self.server_name_entry = LabelEntry(self.window, "Server name:")
        self.url_entry = LabelEntry(self.window, "Server URL:")
        self.user_name_entry = LabelEntry(self.window, "User name:")
        self.password_entry = LabelEntry(self.window, "Password:")
        button_panel = ButtonPanel(self.window, self)

    def save(self):
        self.config.server_name = self.server_name_entry.value.get()
        self.config.base_url = self.url_entry.value.get()
        self.config.user_name = self.user_name_entry.value.get()
        self.config.password = self.password_entry.value.get()
        self.config_save.save(self.config)


class ButtonPanel(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)

        self.controller = controller
        self.save_button = Button(parent, text="Save", command=self.save_callback)
        self.save_button.pack()

    def save_callback(self):
        self.controller.save()


class LabelEntry(Frame):
    def __init__(self, parent, label_text):
        Frame.__init__(self, parent)

        self.value = StringVar()
        label = Label(self, text=label_text)
        label.pack(side=LEFT)
        entry = Entry(self, textvariable=self.value)
        entry.pack(side=RIGHT)

        # parent.window_create("end", window=self)
        self.pack()