import customtkinter as ctk

class GeneralSettings(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        label = ctk.CTkLabel(self, text="Étape 1 : Configuration", font=ctk.CTkFont(size=20))
        label.pack(pady=40)

        bouton_suivant = ctk.CTkButton(self, text="Suivant",
                                       command=lambda: controller.show_page("Etape2"))
        bouton_suivant.pack(pady=10)

        bouton_retour = ctk.CTkButton(self, text="Retour",
                                      command=lambda: controller.show_page("Accueil"))
        bouton_retour.pack(pady=10)
