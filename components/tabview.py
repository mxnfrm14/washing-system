import customtkinter as ctk

class ThemedTabview(ctk.CTkFrame):
    """
    Custom tabview implementation with modern styling that matches your design
    """
    def __init__(self, parent, width=700, height=400, **kwargs):
        # Use white/light background for the entire component
        super().__init__(parent)
        
        self.width = width
        self.height = height
        
        # Create header frame with proper styling
        self.header_frame = ctk.CTkFrame(
            self, 
            height=30,
            fg_color="transparent",
            corner_radius=8
        )
        self.header_frame.pack(fill="x", padx=(10,0), pady=(0, 0))  # No padding, positioned at top
        
        # Create the tab button container with rounded corners
        self.tab_button_frame = ctk.CTkFrame(
            self.header_frame,
            fg_color=("#F8F8F8", "#243783"),
            corner_radius=10,
            height=30
        )
        self.tab_button_frame.pack(side="left", padx=5, pady=5)  # Small padding from left edge
        
        # Create content area that takes full space
        self.content_container = ctk.CTkFrame(
            self,
            fg_color=("#F3F3F3", "#243783"),
            corner_radius=8,
        )
        self.content_container.pack(fill="both", expand=True, padx=0, pady=0)  # No padding, full space
        
        # Inner content frame (where tab content goes) - takes full space
        self.content_frame = ctk.CTkFrame(
            self.content_container,
            fg_color="transparent",
            corner_radius=8,
            border_color="#898989",
            border_width=1
        )
        self.content_frame.pack(fill="both", expand=True, padx=0, pady=0)  # Full space
        
        # Tab management
        self.tabs = {}
        self.tab_buttons = {}
        self.current_tab = None
        self.tab_count = 0
        
        # Start appearance monitoring
        self._appearance_mode = ctk.get_appearance_mode()
        self._check_appearance_mode()
    
    def _get_colors(self):
        """Get theme colors based on appearance mode"""
        mode = ctk.get_appearance_mode()
        
        if mode == "Dark":
            return {
                # Selected tab - blue with white text
                "selected_bg": "#243783",
                "selected_text": "#F8F8F8",
                "selected_hover": "#2F4590",
                
                # Unselected tab - transparent/light with dark text
                "unselected_bg": "transparent",
                "unselected_text": "#6B7280",
                "unselected_hover": "#F3F4F6",
                
                # Container colors
                "tab_container_bg": "#F8F8F8",
                "content_bg": "#243783",
                "main_bg": "#243783"
            }
        else:
            return {
                # Selected tab - blue with white text
                "selected_bg": "#243783",
                "selected_text": "#F8F8F8", 
                "selected_hover": "#2F4590",
                
                # Unselected tab - transparent with dark text
                "unselected_bg": "transparent",
                "unselected_text": "#6B7280",
                "unselected_hover": "#F3F4F6",
                
                # Container colors
                "tab_container_bg": "#F3F3F3",
                "content_bg": "#F8F8F8",
                "main_bg": "#F8F8F8"
            }
    
    def add(self, name):
        """Add a new tab with modern styling"""
        # Create content frame for this tab - full space
        tab_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent", corner_radius=8, border_color="#898989", border_width=1)
        self.tabs[name] = tab_frame
        
        # Determine if this is the first or last tab for proper corner radius
        is_first = len(self.tabs) == 1
        is_last = True  # This will be updated when new tabs are added
        
        # Update previous last tab to not be last anymore
        if self.tab_count > 0:
            for btn_name, btn in self.tab_buttons.items():
                if hasattr(btn, '_is_last'):
                    btn._is_last = False
        
        # Create styled tab button
        colors = self._get_colors()
        button = ctk.CTkButton(
            self.tab_button_frame,
            text=name,
            height=24,
            corner_radius=8,
            border_width=0,
            font=ctk.CTkFont(size=13, weight="normal"),
            command=lambda: self.set(name)
        )
        
        # Store position info
        button._is_first = is_first
        button._is_last = is_last
        
        # Pack with appropriate padding
        if is_first:
            button.pack(side="left", padx=(3, 1), pady=2)
        else:
            button.pack(side="left", padx=(1,3), pady=2)
        
        self.tab_buttons[name] = button
        self.tab_count += 1
        
        # Update all button colors
        self._update_button_colors()
        
        # Select first tab automatically
        if self.current_tab is None:
            self.set(name)
        
        return tab_frame
    
    def set(self, name):
        """Select a tab with modern animation feel"""
        if name not in self.tabs:
            return
            
        # Hide all content frames
        for frame in self.tabs.values():
            frame.pack_forget()
        
        # Show selected tab's content - full space
        self.tabs[name].pack(fill="both", expand=True, padx=0, pady=0)
        self.current_tab = name
        
        # Update all button colors and styles
        self._update_button_colors()
    
    def _update_button_colors(self):
        """Update button colors with modern styling"""
        colors = self._get_colors()
        
        # Update container backgrounds
        self.configure(fg_color=colors["main_bg"])
        self.tab_button_frame.configure(fg_color=colors["tab_container_bg"])
        self.content_container.configure(fg_color=colors["content_bg"])
        
        # Update each button
        for tab_name, button in self.tab_buttons.items():
            if tab_name == self.current_tab:
                # Selected state - blue background, white text
                button.configure(
                    fg_color=colors["selected_bg"],
                    text_color=colors["selected_text"],
                    hover_color=colors["selected_hover"],
                    font=ctk.CTkFont(size=13, weight="bold")
                )
            else:
                # Unselected state - transparent, gray text
                button.configure(
                    fg_color=colors["unselected_bg"],
                    text_color=colors["unselected_text"],
                    hover_color=colors["unselected_hover"],
                    font=ctk.CTkFont(size=13, weight="normal")
                )
    
    def destroy(self):
        """Clean up resources when destroying the widget"""
        try:
            if hasattr(self, '_after_id'):
                self.after_cancel(self._after_id)
        except Exception:
            pass
        super().destroy()
    
    def _check_appearance_mode(self):
        """Monitor appearance mode changes"""
        try:
            if not self.winfo_exists():
                return
                
            current_mode = ctk.get_appearance_mode()
            if current_mode != self._appearance_mode:
                self._appearance_mode = current_mode
                self._update_button_colors()
            
            # Instead of scheduling directly, store the after ID
            if hasattr(self, '_after_id'):
                try:
                    self.after_cancel(self._after_id)
                except Exception:
                    pass
            
            self._after_id = self.after(200, self._check_appearance_mode)
        except Exception:
            pass
    
    def tab(self, name):
        """Get a tab frame by name"""
        return self.tabs.get(name)
    
    def get(self):
        """Get current tab name"""
        return self.current_tab
    
    def configure(self, **kwargs):
        """Configure the tabview"""
        super().configure(**kwargs)