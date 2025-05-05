import customtkinter as ctk
from PIL import Image

class CustomButton(ctk.CTkButton):
    def __init__(self, master, text, font, icon_path, icon_side="left", outlined=False, command=None):
        self.icon_path = icon_path
        self.outlined = outlined
        self.icon_side = icon_side

        # Load original icon
        self.original_icon = Image.open(icon_path).convert("RGBA")

        # Determine colors based on appearance and outlined state
        self.update_colors()

        super().__init__(
            master=master,
            text=text,
            font=font,
            image=self.icon,
            compound=self.icon_side,
            fg_color=self.fg_color,
            border_color=self.border_color,
            border_width=2 if self.outlined else 0,
            corner_radius=6,
            text_color=self.text_color,
            hover_color=self.hover_color,
            command=command
        )

    def tint_icon(self, color_hex):
        """Tint the icon to match the given color"""
        rgb = tuple(int(color_hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (255,)
        overlay = Image.new("RGBA", self.original_icon.size, rgb)
        r, g, b, a = self.original_icon.split()
        result = Image.composite(overlay, Image.new("RGBA", self.original_icon.size), a)
        self.icon = ctk.CTkImage(light_image=result, dark_image=result, size=(20, 20))
        return self.icon

    def update_colors(self):
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

        # Update the icon tint
        self.tint_icon(self.text_color)

        # If already initialized, update appearance
        if hasattr(self, '_canvas'):
            self.configure(
                fg_color=self.fg_color,
                border_color=self.border_color,
                border_width=2 if self.outlined else 0,
                text_color=self.text_color,
                hover_color=self.hover_color,
                image=self.icon
            )

# Helper function
def create_custom_button(master, text, font, icon_path, icon_side="left", outlined=False, command=None):
    return CustomButton(master, text, font, icon_path, icon_side, outlined, command)
