from tkinter import Toplevel, Frame, Label, Entry, LEFT, RIGHT, StringVar, Button


class SettingsMenu(object):
    def __init__(self, controller, config_save):
        self.controller = controller
        config = config_save.get_configuration()
        self.config_save = config_save
        self.window = Toplevel()
        self.server_name_entry = LabelEntry(self.window, "Server name:", False, config.server_name)
        self.url_entry = LabelEntry(self.window, "Server URL:", False, config.base_url)
        self.user_name_entry = LabelEntry(self.window, "User name:", False, config.user_name)
        self.password_entry = LabelEntry(self.window, "Password:", True, config.password)
        button_panel = ButtonPanel(self.window, self)

    def save(self):
        new_server_name = self.server_name_entry.value.get()
        new_base_url = self.url_entry.value.get()
        new_user_name = self.user_name_entry.value.get()
        new_password = self.password_entry.value.get()
        config = self.config_save.get_configuration()

        server_changed = False

        if config.server_name != new_server_name:
            config.server_name = self.server_name_entry.value.get()

        if config.base_url != new_base_url:
            config.base_url = self.url_entry.value.get()
            server_changed = True

        if config.user_name != new_user_name:
            config.user_name = self.user_name_entry.value.get()
            server_changed = True

        if config.password != new_password:
            config.password = self.password_entry.value.get()
            server_changed = True

        self.config_save.save()
        if server_changed:
            self.controller.reset_database()


class ButtonPanel(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)

        self.window = parent
        self.controller = controller
        self.cancel_button = Button(parent, text="Cancel", command=self.cancel_callback)
        self.cancel_button.pack(side=LEFT)
        self.save_button = Button(parent, text="OK", command=self.save_callback)
        self.save_button.pack(side=RIGHT)
        self.apply_button = Button(parent, text="Apply", command=self.apply_callback)
        self.apply_button.pack(side=RIGHT)

    def save_callback(self):
        self.controller.save()
        self.window.destroy()

    def apply_callback(self):
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