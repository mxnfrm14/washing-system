import customtkinter as ctk
from utils.appearance_manager import AppearanceManager


class NavigationMenu(ctk.CTkFrame):
    def __init__(self, parent, controller, appearance_mode):
        super().__init__(parent)
        self.controller = controller
        self.current_page = None
        AppearanceManager.register(self)
        print(appearance_mode)
        self.update_appearance(appearance_mode)
        
        # Keep references to all images
        self.images = {}
        
        # Page mapping - key: page_name, value: (display_name, page_index)
        self.pages = {
            "general_settings": ("General Settings", 0),
            "washing_components": ("Washing Components", 1),
            "pumps": ("Pumps", 2),
            "circuits": ("Circuits", 3),
            "sequence": ("Sequence", 4),
            "results": ("Results", 5)
        }
        
        # Store indicator buttons
        self.indicators = []
    
    def create_nav_indicators(self):
        """Create navigation indicators with circular buttons"""
        # Main frame for indicators
        self.nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.nav_frame.pack(padx=30, pady=10, anchor="center")
        
        # Clear any existing indicators to prevent duplicates
        for indicator in self.indicators:
            if indicator.winfo_exists():
                indicator.destroy()
        self.indicators.clear()
        
        # Create indicator for each page
        for page_name, (display_name, index) in self.pages.items():
            # Create indicator frame with proper callback that saves before switching
            indicator = CircleIndicator(
                self.nav_frame, 
                text=display_name,
                index=index,
                callback=lambda p=page_name: self.navigate_to_page(p),
                controller=self.controller
            )
            indicator.grid(row=0, column=index, padx=30,)
            self.indicators.append(indicator)
        
        # Set initial active indicator
        if self.current_page and self.current_page in self.pages:
            self.set_active_indicator(self.pages[self.current_page][1])
        else:
            # Default to first indicator
            self.set_active_indicator(0)
    
    def navigate_to_page(self, page_name):
        """Navigate to a page after saving current page configuration"""
        try:
            # First check if the current page has a leave method to verify completion
            if self.controller.current_page and self.controller.current_page in self.controller.pages:
                current_page = self.controller.pages[self.controller.current_page]
                if hasattr(current_page, 'on_leave_page'):
                    current_page.on_leave_page()
            
            # Save current page configuration before switching
            if hasattr(self.controller, 'save_current_page_config'):
                self.controller.save_current_page_config()
                print(f"Configuration saved before navigating from {self.controller.current_page} to {page_name}")
            
            # Navigate to the new page
            if hasattr(self.controller, 'show_page'):
                self.controller.show_page(page_name)
                
                # Check if the new page should verify its completion status
                if page_name in self.controller.pages:
                    new_page = self.controller.pages[page_name]
                    if hasattr(new_page, 'on_show_page'):
                        new_page.on_show_page()
            
        except Exception as e:
            print(f"Error navigating to page {page_name}: {e}")
    
    def set_active_indicator(self, index):
        """Set active indicator based on index"""
        for i, indicator in enumerate(self.indicators):
            if i == index:
                indicator.set_active()
            else:
                indicator.set_inactive()
    
    def update_completion_status(self, page_name):
        """Update the completion status of a page indicator"""
        if page_name in self.pages:
            index = self.pages[page_name][1]
            if 0 <= index < len(self.indicators):
                # Set the indicator as completed
                self.indicators[index].set_completed()
                print(f"Page {page_name} marked as completed in navigation menu")

    def update_incomplete_status(self, page_name):
        """Update the completion status of a page indicator to incomplete"""
        if page_name in self.pages:
            index = self.pages[page_name][1]
            if 0 <= index < len(self.indicators):
                # Set the indicator as inactive (incomplete)
                self.indicators[index].set_inactive()
                print(f"Page {page_name} marked as incomplete in navigation menu")
    
    def update_navigation_state(self, current_page):
        """Update navigation state based on current page"""
        if current_page in self.pages:
            index = self.pages[current_page][1]
            
            # First check with the controller if the page is marked as completed
            is_completed = False
            if hasattr(self.controller, 'completed_pages'):
                is_completed = current_page in self.controller.completed_pages
            
            # Set the appropriate state based on completion status
            if is_completed:
                self.indicators[index].set_completed()
            else:
                # If not completed, set it as active
                self.set_active_indicator(index)
            
            self.current_page = current_page
            
            # Update all other indicators based on controller's completed_pages
            if hasattr(self.controller, 'completed_pages'):
                for page, (_, page_index) in self.pages.items():
                    # Skip the current page as we already handled it
                    if page == current_page:
                        continue
                    
                    # If page is completed, mark it as completed
                    if page in self.controller.completed_pages:
                        self.indicators[page_index].set_completed()
                    # If page is not current and not completed, ensure it's inactive
                    elif page_index != index:
                        self.indicators[page_index].set_inactive()
    
    def refresh_all_completion_status(self):
        """Refresh all indicators based on current completion status from controller"""
        if not hasattr(self.controller, 'completed_pages'):
            return
        
        # Update all indicators based on controller's completed_pages
        for page_name, (_, page_index) in self.pages.items():
            if page_name in self.controller.completed_pages:
                self.indicators[page_index].set_completed()
                print(f"Navigation menu: Page {page_name} set as completed")
            else:
                # If this is the current page, set it as active, otherwise inactive
                if page_name == self.current_page:
                    self.indicators[page_index].set_active()
                else:
                    self.indicators[page_index].set_inactive()

    def update_appearance(self, appearance_mode):
        """Update the appearance of the navigation frame based on the appearance mode"""
        self.appearance_mode = appearance_mode
        
        # Get the actual appearance mode (important for "System" setting)
        actual_mode = ctk.get_appearance_mode()
        
        # Update frame color based on actual appearance mode
        self.configure(fg_color="#1A296C" if actual_mode == "Dark" else "#FFFFFF")
        
        # Update indicators if they exist and are not empty
        if hasattr(self, 'indicators') and self.indicators:
            for indicator in self.indicators:
                if hasattr(indicator, 'set_active') and indicator.active:
                    indicator.set_active()
                elif hasattr(indicator, 'set_inactive'):
                    indicator.set_inactive()


