import customtkinter as ctk

class NavigationMenu(ctk.CTkFrame):
    def __init__(self, parent, controller, current_page=None):
        super().__init__(parent)
        self.controller = controller
        self.current_page = current_page
        
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

        #test
        self.test_label = ctk.CTkLabel(self, text="Test Label", font=controller.fonts.get("default", None))
        self.test_label.pack(pady=10)
        
        # Create the navigation indicators
        #self.create_nav_indicators()
    
    def create_nav_indicators(self):
        """Create navigation indicators with circular buttons"""
        # Main frame for indicators
        self.nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.nav_frame.pack(fill="x", padx=20, pady=10)
        
        # Create indicator for each page
        for page_name, (display_name, index) in self.pages.items():
            # Create indicator frame
            indicator = CircleIndicator(
                self.nav_frame, 
                text=display_name,
                index=index,
                callback=lambda p=page_name: self.controller.show_page(p)
            )
            indicator.grid(row=0, column=index, padx=30)
            self.indicators.append(indicator)
        
        # Default active indicator
        if self.current_page and self.current_page in self.pages:
            self.set_active_indicator(self.pages[self.current_page][1])
        else:
            # Default to first indicator
            self.set_active_indicator(0)
    
    def set_active_indicator(self, index):
        """Set active indicator based on index"""
        for i, indicator in enumerate(self.indicators):
            if i == index:
                indicator.set_active()
            else:
                indicator.set_inactive()
    
    def update_navigation_state(self, current_page):
        """Update navigation state based on current page"""
        if current_page in self.pages:
            index = self.pages[current_page][1]
            self.set_active_indicator(index)
            self.current_page = current_page


class CircleIndicator(ctk.CTkFrame):
    """Circle indicator for navigation menu"""
    
    def __init__(self, parent, text, index, callback):
        super().__init__(parent, fg_color="transparent")
        self.index = index
        self.callback = callback
        self.active = False
        self.completed = False
        
        # Create circle indicator
        self.circle_frame = ctk.CTkFrame(self, width=40, height=40, corner_radius=20)
        self.circle_frame.grid(row=0, column=0, padx=5, pady=5)
        self.circle_frame.grid_propagate(False)  # Maintain fixed size
        
        # Create inner circle that shows active/completed state
        self.inner_circle = ctk.CTkLabel(
            self.circle_frame,
            text="",
            width=36,
            height=36,
            corner_radius=18,
            fg_color="transparent",  # Default state
        )
        self.inner_circle.place(relx=0.5, rely=0.5, anchor="center")
        
        # Label for the indicator
        self.label = ctk.CTkLabel(self, text=text)
        self.label.grid(row=1, column=0, pady=(0, 5))
        
        # Bind click events
        self.circle_frame.bind("<Button-1>", lambda e: self.callback())
        self.inner_circle.bind("<Button-1>", lambda e: self.callback())
        self.label.bind("<Button-1>", lambda e: self.callback())
        
        # Set initial state
        self.set_inactive()
    
    def set_active(self):
        """Set this indicator as active"""
        self.active = True
        self.completed = False
        self.inner_circle.configure(
            fg_color="#F8F8F8" if ctk.get_appearance_mode() == "Dark" else "#243783",
            text_color="#243783" if ctk.get_appearance_mode() == "Dark" else "#F8F8F8",
            text=""
        )
    
    def set_inactive(self):
        """Set this indicator as inactive"""
        self.active = False
        self.inner_circle.configure(
            fg_color="transparent",
            text=""
        )
    
    def set_completed(self):
        """Mark this indicator as completed"""
        self.completed = True
        self.active = False
        self.inner_circle.configure(
            fg_color="#4CAF50",  # Green color for completion
            text="✓",
            text_color="#FFFFFF"
        )