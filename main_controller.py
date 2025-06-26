import customtkinter as ctk
import json
import os
from datetime import datetime
import uuid

from pages.welcome_window import WelcomeWindow
from app import App

class MainController:
    """
    A unified controller that manages the entire application lifecycle,
    from the welcome screen to page navigation and data management within the main app.
    """
    def __init__(self):
        # --- Initialization from AppController ---
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("theme.json")
        
        # --- Window references ---
        self.welcome_window = None
        self.main_app = None

        # --- State from PageController ---
        self.container = None  # This will be set when the main app is created
        self.pages = {}
        self.current_page = None
        self.navigation_menu = None
        self.completed_pages = set()
        self.fonts = {}  # This will be populated by the App instance

        # The single source of truth for all configuration data
        self.config_data = self._get_initial_config_data()
        self.config_file = "washing_system_config.json"

    def _get_initial_config_data(self):
        """Returns the default empty structure for the application's configuration data."""
        return {
            "general_settings": {},
            "washing_components": [],
            "pumps": [],
            "circuits": [],
            "sequences": {}
        }

    # --- Application Lifecycle Methods (Previously in AppController) ---

    def start(self):
        """Starts the application by showing the welcome window."""
        self.welcome_window = WelcomeWindow(self)
        self.welcome_window.mainloop()

    def handle_new_config_request(self):
        """Handles the user's choice to create a new configuration."""
        self.config_data = self._get_initial_config_data()
        if self.welcome_window:
            self.welcome_window.destroy()
        self._show_main_app()

    def handle_load_config_request(self):
        """Handles the user's choice to load a configuration from a file."""
        filename = ctk.filedialog.askopenfilename(
            title="Load Configuration",
            filetypes=[("Configuration files", "*.json"), ("All files", "*.*")]
        )
        
        if filename and self.load_whole_configuration(filename):
            if self.welcome_window:
                self.welcome_window.destroy()
            self._show_main_app()
        elif filename:
            # Optional: Show an error message if loading fails
            print(f"Failed to load configuration file: {filename}")

    def _show_main_app(self):
        """Creates and displays the main application window."""
        self.main_app = App(self)  # Pass this controller to the App
        self.main_app.mainloop()

    # --- Page & Data Management Methods (Previously in PageController) ---

    def set_container_and_fonts(self, container, fonts):
        """Called by the App to provide the page container and fonts."""
        self.container = container
        self.fonts = fonts

    def add_page(self, name, page_class):
        """Adds a page to the main application view."""
        if not self.container:
            print("Error: Container not set. Cannot add page.")
            return None
        
        page = page_class(self.container, self)
        if hasattr(page, 'fonts') and self.fonts:
            page.fonts = self.fonts
        
        self.pages[name] = page
        page.grid(row=0, column=0, sticky="nsew")
        return page

    def show_page(self, page_name):
        """Shows the specified page and saves the state of the previous one."""
        if page_name in self.pages:
            self.save_current_page_config()  # Save before switching
            
            page = self.pages[page_name]
            page.tkraise()
            self.current_page = page_name
            
            self.load_page_config(page_name) # Load new data for the page
            
            # Refresh pages that need it
            if page_name in ["circuits", "sequence"] and hasattr(page, 'refresh_configuration'):
                page.refresh_configuration()

            if self.navigation_menu and hasattr(self.navigation_menu, 'update_navigation_state'):
                self.navigation_menu.update_navigation_state(page_name)
        else:
            print(f"Page not found: {page_name}")

    def save_current_page_config(self):
        """Saves the configuration from the currently visible page."""
        if not self.current_page or self.current_page not in self.pages:
            return

        page = self.pages[self.current_page]
        if not hasattr(page, 'get_configuration'):
            return

        try:
            page_to_key_map = {
                "general_settings": "general_settings",
                "washing_components": "washing_components",
                "pumps": "pumps",
                "circuits": "circuits",
                "sequence": "sequences"
            }
            if self.current_page in page_to_key_map:
                data_key = page_to_key_map[self.current_page]
                data = page.get_configuration()
                
                # Add unique IDs if they are missing
                if data_key in ["washing_components", "pumps"]:
                    for item in data:
                        if isinstance(item, dict) and 'id' not in item:
                            item['id'] = f"{data_key[:-1]}_{uuid.uuid4().hex[:8]}"
                
                self.config_data[data_key] = data
        except Exception as e:
            print(f"Error saving config for {self.current_page}: {e}")

    def load_page_config(self, page_name):
        """Loads dependencies for pages that need data from others."""
        if page_name not in self.pages: return
        page = self.pages[page_name]

        config_to_load = None
        if page_name == "circuits":
            config_to_load = {
                "general_settings": self.get_config_data("general_settings"),
                "washing_components": self.get_config_data("washing_components"),
                "pumps": self.get_config_data("pumps")
            }
        elif page_name == "sequence":
            config_to_load = {
                "general_settings": self.get_config_data("general_settings"),
                "washing_components": self.get_config_data("washing_components"),
                "pumps": self.get_config_data("pumps"),
                "circuits": self.get_config_data("circuits")
            }
        elif page_name == "results":
            config_to_load = self.config_data

        if config_to_load and hasattr(page, 'load_configuration'):
            page.load_configuration(config_to_load)

    def save_whole_configuration(self):
        """Saves the entire configuration data object to a JSON file."""
        self.save_current_page_config() # Ensure current page is saved
        try:
            filepath = ctk.filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Save Configuration As..."
            )
            if not filepath:
                return False # User cancelled
            
            config_with_metadata = {
                "timestamp": str(datetime.now()),
                "configuration": self.config_data
            }
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(config_with_metadata, f, indent=2, ensure_ascii=False)
            print(f"Configuration saved to {filepath}")
            return True
        except Exception as e:
            print(f"Error saving configuration to file: {e}")
            return False

    def load_whole_configuration(self, filename):
        """Loads a complete configuration from a JSON file into the controller."""
        try:
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if "configuration" in data:
                    # Overwrite config_data with loaded data
                    self.config_data = data["configuration"]
                    # Ensure all keys exist to prevent future errors
                    for key, value in self._get_initial_config_data().items():
                        self.config_data.setdefault(key, value)
                    print(f"Configuration loaded from {filename}")
                    return True
        except Exception as e:
            print(f"Error loading configuration from file: {e}")
        return False

    def reset_app(self):
        """Resets the application data to its initial empty state."""
        self.config_data = self._get_initial_config_data()
        self.completed_pages.clear()
        
        # Reset all pages in the UI
        for page in self.pages.values():
            if hasattr(page, 'reset_app'): # Assuming pages have a 'reset_page' method
                page.reset_app()
        
        # Go back to the first page
        self.show_page("general_settings")
        print("Application data has been reset.")

    # --- Getters and other utility methods ---
    def get_config_data(self, section=None):
        """Gets a specific section of the config data or the whole object."""
        if section:
            return self.config_data.get(section, {})
        return self.config_data
    
    def update_config_data(self, section, data):
        """Update configuration data for a specific section"""
        self.config_data[section] = data
        print(f"Updated configuration for section: {section}")
    
    def save_circuit_config(self, circuits_data):
        """Save circuit configuration data"""
        self.config_data["circuits"] = circuits_data
        print(f"Saved circuit configuration to controller: {len(circuits_data)} circuits")
        
        # Also trigger a full save when circuits are saved via the save button
        self.save_whole_configuration()

    def set_navigation_menu(self, navigation_menu):
        """Stores a reference to the navigation menu."""
        self.navigation_menu = navigation_menu

    def mark_page_completed(self, page_name):
        """Marks a page as complete for UI feedback."""
        if page_name in self.pages:
            self.completed_pages.add(page_name)
            if self.navigation_menu:
                self.navigation_menu.update_completion_status(page_name)

    def mark_page_incomplete(self, page_name):
        """Mark a page as incomplete and update the navigation menu"""
        if page_name in self.completed_pages:
            self.completed_pages.remove(page_name)
            # Update navigation menu if available
            if self.navigation_menu and hasattr(self.navigation_menu, 'update_incomplete_status'):
                self.navigation_menu.update_incomplete_status(page_name)
            return True
        return False
    
    def is_page_completed(self, page_name):
        """Check if a page is marked as completed"""
        return page_name in self.completed_pages
