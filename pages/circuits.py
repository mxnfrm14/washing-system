import customtkinter as ctk

class Circuits(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        # self.fonts = {}  # Will be populated by the controller
        # self.app = None  # Will be set by the controller
        ctk.set_default_color_theme("theme.json")

        label = ctk.CTkLabel(self, text="Étape 4 : Configuration", font=controller.fonts.get("title", None), anchor="w")
        label.pack(pady=40)

        bouton_suivant = ctk.CTkButton(self, text="Suivant", font=controller.fonts.get("default", None),
                                      command=lambda: controller.show_page("Etape5"))
        bouton_suivant.pack(pady=10)

        bouton_retour = ctk.CTkButton(self, text="Retour", font=controller.fonts.get("default", None),
                                     command=lambda: controller.show_page("Etape3"))
        bouton_retour.pack(pady=10)
    
    def update_appearance(self):
        """Update any appearance-dependent elements"""
        # If you have any appearance-dependent elements, update them here
        pass