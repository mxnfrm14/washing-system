import customtkinter as ctk
from PIL import Image
from custom_button import create_custom_button


class StartPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        # self.fonts = {}  # Will be populated by the controller
        # self.app = None  # Will be set by the controller
        ctk.set_default_color_theme("theme.json")
        ctk.set_appearance_mode("Dark")



        logo = ctk.CTkImage(light_image=Image.open("assets/images/logo_white.png"),
                            dark_image=Image.open("assets/images/logo_blue.png"), 
                            size=(300, 200))
        logo_label = ctk.CTkLabel(self, text="", image=logo, compound="top")
        logo_label.pack(pady=20)
        
        label = ctk.CTkLabel(self, text="Bienvenue dans l'application", 
                             font=controller.fonts.get("title", None),
                             anchor="w")
        label.pack(pady=40)

        bouton = ctk.CTkButton(self, text="Commencer", 
                               font=controller.fonts.get("default", None),
                              command=lambda: controller.show_page("Etape1"))
        bouton.pack()
