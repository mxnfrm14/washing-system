import customtkinter as ctk
from PIL import Image
import os

class CustomButton(ctk.CTkButton):
    """
    Enhanced button with icon support and outlined variant
    """
    # Class variable to track all button instances
    _instances = []
    
    def __init__(self, master, text, font=None, icon_path=None, icon_size=(20, 20), 
                 icon_side="left", outlined=False, command=None, **kwargs):
        self.icon_path = icon_path
        self.icon_size = icon_size
        self.outlined = outlined
        self.icon_side = icon_side
        self.icon = None
        self.original_icon = None
        
        # Keep track of this instance
        CustomButton._instances.append(self)
        
        # Set default appearance values
        self.update_colors()
        
        # Load the icon if a path is provided
        if self.icon_path and os.path.exists(self.icon_path):
            self.load_icon()
        
        # Initialize the button
        super().__init__(
            master=master,
            text=text,
            font=font,
            image=self.icon,
            compound=self.icon_side if self.icon else "center",
            fg_color=self.fg_color,
            border_color=self.border_color,
            border_width=2 if self.outlined else 0,
            corner_radius=6,
            text_color=self.text_color,
            hover_color=self.hover_color,
            command=command,
            **kwargs
        )
        
        # Track appearance mode changes
        self._appearance_mode = ctk.get_appearance_mode()
        self._check_appearance_mode_timer = self.after(100, self._check_appearance_mode)
    
    def load_icon(self):
        """Load the icon and create CTkImage"""
        try:
            # Load the original icon
            self.original_icon = Image.open(self.icon_path).convert("RGBA")
            self.create_icon()
        except Exception as e:
            print(f"Error loading icon {self.icon_path}: {e}")
            self.icon = None
    
    def create_icon(self):
        """Create the icon with current color"""
        if self.original_icon:
            self.tint_icon(self.text_color)

    def tint_icon(self, color_hex):
        """Tint the icon to match the given color"""
        if not self.original_icon:
            return None
            
        try:
            # Extract RGB values from hex color
            rgb = tuple(int(color_hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (255,)
            
            # Create overlay with specified color
            overlay = Image.new("RGBA", self.original_icon.size, rgb)
            
            # Get alpha channel from original icon
            r, g, b, a = self.original_icon.split()
            
            # Compose final image with alpha channel
            result = Image.composite(overlay, Image.new("RGBA", self.original_icon.size), a)
            
            # Always create a new CTkImage instance
            self.icon = ctk.CTkImage(light_image=result, dark_image=result, size=self.icon_size)
            return self.icon
        except Exception as e:
            print(f"Error in tint_icon: {e}")
            self.icon = None
            return None

    def refresh_icon(self):
        """Refresh the icon - used when window context changes"""
        if self.original_icon:
            try:
                self.create_icon()
                self.configure(image=self.icon)
            except Exception as e:
                print(f"Error refreshing icon: {e}")
                # If error, try to reload from file
                if self.icon_path and os.path.exists(self.icon_path):
                    self.load_icon()
                    if self.icon:
                        self.configure(image=self.icon)

    def _check_appearance_mode(self):
        """Track appearance mode changes and update colors accordingly"""
        try:
            # Check if widget still exists before doing anything
            if not self.winfo_exists():
                return
                
            current_mode = ctk.get_appearance_mode()
            if self._appearance_mode != current_mode:
                self._appearance_mode = current_mode
                self.update_colors()
                
                # Update the button configuration
                self.configure(
                    fg_color=self.fg_color,
                    border_color=self.border_color,
                    border_width=2 if self.outlined else 0,
                    text_color=self.text_color,
                    hover_color=self.hover_color
                )
                
                # Update the icon with new colors
                self.refresh_icon()
        except Exception as e:
            # Widget was destroyed or other error
            if "invalid command name" in str(e):
                return
            print(f"Error in appearance mode check: {e}")
            return
        
        # Schedule the next check if widget still exists
        try:
            if self.winfo_exists():
                self._check_appearance_mode_timer = self.after(100, self._check_appearance_mode)
        except Exception:
            # Widget was destroyed, don't schedule
            pass

    def update_colors(self):
        """Update colors based on current appearance mode"""
        try:
            mode = ctk.get_appearance_mode()
            self._appearance_mode = mode

            # Apply different color schemes based on appearance mode and outlined state
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
        except Exception as e:
            print(f"Error updating colors: {e}")

    def destroy(self):
        """Clean up resources when destroying the widget"""
        # Remove from instances list
        if self in CustomButton._instances:
            CustomButton._instances.remove(self)
        
        # Cancel the scheduled appearance mode check
        if hasattr(self, '_check_appearance_mode_timer'):
            self.after_cancel(self._check_appearance_mode_timer)
        
        super().destroy()
    
    @classmethod
    def refresh_all_icons(cls):
        """Refresh icons for all button instances"""
        for instance in cls._instances:
            if instance.winfo_exists():
                instance.refresh_icon()


# Helper function for easier creation
def create_custom_button(master, text, font=None, icon_path=None, icon_size=(20, 20), 
                         icon_side="left", outlined=False, command=None, **kwargs):
    """Create a CustomButton with the given parameters"""
    try:
        return CustomButton(master, text, font, icon_path, icon_size, icon_side, outlined, command, **kwargs)
    except Exception as e:
        print(f"Error creating custom button: {e}")
        # Fallback to a standard button if there's an error
        return ctk.CTkButton(master, text=text, font=font, command=command, **kwargs)