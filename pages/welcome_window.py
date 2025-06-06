import customtkinter as ctk
from PIL import Image
from components.custom_button import CustomButton


class WelcomeWindow(ctk.CTk):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.title("Welcome to Washing System")
        self.iconbitmap("assets/icons/logo.ico")
        self.geometry("600x400")
        
        # Configure grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Main container
        self.container = ctk.CTkFrame(self)
        self.container.grid(row=0, column=0, sticky="nsew")
        self.container.grid_rowconfigure((0, 1), weight=1)
        self.container.grid_columnconfigure((0, 1), weight=1)

        # Logo
        self.logo = ctk.CTkImage(light_image=Image.open("assets/images/logo_white.png"),
                            dark_image=Image.open("assets/images/logo_blue.png"), 
                            size=(300, 200))
        self.logo_label = ctk.CTkLabel(self, text="", image=self.logo, compound="top")
        self.logo_label.grid(row=0, column=0, pady=(0, 70))

        # Load Config Button
        self.load_config_button = CustomButton(
            master=self.container,
            text="Charger la configuration",
            font=ctk.CTkFont(family="Encode Sans Expanded", size=14, weight="normal"),
            icon_path="assets/icons/upload.png",
            icon_side="left",
            outlined=True,
            command=self.load_config
        )
        self.load_config_button.grid(row=1, column=0, pady=10)

        # New Config Button
        self.new_config_button = CustomButton(
            master=self.container,
            text="Nouvelle configuration",
            font=ctk.CTkFont(family="Encode Sans Expanded", size=14, weight="normal"),
            icon_path="assets/icons/add.png",
            icon_side="left",
            outlined=False,
            command=self.launch_main_app
        )
        self.new_config_button.grid(row=1, column=1, pady=10)

    def launch_main_app(self):
        """Launch the main application via the controller"""
        self.load_config_button.destroy()
        self.new_config_button.destroy()
        self.logo_label.destroy()



        self.controller.show_main_app()

    def load_config(self):
        """Load configuration via the controller"""
        self.controller.load_configuration()