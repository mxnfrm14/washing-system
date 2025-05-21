import customtkinter as ctk
from pages.welcome_window import WelcomeWindow
from app import App
from components.custom_button import CustomButton
import time

class AppController:
    """
    Controller that manages the application flow between
    the welcome screen and the main application
    """
    def __init__(self):
        # Initialize custom themes and appearance
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("theme.json")
        
        # Create the welcome window
        self.welcome_window = WelcomeWindow(self)
        
        # Main app reference (will be created later)
        self.main_app = None
    
    def start(self):
        """Start the application with the welcome window"""
        self.welcome_window.mainloop()
    
    def show_main_app(self):
        """Create and show the main application"""
        # from custom_button import CustomButton
        # CustomButton.clear_all_instances()
        
        # Hide the welcome window instead of destroying it
        if self.welcome_window:
             self.welcome_window.destroy()
            # self.welcome_window.withdraw() # Hide root window
            # self.welcome_window.quit() # End the mainloop and stop tcl interpreter commands
        
        # Create and show the main app
        self.main_app = App()
        self.main_app.mainloop()

    def on_main_app_close(self):
        """Handle main app close event"""
        # Destroy main app
        if self.main_app:
            self.main_app.destroy()
            self.main_app = None
        
        
    
    def load_configuration(self):
        """Load a configuration file from disk"""
        # Use a file dialog to select a configuration file
        filename = ctk.filedialog.askopenfilename(
            title="Load Configuration",
            filetypes=[("Configuration files", "*.json"), ("All files", "*.*")]
        )
        
        # If a file was selected, load it and start the main app
        if filename:
            # Here you would load the configuration
            # For now, just start the main app
            self.show_main_app()