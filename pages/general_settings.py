import customtkinter as ctk
from custom_button import create_custom_button

class GeneralSettings(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        # self.fonts = {}  # Will be populated by the controller
        # self.app = None  # Will be set by the controller
        ctk.set_default_color_theme("theme.json")

        label = ctk.CTkLabel(self, text="General Settings", font=controller.fonts.get("title", None), anchor="w")
        label.pack(pady=40)

        # bouton_suivant = ctk.CTkButton(self, text="Suivant", font=controller.fonts.get("default", None),
        #                               command=lambda: controller.show_page("washing_components"))
        # bouton_suivant.pack(pady=10)

        bouton_suivant = create_custom_button(self,
                                        text="Suivant",
                                        font=controller.fonts.get("default", None),
                                        icon_path="assets/icons/next.png",
                                        icon_side="right",
                                        command=lambda: controller.show_page("washing_components"))
        bouton_suivant.pack(pady=10)

        
    def update_appearance(self):
        """Update any appearance-dependent elements"""
        # If you have any appearance-dependent elements, update them here
        pass