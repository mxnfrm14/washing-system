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
                 icon_side="left", outlined=False, command=None, height=36, 
                 custom_fg_color=None, custom_text_color=None, custom_hover_color=None,
                 custom_border_color=None, **kwargs):
        self.icon_path = icon_path
        self.icon_size = icon_size
        self.outlined = outlined
        self.icon_side = icon_side
        self.icon = None
        
        # Store custom colors and flag
        self.custom_fg_color = custom_fg_color
        self.custom_text_color = custom_text_color
        self.custom_hover_color = custom_hover_color
        self.custom_border_color = custom_border_color
        self.use_custom_colors = any([custom_fg_color, custom_text_color, custom_hover_color, custom_border_color])
        
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
        
        # Remove height from kwargs to avoid duplicate param error
        if 'height' in kwargs_copy:
            height = kwargs_copy.pop('height')
        else:
            height = 36  # Default height

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
            height=height,
            **kwargs_copy
        )
        
        # Register with appearance manager
        AppearanceManager.register(self)
    
    def _set_colors(self):
        """Set colors based on appearance mode or use custom colors"""
        if self.use_custom_colors:
            # Use custom colors if provided, otherwise fall back to defaults
            mode = ctk.get_appearance_mode()
            
            # Set default colors first
            if mode == "Dark":
                default_hover = "#C8C8C8" if self.outlined else "#D0D0D0"
                default_text = "#F8F8F8" if self.outlined else "#243783"
                default_border = "#F8F8F8"
                default_fg = "transparent" if self.outlined else "#F8F8F8"
            else:
                default_hover = "#8995C6" if self.outlined else "#12205C"
                default_text = "#243783" if self.outlined else "#F8F8F8"
                default_border = "#243783"
                default_fg = "transparent" if self.outlined else "#243783"
            
            # Use custom colors or fall back to defaults
            self.hover_color = self.custom_hover_color or default_hover
            self.text_color = self.custom_text_color or default_text
            self.border_color = self.custom_border_color or default_border
            self.fg_color = self.custom_fg_color or default_fg
        else:
            # Original color logic for non-custom buttons
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
        # Skip color updates if using custom colors
        if not self.use_custom_colors:
            self._set_colors()
            
            # Update button properties
            self.configure(
                fg_color=self.fg_color,
                border_color=self.border_color,
                border_width=2 if self.outlined else 0,
                text_color=self.text_color,
                hover_color=self.hover_color
            )
        
        # Always update icon (icon color might still need to change based on text color)
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