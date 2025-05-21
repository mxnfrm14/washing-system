import customtkinter as ctk
from utils.appearance_manager import AppearanceManager

class PrioritySelector(ctk.CTkFrame):
    """
    Custom priority selector component that functions like a switch/radio button.
    Allows selecting between Prioritary (P) and Secondary (S) options.
    """
    def __init__(
        self, 
        master, 
        command=None, 
        initial_value="P",
        width=90,
        height=30,
        **kwargs
    ):
        super().__init__(master, fg_color="transparent", width=width, height=height, **kwargs)
        
        self.command = command
        self.value = initial_value  # "P" or "S"
        self.width = width
        self.height = height
        
        # Initialize button color attributes
        self.p_fg_color = None
        self.p_text_color = None
        self.p_hover_color = None
        self.s_fg_color = None
        self.s_text_color = None
        self.s_hover_color = None
        
        # Create container frame
        self.container = ctk.CTkFrame(self, fg_color="transparent", width=width, height=height)
        self.container.pack(fill="both", expand=True)
        
        # Configure grid for the two buttons (2 columns)
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_columnconfigure(1, weight=1)
        self.container.grid_rowconfigure(0, weight=1)
        
        # Get colors for initial setup
        self._set_colors()
        
        # Set initial button colors based on initial_value
        if initial_value == "P":
            self.p_fg_color = self.active_fg
            self.p_text_color = self.active_text
            self.p_hover_color = self.active_hover
            self.s_fg_color = self.inactive_fg
            self.s_text_color = self.inactive_text
            self.s_hover_color = self.inactive_hover
        else:
            self.p_fg_color = self.inactive_fg
            self.p_text_color = self.inactive_text
            self.p_hover_color = self.inactive_hover
            self.s_fg_color = self.active_fg
            self.s_text_color = self.active_text
            self.s_hover_color = self.active_hover
        
        # Create priority buttons
        self.p_button = ctk.CTkButton(
            self.container,
            text="P",
            width=width // 2,
            height=height,
            corner_radius=12,
            border_width=0,
            command=lambda: self.select("P"),
            fg_color=self.p_fg_color,
            hover_color=self.p_hover_color,
            text_color=self.p_text_color
        )
        self.p_button.grid(row=0, column=0, sticky="nsew")
        
        self.s_button = ctk.CTkButton(
            self.container,
            text="S",
            width=width // 2,
            height=height,
            corner_radius=12,
            border_width=0,
            command=lambda: self.select("S"),
            fg_color=self.s_fg_color,
            hover_color=self.s_hover_color,
            text_color=self.s_text_color
        )
        self.s_button.grid(row=0, column=1, sticky="nsew")
        
        # Register with appearance manager for theme changes
        AppearanceManager.register(self)
    
    def _set_colors(self):
        """Set colors based on appearance mode"""
        mode = ctk.get_appearance_mode()
        
        if mode == "Dark":
            # Dark mode colors
            self.active_fg = "#243783"  # Blue background for active
            self.active_text = "#F8F8F8"  # White text for active
            self.active_hover = "#2A4090"  # Slightly lighter blue for hover
            
            self.inactive_fg = "#E8E8E8"  # Dark gray background for inactive 3A3A3A
            self.inactive_text = "#243783"  # White text for inactive F8F8F8
            self.inactive_hover = "#D0D0D0"  # Slightly lighter gray for hover 4A4A4A
        else:
            # Light mode colors
            self.active_fg = "#243783"  # Blue background for active
            self.active_text = "#F8F8F8"  # White text for active
            self.active_hover = "#2A4090"  # Slightly lighter blue for hover
            
            self.inactive_fg = "#E8E8E8"  # Light gray background for inactive
            self.inactive_text = "#243783"  # Blue text for inactive
            self.inactive_hover = "#D0D0D0"  # Slightly darker gray for hover
    
    def select(self, value, call_command=True):
        """Select the priority (P or S) and update the appearance"""
        if value not in ["P", "S"]:
            return
        
        self.value = value
        
        # Set colors based on selection
        if value == "P":
            self.p_fg_color = self.active_fg
            self.p_text_color = self.active_text
            self.p_hover_color = self.active_hover
            
            self.s_fg_color = self.inactive_fg
            self.s_text_color = self.inactive_text
            self.s_hover_color = self.inactive_hover
        else:  # value == "S"
            self.p_fg_color = self.inactive_fg
            self.p_text_color = self.inactive_text
            self.p_hover_color = self.inactive_hover
            
            self.s_fg_color = self.active_fg
            self.s_text_color = self.active_text
            self.s_hover_color = self.active_hover
        
        # Update button appearances
        self.p_button.configure(
            fg_color=self.p_fg_color,
            text_color=self.p_text_color,
            hover_color=self.p_hover_color
        )
        
        self.s_button.configure(
            fg_color=self.s_fg_color,
            text_color=self.s_text_color,
            hover_color=self.s_hover_color
        )
        
        # Call command if provided and requested
        if call_command and self.command:
            self.command(value)
    
    def get(self):
        """Get the current priority value"""
        return self.value
    
    def set(self, value):
        """Set the priority value programmatically"""
        self.select(value)
    
    def update_appearance(self, mode=None):
        """Update appearance when theme changes"""
        self._set_colors()
        # Re-apply current selection with the new colors
        self.select(self.value, call_command=False)
    
    def destroy(self):
        """Clean up when destroying the widget"""
        # Unregister from appearance manager
        AppearanceManager.unregister(self)
        super().destroy()