import customtkinter as ctk
import os
from utils.appearance_manager import AppearanceManager
from utils.open_image import open_icon
import weakref

class CustomButton(ctk.CTkButton):
    """Enhanced button with icon support and outlined variant"""
    # Instead of a list, use a weak reference set to avoid memory leaks
    _instances = weakref.WeakSet()
    
    @classmethod
    def clear_all_instances(cls):
        """Clear all button instances"""
        cls._instances.clear()
        
    def __init__(self, master, text, font=None, icon_path=None, icon_size=(20, 20), 
                 icon_side="left", outlined=False, command=None, **kwargs):
        self.icon_path = icon_path
        self.icon_size = icon_size
        self.outlined = outlined
        self.icon_side = icon_side
        self.icon = None
        
        if font is None:
            font = ctk.CTkFont(family="Encode Sans Expanded", size=14, weight="normal")

        # Set colors based on current appearance
        self._set_colors()
        
        # Make a deep copy of kwargs to avoid modifying the original
        kwargs_copy = kwargs.copy()
        
        # Load icon safely
        if self.icon_path:
            self._load_icon()
            if self.icon:
                kwargs_copy["image"] = self.icon
        
        # Set compound parameter only if not provided and we have an icon
        if "compound" not in kwargs_copy:
            kwargs_copy["compound"] = self.icon_side if self.icon else "center"
        
        # Initialize button with safe parameters
        super().__init__(
            master=master,
            text=text,
            font=font,
            fg_color=self.fg_color,
            border_color=self.border_color,
            border_width=2 if self.outlined else 0,
            corner_radius=6,
            text_color=self.text_color,
            hover_color=self.hover_color,
            command=command,
            height=36,
            **kwargs_copy
        )
        
        # Register with appearance manager
        AppearanceManager.register(self)
    
    def _set_colors(self):
        """Set colors based on appearance mode"""
        mode = ctk.get_appearance_mode()
        
        if mode == "Dark":
            self.hover_color = "#C8C8C8" if self.outlined else "#D0D0D0"
            self.text_color = "#F8F8F8" if self.outlined else "#243783"
            self.border_color = "#F8F8F8"
            self.fg_color = "transparent" if self.outlined else "#F8F8F8"
        else:
            self.hover_color = "#8995C6" if self.outlined else "#12205C"
            self.text_color = "#243783" if self.outlined else "#F8F8F8"
            self.border_color = "#243783"
            self.fg_color = "transparent" if self.outlined else "#243783"
    
    def _load_icon(self):
        """Load and tint the icon"""
        try:
            if os.path.exists(self.icon_path):
                self.icon = open_icon(self.icon_path, self.icon_size, tint_color=self.text_color)
            else:
                print(f"WARNING: Icon path does not exist: {self.icon_path}")
                self.icon = None
        except Exception as e:
            print(f"Error loading icon {self.icon_path}: {e}")
            self.icon = None
    
    def update_appearance(self, mode=None):
        """Update for appearance mode changes"""
        self._set_colors()
        
        # Update button properties
        self.configure(
            fg_color=self.fg_color,
            border_color=self.border_color,
            border_width=2 if self.outlined else 0,
            text_color=self.text_color,
            hover_color=self.hover_color
        )
        
        # Update icon
        if self.icon_path:
            old_icon = self.icon
            self._load_icon()
            if self.icon and self.icon != old_icon:
                self.configure(image=self.icon)
    
    def destroy(self):
        """Clean up when destroying the widget"""
        # Unregister from appearance manager
        AppearanceManager.unregister(self)
        super().destroy()