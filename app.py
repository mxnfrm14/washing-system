import customtkinter as ctk
from controller import PageController
from pages.start_page import StartPage
from pages.general_settings import GeneralSettings
from pages.washing_component import WashingComponent
from pages.pumps import Pumps
from pages.circuits import Circuits
from pages.sequences import Sequences
from pages.results import Results
from custom_button import create_custom_button
from navigation_menu import NavigationMenu
from PIL import Image
import os

ctk.set_appearance_mode('System')
ctk.set_default_color_theme("theme.json")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Washing System")
        self.iconbitmap("assets/icons/logo.ico")
        self.geometry("1300x800")
        
        # Store images as instance variables to prevent garbage collection
        self.images = {}
        
        # Define fonts
        self.fonts = {
            "default": ctk.CTkFont(family="EncodeSansExpanded-Regular", size=14, weight="normal"),
            "bold": ctk.CTkFont(family="EncodeSansExpanded-Bold", size=14, weight="bold"),
            "title": ctk.CTkFont(family="EncodeSansExpanded-Bold", size=20, weight="bold"),
            "subtitle": ctk.CTkFont(family="EncodeSansExpanded-Regular", size=16, weight="normal")
        }

        # Configure grid layout
        self.grid_rowconfigure(1, weight=1)  # Make the middle row expandable
        self.grid_rowconfigure((0,2), weight=0)  # Make the top and bottom rows non-expandable
        self.grid_columnconfigure(0, weight=1)  # Make the column expandable
        
        # Create main container for pages
        self.container = ctk.CTkFrame(self, corner_radius=10)
        self.container.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        # Make the container take the whole space
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        # Create page controller
        self.controller = PageController(self.container, self)
        
        # Create navigation menu - IMPORTANT: Use the NavigationMenu class, not a regular frame
        self.navigation_frame = NavigationMenu(self, self.controller)
        
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

        # Create utilities frame
        self.utils_frame = ctk.CTkFrame(self, fg_color="transparent")
        
        # Configuration for bottom layout: 1 row, 3 columns
        self.utils_frame.grid_rowconfigure(0, weight=1)
        self.utils_frame.grid_columnconfigure(0, weight=0)  # Options column
        self.utils_frame.grid_columnconfigure(1, weight=1)  # Empty space
        self.utils_frame.grid_columnconfigure(2, weight=0)  # Reset button column

        # Frame for organizing the 2x2 options
        self.settings_inner_frame = ctk.CTkFrame(self.utils_frame, fg_color="transparent")
        self.settings_inner_frame.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # Grid for 2 rows, 2 columns
        self.settings_inner_frame.grid_rowconfigure((0,1), weight=0)
        self.settings_inner_frame.grid_columnconfigure((0,1), weight=1)

        # Widgets for appearance mode and scaling
        self.appearance_mode_label = ctk.CTkLabel(
            self.utils_frame, 
            text="Appearance Mode:", 
            anchor="w", 
            font=self.fonts["default"]
        )
        
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(
            self, 
            values=["System", "Light", "Dark"],
            command=self.change_appearance_mode, 
            font=self.fonts["default"], 
            dropdown_font=self.fonts["default"]
        )
        
        self.scaling_label = ctk.CTkLabel(
            self.utils_frame, 
            text="UI Scaling:", 
            anchor="w", 
            font=self.fonts["default"]
        )
        
        self.scaling_optionemenu = ctk.CTkOptionMenu(
            self, 
            values=["80%", "90%", "100%", "110%", "120%"],
            command=self.change_scaling_event, 
            font=self.fonts["default"], 
            dropdown_font=self.fonts["default"]
        )
        self.scaling_optionemenu.set("100%")  # Set default scaling
        self.appearance_mode_optionemenu.set("System")  # Set default appearance mode

        # Load the trash icon safely
        try:
            trash_icon_path = "assets/icons/trash.png"
            if os.path.exists(trash_icon_path):
                # Load and store the icon as an instance variable
                trash_img = Image.open(trash_icon_path)
                self.images["trash"] = ctk.CTkImage(
                    light_image=trash_img,
                    dark_image=trash_img,
                    size=(20, 20)
                )
                
                # Create reset button with icon
                self.reset_button = ctk.CTkButton(
                    master=self.utils_frame,
                    text="Reset",
                    font=self.fonts["default"],
                    image=self.images["trash"],
                    compound="left",
                    command=lambda: self.controller.show_page("general_settings"),
                )
            else:
                print(f"Warning: Icon file not found: {trash_icon_path}")
                # Fallback to button without icon
                self.reset_button = ctk.CTkButton(
                    master=self.utils_frame,
                    text="Reset",
                    font=self.fonts["default"],
                    command=lambda: self.controller.show_page("general_settings")
                )
        except Exception as e:
            print(f"Error creating reset button: {e}")
            # Fallback to button without icon
            self.reset_button = ctk.CTkButton(
                master=self.utils_frame,
                text="Reset",
                font=self.fonts["default"],
                command=lambda: self.controller.show_page("general_settings")
            )

        # Function to update widget visibility based on the current page
        def update_widget_visibility():
            # Make sure the navigation frame is properly positioned
            self.navigation_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
            self.utils_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
            
            # OptionMenu widgets placed in settings_inner_frame
            self.appearance_mode_label.grid(row=0, column=0, sticky="w", padx=5, pady=5, in_=self.settings_inner_frame)
            self.appearance_mode_optionemenu.grid(row=1, column=0, sticky="w", padx=5, pady=5, in_=self.settings_inner_frame)

            self.scaling_label.grid(row=0, column=1, sticky="w", padx=5, pady=5, in_=self.settings_inner_frame)
            self.scaling_optionemenu.grid(row=1, column=1, sticky="w", padx=5, pady=5, in_=self.settings_inner_frame)
            self.reset_button.grid(row=0, column=2, sticky="e", padx=10, in_=self.utils_frame)

        update_widget_visibility()  # Initial call to set visibility
        # Show the initial page and update visibility
        self.controller.show_page("general_settings")
    
    def load_image(self, path, size=None):
        """Safely load an image and store it in the images dictionary"""
        if not os.path.exists(path):
            print(f"Warning: Image file not found: {path}")
            return None
            
        try:
            img = Image.open(path)
            
            # Create a unique key based on the path and size
            key = f"{path}_{size}"
            
            # Store in the images dictionary to prevent garbage collection
            if size:
                self.images[key] = ctk.CTkImage(light_image=img, dark_image=img, size=size)
            else:
                self.images[key] = ctk.CTkImage(light_image=img, dark_image=img)
                
            return self.images[key]
        except Exception as e:
            print(f"Error loading image {path}: {e}")
            return None
    
    def change_appearance_mode(self, new_appearance_mode):
        """Change the appearance mode globally and update the stored setting"""
        ctk.set_appearance_mode(new_appearance_mode)
        
        # Update navigation state if needed
        if hasattr(self.navigation_frame, 'update_navigation_state') and self.controller.current_page:
            self.navigation_frame.update_navigation_state(self.controller.current_page)
    
    def change_scaling_event(self, new_scaling: str):
        """Change the UI scaling globally"""
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        ctk.set_widget_scaling(new_scaling_float)