class CircleIndicator(ctk.CTkFrame):
    """Circle indicator for navigation menu"""
    
    def __init__(self, parent, text, index, callback, controller=None):
        super().__init__(parent, fg_color="transparent")
        self.index = index
        self.callback = callback
        self.active = False
        self.completed = False
        self.controller = controller
        
        # Create circle button that will handle the visual states
        self.circle_button = ctk.CTkButton(
            self,
            text="",
            width=26,
            height=26,
            corner_radius=20,
            fg_color="transparent",
            border_width=2,
            hover=False  # Disable hover effect
        )
        self.circle_button.grid(row=0, column=0, padx=5, pady=5)
        
        # Label for the indicator
        if controller and hasattr(controller, 'fonts') and controller.fonts.get("default"):
            self.label = ctk.CTkLabel(self, text=text, font=controller.fonts.get("default"))
        else:
            self.label = ctk.CTkLabel(self, text=text)
        
        self.label.grid(row=1, column=0, pady=(0, 5))
        
        # Bind click events with error handling
        self.bind_click_events()
        
        # Set initial state
        self.set_inactive()
    
    def bind_click_events(self):
        """Safely bind click events to all components"""
        try:
            self.circle_button.configure(command=self.safe_callback)
            self.label.bind("<Button-1>", lambda e: self.safe_callback())
        except Exception as e:
            print(f"Error binding click events: {e}")
    
    def safe_callback(self):
        """Execute callback with error handling"""
        try:
            if callable(self.callback):
                self.callback()
        except Exception as e:
            print(f"Error in indicator callback: {e}")
    
    def set_active(self):
        """Set this indicator as active - filled circle"""
        self.active = True
        self.completed = False
        try:
            # Get the appropriate color based on theme
            fill_color = "#F8F8F8" if ctk.get_appearance_mode() == "Dark" else "#243783"
            
            # Fill the circle
            self.circle_button.configure(
                fg_color=fill_color,
                border_width=0,
                text="",
                text_color=fill_color
            )
        except Exception as e:
            print(f"Error setting active state: {e}")
    
    def set_inactive(self):
        """Set this indicator as inactive - bordered circle only"""
        self.active = False
        try:
            # Get the appropriate border color based on theme
            border_color = "#F8F8F8" if ctk.get_appearance_mode() == "Dark" else "#243783"
            
            # Create border effect
            self.circle_button.configure(
                fg_color="transparent",
                border_width=2,
                border_color=border_color,
                text="",
                text_color=border_color
            )
        except Exception as e:
            print(f"Error setting inactive state: {e}")
    
    def set_completed(self):
        """Mark this indicator as completed"""
        self.completed = True
        self.active = False
        try:
            self.circle_button.configure(
                fg_color="#4CAF50",
                border_width=0,
                text="✓",
                text_color="#FFFFFF",
                font=("Arial", 16, "bold")
            )
        except Exception as e:
            print(f"Error setting completed state: {e}")