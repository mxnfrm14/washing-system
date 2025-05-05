class PageController:
    def __init__(self, container, root):
        self.container = container
        self.root = root
        self.pages = {}

    def add_page(self, name, PageClass):
        page = PageClass(parent=self.container, controller=self)
        self.pages[name] = page
        page.grid(row=0, column=0, sticky="nsew")

    def show_page(self, name):
        page = self.pages[name]
        page.tkraise()
