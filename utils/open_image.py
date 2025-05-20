import os
import customtkinter as ctk
from PIL import Image, ImageOps

def open_image(path, size=None):
    """
    Opens an image from a path and returns a PIL Image object.
    Returns None if the image can't be loaded.
    
    Args:
        path (str): Path to the image
        size (tuple): Optional size for resizing (width, height)
        
    Returns:
        PIL.Image or None: The loaded image or None if loading fails
    """
    try:
        if not os.path.exists(path):
            print(f"Image not found: {path}")
            return None
            
        img = Image.open(path)
        
        if size:
            img = img.resize(size, Image.Resampling.LANCZOS)
            
        return img
    except Exception as e:
        print(f"Error opening image {path}: {e}")
        return None

def open_icon(path, size=(20, 20), tint_color=None):
    """
    Opens an icon and converts it to a CTkImage.
    
    Args:
        path (str): Path to the icon
        size (tuple): Size for the icon (width, height)
        tint_color (str): Color to tint the icon (for icons)
        
    Returns:
        CTkImage or None: CTkImage object or None if loading fails
    """
    try:
        if not os.path.exists(path):
            print(f"Icon not found: {path}")
            # Create a placeholder colored square as fallback
            placeholder = Image.new('RGBA', (64, 64), (200, 200, 200, 128))
            ctk_img = ctk.CTkImage(light_image=placeholder, dark_image=placeholder, size=size)
            return ctk_img
            
        # Load image
        img = Image.open(path)
        
        # Convert to RGBA if not already
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        if tint_color:
            try:
                # Create a colored image for tinting
                if isinstance(tint_color, str) and tint_color.startswith("#"):
                    # Convert hex to RGB
                    r = int(tint_color[1:3], 16)
                    g = int(tint_color[3:5], 16)
                    b = int(tint_color[5:7], 16)
                    tint_color = (r, g, b, 255)
                
                # Create a solid color image
                solid_color = Image.new('RGBA', img.size, tint_color)
                
                # Use the alpha channel of the original as mask
                r, g, b, alpha = img.split()
                solid_color.putalpha(alpha)
                img = solid_color
            except Exception as e:
                print(f"Error tinting icon {path}: {e}")
                # Continue with original image if tinting fails
        
        # Create CTkImage
        ctk_img = ctk.CTkImage(
            light_image=img,
            dark_image=img,
            size=size
        )
        
        return ctk_img
    except Exception as e:
        print(f"Error creating CTkImage from {path}: {e}")
        # Create a placeholder colored square as fallback
        placeholder = Image.new('RGBA', (64, 64), (200, 200, 200, 128))
        ctk_img = ctk.CTkImage(light_image=placeholder, dark_image=placeholder, size=size)
        return ctk_img