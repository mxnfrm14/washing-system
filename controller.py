import customtkinter as ctk

class PageController:
    def __init__(self, container, app):
        self.container = container
        self.app = app
        self.pages = {}
        self.current_page = None
        self.page_change_callback = None
        self.navigation_menu = None
        
        # Get fonts from app if available
        self.fonts = getattr(app, 'fonts', {})
    
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

    def show_page(self, page_name):
        """Show the specified page and trigger the page change callback."""
        if page_name in self.pages:
            try:
                # Get the page and bring it to the front
                page = self.pages[page_name]
                page.tkraise()
                
                # Update the current page
                self.current_page = page_name
                
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