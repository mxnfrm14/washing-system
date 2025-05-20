import customtkinter as ctk
from controller import PageController
from pages.general_settings import GeneralSettings
from pages.washing_component import WashingComponent
from pages.pumps import Pumps
from pages.circuits import Circuits
from pages.sequences import Sequences
from pages.results import Results
from components.custom_button import CustomButton
from components.navigation_menu import NavigationMenu
from utils.appearance_manager import AppearanceManager


ctk.set_appearance_mode('System')
ctk.set_default_color_theme("theme.json")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Washing System")
        self.iconbitmap("assets/icons/logo.ico")
        self.geometry("1300x800")
        self.resizable(False, False)
        
        # Define fonts
        self.fonts = {
            "default": ctk.CTkFont(family="Encode Sans Expanded", size=14, weight="normal"),
            "bold": ctk.CTkFont(family="Encode Sans Expanded Bold", size=14, weight="bold"),
            "title": ctk.CTkFont(family="Encode Sans Expanded Bold", size=24, weight="bold"),
            "subtitle": ctk.CTkFont(family="Encode Sans Expanded", size=16, weight="normal")
        }

        # Configure grid layout
        self.grid_rowconfigure(1, weight=1)  # Make the middle row expandable
        self.grid_rowconfigure((0,2), weight=0)  # Make the top and bottom rows non-expandable
        self.grid_columnconfigure(0, weight=1)  # Make the column expandable
        
        # Create main container for pages
        self.container = ctk.CTkFrame(self)
        self.container.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        # Make the container take the whole space
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        # Create page controller
        self.controller = PageController(self.container, self)
        
        # Create navigation menu - IMPORTANT: Use the NavigationMenu class, not a regular frame
        self.navigation_frame = NavigationMenu(self, self.controller, appearance_mode=ctk.get_appearance_mode())
        
        # Add pages to the controller
        self.controller.add_page("general_settings", GeneralSettings)
        self.controller.add_page("washing_components", WashingComponent)
        self.controller.add_page("pumps", Pumps)
        self.controller.add_page("circuits", Circuits)
        self.controller.add_page("sequence", Sequences)
        self.controller.add_page("results", Results)
        
        # Set up the navigation menu
        self.controller.set_navigation_menu(self.navigation_frame)
        self.navigation_frame.create_nav_indicators()

        self.navigation_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
        
        # Create utilities frame
        self.utils_frame = ctk.CTkFrame(self, fg_color="transparent")
        
        # Configuration for bottom layout: 1 row, 3 columns
        self.utils_frame.grid_rowconfigure(0, weight=1)
        self.utils_frame.grid_columnconfigure(0, weight=0)  # Options column
        self.utils_frame.grid_columnconfigure(1, weight=1)  # Empty space
        self.utils_frame.grid_columnconfigure(2, weight=0)  # Reset button column

        self.utils_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))

        # Frame for organizing the 2x2 options
        self.settings_inner_frame = ctk.CTkFrame(self.utils_frame, fg_color="transparent")
        self.settings_inner_frame.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # Grid for 2 rows, 2 columns
        self.settings_inner_frame.grid_rowconfigure(0, weight=0)
        self.settings_inner_frame.grid_columnconfigure((0,1), weight=1)

        # Widgets for appearance mode and scaling 
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(
            self, 
            values=["Light", "Dark"],
            command=self.change_appearance_mode, 
            font=self.fonts["default"], 
            dropdown_font=self.fonts["default"]
        )
        
        self.scaling_optionemenu = ctk.CTkOptionMenu(
            self, 
            values=["80%", "90%", "100%", "110%", "120%"],
            command=self.change_scaling_event, 
            font=self.fonts["default"], 
            dropdown_font=self.fonts["default"]
        )
        self.scaling_optionemenu.set("100%")  # Set default scaling
        self.appearance_mode_optionemenu.set("Dark")  # Set default appearance mode

        # Place widgets in the settings_inner_frame
        self.appearance_mode_optionemenu.grid(row=0, column=0, sticky="w", padx=5, pady=5, in_=self.settings_inner_frame)
        self.scaling_optionemenu.grid(row=0, column=1, sticky="w", padx=5, pady=5, in_=self.settings_inner_frame)
        
        # Create reset button
        self.reset_button = CustomButton(
                    master=self.utils_frame,
                    text="Reset",
                    font=self.fonts["default"],
                    icon_path="assets/icons/trash.png",
                    icon_side="left",
                    outlined=False,
                    command=lambda: self.controller.show_page("general_settings"),
                )
        self.reset_button.grid(row=0, column=2, sticky="e", padx=10, in_=self.utils_frame)

        self.controller.show_page("general_settings")
    
    def change_appearance_mode(self, new_appearance_mode):
        """Change the appearance mode globally and update all components"""
        # Use the appearance manager to change mode and notify all components
        AppearanceManager.set_appearance_mode(new_appearance_mode)
    
    
    def change_scaling_event(self, new_scaling: str):
        """Change the UI scaling globally"""
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        ctk.set_widget_scaling(new_scaling_float)