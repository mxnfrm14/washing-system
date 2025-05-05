import customtkinter as ctk
from controller import PageController
from pages.start_page import StartPage
from pages.general_settings import GeneralSettings


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Washing System")
        # self.iconbitmap("assets/icons/logo.ico")
        self.geometry("800x600")
        ctk.set_appearance_mode("system")  # "dark", "light", or "system"
        ctk.set_default_color_theme("theme.json")  # Utilisation d'un fichier JSON pour le thème

        font = ctk.CTkFont(family="EncodeSansExpanded-Regular", size=14, weight="normal")

        # self.navigation_frame

        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)

        self.controller = PageController(self.container, self)
        self.controller.add_page("Accueil", StartPage)
        self.controller.add_page("Etape1", GeneralSettings)

        self.controller.show_page("Accueil")
