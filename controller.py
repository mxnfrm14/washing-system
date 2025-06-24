import customtkinter as ctk
import json
import os
from datetime import datetime
import uuid

class PageController:
    def __init__(self, container, app):
        self.container = container
        self.app = app
        self.pages = {}
        self.current_page = None
        self.navigation_menu = None
        # Track completed pages
        self.completed_pages = set()
        
        # Get fonts from app if available
        self.fonts = getattr(app, 'fonts', {})

        self.config_data = {
            "general_settings": {},
            "washing_components": [],
            "pumps": [],
            "circuits": [],
            "sequences": {}
        }
        
        # Configuration file path
        self.config_file = "washing_system_config.json"
    
    def set_navigation_menu(self, navigation_menu):
        """Set the navigation menu for this controller"""
        self.navigation_menu = navigation_menu
    
    def add_page(self, name, page_class):
        """Add a page to the controller"""
        try:
            # Create the page instance
            page = page_class(self.container, self)
            
            # Pass fonts to the page if available
            if hasattr(page, 'fonts') and self.fonts:
                page.fonts = self.fonts
            
            # Pass app reference to the page if it has an app attribute
            if hasattr(page, 'app'):
                page.app = self.app
            
            # Add the page to our dictionary
            self.pages[name] = page
            
            # Configure the grid for this page
            page.grid(row=0, column=0, sticky="nsew")
            
            return page
        except Exception as e:
            print(f"Error adding page {name}: {e}")
            return None

    def mark_page_completed(self, page_name):
        """Mark a page as completed and update the navigation menu"""
        if page_name in self.pages:
            self.completed_pages.add(page_name)
            # Update navigation menu if available
            if self.navigation_menu and hasattr(self.navigation_menu, 'update_completion_status'):
                self.navigation_menu.update_completion_status(page_name)
            return True
        return False
    
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

    def show_page(self, page_name):
        """Show the specified page and trigger the page change callback."""
        if page_name in self.pages:
            try:
                # Save current page configuration before switching
                self.save_current_page_config()
                
                # Get the page and bring it to the front
                page = self.pages[page_name]
                page.tkraise()
                
                # Update the current page
                self.current_page = page_name
                
                # Load configuration for the new page (this will refresh circuits page)
                self.load_page_config(page_name)
                
                # Special handling for pages that need refreshing
                if page_name == "circuits" and hasattr(page, 'refresh_configuration'):
                    page.refresh_configuration()

                if page_name == "sequence" and hasattr(page, 'refresh_configuration'):
                    page.refresh_configuration()
                
                # Update navigation menu if available
                if self.navigation_menu and hasattr(self.navigation_menu, 'update_navigation_state'):
                    try:
                        self.navigation_menu.update_navigation_state(page_name)
                    except Exception as e:
                        print(f"Error updating navigation menu: {e}")
                
            except Exception as e:
                print(f"Error showing page {page_name}: {e}")
                return False
        else:
            print(f"Page not found: {page_name}")
            return False

    def save_current_page_config(self):
        """Save the current configuration when changing pages"""
        if not self.current_page or self.current_page not in self.pages:
            return
            
        page = self.pages[self.current_page]
        
        try:
            if self.current_page == "general_settings":
                if hasattr(page, 'get_configuration'):
                    self.config_data["general_settings"] = page.get_configuration()
                    
            elif self.current_page == "washing_components":
                if hasattr(page, 'get_configuration'):
                    components = page.get_configuration()
                    # Ensure each component has an ID
                    for component in components:
                        if isinstance(component, dict) and 'id' not in component:
                            component['id'] = f"component_{uuid.uuid4().hex[:8]}"
                    self.config_data["washing_components"] = components
                    
            elif self.current_page == "pumps":
                if hasattr(page, 'get_configuration'):
                    pumps = page.get_configuration()
                    # Ensure each pump has an ID
                    for pump in pumps:
                        if isinstance(pump, dict) and 'id' not in pump:
                            pump['id'] = f"pump_{uuid.uuid4().hex[:8]}"
                    self.config_data["pumps"] = pumps
                    
            elif self.current_page == "circuits":
                if hasattr(page, 'get_configuration'):
                    self.config_data["circuits"] = page.get_configuration()
                    
            elif self.current_page == "sequence":
                if hasattr(page, 'get_configuration'):
                    self.config_data["sequences"] = page.get_configuration()
                    
            print(f"Saved configuration for {self.current_page}: {len(self.config_data.get(self.current_page, []))} items")
            
        except Exception as e:
            print(f"Error saving configuration for {self.current_page}: {e}")
    
    def load_page_config(self, page_name):
        """Load configuration for a page that depends on previous pages"""
        if page_name not in self.pages:
            return
            
        page = self.pages[page_name]
        
        try:
            if page_name == "circuits":
                # Circuits page needs data from general_settings, washing_components, and pumps
                circuit_config = {
                    "general_settings": self.config_data["general_settings"],
                    "washing_components": self.config_data["washing_components"],
                    "pumps": self.config_data["pumps"]
                }
                if hasattr(page, 'load_configuration'):
                    page.load_configuration(circuit_config)
                    
            elif page_name == "sequence":
                # Sequences page needs data from previous pages
                sequence_config = {
                    "general_settings": self.config_data["general_settings"],
                    "washing_components": self.config_data["washing_components"],
                    "pumps": self.config_data["pumps"],
                    "circuits": self.config_data["circuits"]
                }
                if hasattr(page, 'load_configuration'):
                    page.load_configuration(sequence_config)
                    
            elif page_name == "results":
                # Results page needs all previous data
                if hasattr(page, 'load_configuration'):
                    page.load_configuration(self.config_data)
                    
        except Exception as e:
            print(f"Error loading configuration for {page_name}: {e}")

    def save_whole_configuration(self):
        """Save the whole configuration to disk"""
        try:
            # Save current page before saving to file
            self.save_current_page_config()
            
            # Add metadata
            config_with_metadata = {
                "timestamp": str(datetime.now()),
                "configuration": self.config_data
            }
            
            # Save to file
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_with_metadata, f, indent=2, ensure_ascii=False)
            
            print(f"Configuration saved to {self.config_file}")
            return True
            
        except Exception as e:
            print(f"Error saving configuration to file: {e}")
            return False
    
    def load_whole_configuration(self):
        """Load the whole configuration from disk"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                if "configuration" in data:
                    self.config_data = data["configuration"]
                    print(f"Configuration loaded from {self.config_file}")
                    return True
        except Exception as e:
            print(f"Error loading configuration from file: {e}")
        
        return False
    
    def get_config_data(self, section=None):
        """Get configuration data for a specific section or all data"""
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