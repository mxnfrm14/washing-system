import customtkinter as ctk

class PageController:
    def __init__(self, container, app):
        self.container = container
        self.app = app
        self.pages = {}
        self.current_page = None
        self.page_change_callback = None
        self.fonts = app.fonts
        ctk.set_default_color_theme("theme.json")
        self.app.fonts = self.fonts


    def add_page(self, name, page_class):
        page = page_class(self.container, self)
        page.fonts = self.app.fonts
        page.app = self.app
        self.pages[name] = page
        page.grid(row=0, column=0, sticky="nsew")

    def on_page_change(self, callback):
        """Register a callback to be called when the page changes."""
        self.page_change_callback = callback

    def show_page(self, page_name):
        """Show the specified page and trigger the page change callback."""
        if page_name in self.pages:
            page = self.pages[page_name]
            page.tkraise()
            self.current_page = page_name
            if self.page_change_callback:
                self.page_change_callback(page_name)

