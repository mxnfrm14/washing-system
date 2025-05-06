import customtkinter as ctk
from controller import PageController
from pages.start_page import StartPage
from pages.general_settings import GeneralSettings
from custom_button import create_custom_button

ctk.set_appearance_mode('System')  # Set the default appearance mode to System
ctk.set_default_color_theme("theme.json")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Washing System")
        self.iconbitmap("assets/icons/logo.ico")
        self.geometry("800x600")
        # self.resizable(False, False)

        self.fonts = {
            "default": ctk.CTkFont(family="EncodeSansExpanded-Regular", size=14, weight="normal"),
            "bold": ctk.CTkFont(family="EncodeSansExpanded-Bold", size=14, weight="bold"),
            "title": ctk.CTkFont(family="EncodeSansExpanded-Bold", size=20, weight="bold"),
            "subtitle": ctk.CTkFont(family="EncodeSansExpanded-Regular", size=16, weight="normal")
        }

        self.grid_rowconfigure(1, weight=1) # Make the middle row expandable
        self.grid_rowconfigure((0,2), weight=0) # Make the top and bottom rows non-expandable
        self.grid_columnconfigure(1, weight=1) # Make the middle column expandable
        self.grid_columnconfigure((0,2), weight=0) # Make the left and right columns non-expandable


        self.navigation_frame = ctk.CTkFrame(self, fg_color="transparent")
        # self.navigation_frame.grid(row=0, column=0, columnspan=3, sticky="new")
        self.navigation_frame.grid_rowconfigure(0, weight=0)
        self.navigation_frame.grid_columnconfigure((0,1,2), weight=0)

        
        self.container = ctk.CTkFrame(self, corner_radius=6)
        
        # Make the frames take the whole space
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.container.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=10, pady=10)


        self.controller = PageController(self.container, self)
        self.controller.add_page("Accueil", StartPage)
        self.controller.add_page("Etape1", GeneralSettings)

        self.controller.show_page("Accueil")

        self.utils_frame = ctk.CTkFrame(self , fg_color="transparent")
        # Configuration pour layout bas : 1 row, 3 colonnes
        self.utils_frame.grid_rowconfigure(0, weight=1)
        self.utils_frame.grid_columnconfigure(0, weight=0)  # Colonne des options
        self.utils_frame.grid_columnconfigure(1, weight=1)  # Espace vide
        self.utils_frame.grid_columnconfigure(2, weight=0)  # Reset button

        # Frame pour organiser les 2x2 options
        self.settings_inner_frame = ctk.CTkFrame(self.utils_frame, fg_color="transparent")
        self.settings_inner_frame.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # Grid pour 2 lignes, 2 colonnes
        self.settings_inner_frame.grid_rowconfigure((0,1), weight=0)
        self.settings_inner_frame.grid_columnconfigure((0,1), weight=1)


        # Widgets for appearance mode and scaling
        self.appearance_mode_label = ctk.CTkLabel(self.utils_frame, text="Appearance Mode:", anchor="w", font=self.fonts["default"])
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self, values=["System", "Light", "Dark"],
                                     command=self.change_appearance_mode, font=self.fonts["default"], dropdown_font=self.fonts["default"])
        self.scaling_label = ctk.CTkLabel(self.utils_frame, text="UI Scaling:", anchor="w", font=self.fonts["default"])
        self.scaling_optionemenu = ctk.CTkOptionMenu(self, values=["80%", "90%", "100%", "110%", "120%"],
                                 command=self.change_scaling_event, font=self.fonts["default"], dropdown_font=self.fonts["default"])


        # Reset button
        self.reset_button = create_custom_button(
            master=self.utils_frame,
            text="Reset",
            font=self.fonts["default"],
            icon_path="assets/icons/trash.png",
            icon_side="left",
            outlined=False,
            command=lambda: self.controller.show_page("Accueil")
        )
        # Function to update widget visibility based on the current page
        def update_widget_visibility(page_name):
            if page_name == "Accueil":
                self.navigation_frame.grid_forget()
                self.utils_frame.grid_forget()
                self.appearance_mode_label.grid_forget()
                self.appearance_mode_optionemenu.grid_forget()
                self.scaling_label.grid_forget()
                self.scaling_optionemenu.grid_forget()
                self.reset_button.grid_forget()
            else:
                self.navigation_frame.grid(row=0, column=0, columnspan=3, sticky="new")
                self.utils_frame.grid(row=2, column=0, columnspan=3, sticky="sew")
                # OptionMenu widgets placés dans settings_inner_frame
                self.appearance_mode_label.grid(row=0, column=0, sticky="w", padx=5, pady=5, in_=self.settings_inner_frame)
                self.appearance_mode_optionemenu.grid(row=1, column=0, sticky="w", padx=5, pady=5, in_=self.settings_inner_frame)

                self.scaling_label.grid(row=0, column=1, sticky="w", padx=5, pady=5, in_=self.settings_inner_frame)
                self.scaling_optionemenu.grid(row=1, column=1, sticky="w", padx=5, pady=5, in_=self.settings_inner_frame)
                self.reset_button.grid(row=0, column=2, sticky="e", padx=5, pady=5, in_=self.utils_frame)


        # Bind the visibility update to page changes
        self.controller.on_page_change(update_widget_visibility)

        # Initial visibility update
        update_widget_visibility(self.controller.current_page)
    
    def change_appearance_mode(self, new_appearance_mode):
        """Change the appearance mode globally and update the stored setting"""
        self.current_appearance_mode = new_appearance_mode
        ctk.set_appearance_mode(new_appearance_mode)
    
    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        ctk.set_widget_scaling(new_scaling_float)