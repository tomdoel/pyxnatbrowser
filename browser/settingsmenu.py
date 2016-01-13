from tkinter import Toplevel, Frame, Label, Entry, LEFT, RIGHT, StringVar, Button


class SettingsMenu(object):
    def __init__(self, config_save):
        self.config = config_save.get_configuration()
        self.config_save = config_save
        self.window = Toplevel()
        self.server_name_entry = LabelEntry(self.window, "Server name:", False, self.config.server_name)
        self.url_entry = LabelEntry(self.window, "Server URL:", False, self.config.base_url)
        self.user_name_entry = LabelEntry(self.window, "User name:", False, self.config.user_name)
        self.password_entry = LabelEntry(self.window, "Password:", True, self.config.password)
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

        self.window = parent
        self.controller = controller
        self.cancel_button = Button(parent, text="Cancel", command=self.cancel_callback)
        self.cancel_button.pack(side=LEFT)
        self.save_button = Button(parent, text="Save", command=self.save_callback)
        self.save_button.pack(side=RIGHT)

    def save_callback(self):
        self.controller.save()

    def cancel_callback(self):
        self.window.destroy()


class LabelEntry(Frame):
    def __init__(self, parent, label_text, is_password, initial_value):
        Frame.__init__(self, parent)

        self.value = StringVar()
        self.value.set(initial_value)
        label = Label(self, text=label_text)
        label.pack(side=LEFT)
        if is_password:
            entry = Entry(self, show="*", textvariable=self.value)
        else:
            entry = Entry(self, textvariable=self.value)
        entry.pack(side=RIGHT)

        # parent.window_create("end", window=self)
        self.pack()