import customtkinter as ctk
from PIL import Image
from components.custom_button import CustomButton

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("theme.json")

class WelcomeWindow(ctk.CTk):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller #MainController
        self.title("Welcome to Washing System")
        self.iconbitmap("assets/icons/logo.ico")
        self.geometry("600x400")
        self.resizable(False, False)
        
        # Center the window
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Main container
        self.container = ctk.CTkFrame(self)
        self.container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Logo
        self.logo = ctk.CTkImage(light_image=Image.open("assets/images/logo_white.png"),
                                 dark_image=Image.open("assets/images/logo_blue.png"), 
                                 size=(300, 200))
        self.logo_label = ctk.CTkLabel(self.container, text="", image=self.logo)
        self.logo_label.pack(pady=20)

        # Button Frame
        self.button_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.button_frame.pack(pady=20, padx=20, fill="x")
        self.button_frame.grid_columnconfigure((0, 1), weight=1)

        # Load Config Button
        self.load_config_button = CustomButton(
            master=self.button_frame,
            text="Charger la configuration",
            font=ctk.CTkFont(family="Encode Sans Expanded", size=14),
            icon_path="assets/icons/upload.png",
            icon_side="left",
            outlined=True,
            command=self.controller.handle_load_config_request
        )
        self.load_config_button.grid(row=0, column=0, padx=10, pady=10)

        # New Config Button
        self.new_config_button = CustomButton(
            master=self.button_frame,
            text="Nouvelle configuration",
            font=ctk.CTkFont(family="Encode Sans Expanded", size=14),
            icon_path="assets/icons/add.png",
            icon_side="left",
            outlined=False,
            command=self.controller.handle_new_config_request
        )
        self.new_config_button.grid(row=0, column=1, padx=10, pady=10)
