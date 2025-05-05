import customtkinter as ctk

class StartPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        label = ctk.CTkLabel(self, text="Bienvenue dans l'application", font=ctk.CTkFont(size=20, weight="bold"))
        label.pack(pady=40)

        bouton = ctk.CTkButton(self, text="Commencer",
                               command=lambda: controller.show_page("Etape1"))
        bouton.pack()
