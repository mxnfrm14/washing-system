import customtkinter as ctk
from PIL import Image
from custom_button import create_custom_button

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("theme.json")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("CustomTkinter Example")
        self.geometry("600x500")
        
        # Create a list to track all custom components that need updating
        self.custom_components = []
        
        my_font = ctk.CTkFont(family="EncodeSansExpanded-Regular", size=14, weight="normal")

        # Rest of your initialization code
        self.appearance_mode_label = ctk.CTkLabel(self, text="Appearance Mode:", anchor="w", font=my_font)
        self.appearance_mode_label.pack(pady=(20, 0))
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self, values=["System","Light", "Dark"],
                                                           command=self.change_appearance_mode_event, font=my_font, dropdown_font=my_font)
        self.appearance_mode_optionemenu.pack(pady=(0, 20))

        self.scaling_label = ctk.CTkLabel(self, text="UI Scaling:", anchor="w")
        self.scaling_label.pack(pady=(20, 0))
        self.scaling_optionemenu = ctk.CTkOptionMenu(self, values=["80%", "90%", "100%", "110%", "120%"],
                                                               command=self.change_scaling_event)
        self.scaling_optionemenu.pack(pady=(0, 20))
        

        self.label = ctk.CTkLabel(self, text="Pump", font=my_font, anchor="w")
        self.label.pack(pady=20)

        self.button = ctk.CTkButton(self, text="Click Me", command=self.on_button_click)
        self.button.pack(pady=20)

        self.frame = ctk.CTkFrame(self, width=200, height=100)
        self.frame.pack(pady=20, padx=20, fill="both", expand=True)

        self.bouton = ctk.CTkButton(self.frame, text="TEST", 
                                    font=my_font,
                                    image=ctk.CTkImage(light_image=Image.open("assets/icons/upload.png"),
                                                    dark_image=Image.open("assets/icons/upload.png"), size=(20, 20)),
                                    compound="left",
                                    command=self.on_button_click)
        self.bouton.pack(pady=10)
        self.custom_components.append(self.bouton)  # Add to tracking list
        
        # Create custom buttons and add them to our tracking list
        self.btn1 = create_custom_button(
            master=self.frame,
            text="Télécharger",
            font=my_font,
            icon_path="assets/icons/save.png",
            icon_side="left",
            outlined=False,
            command=self.on_button_click
        )
        self.btn1.pack(pady=10)
        self.custom_components.append(self.btn1)  # Add to tracking list

        self.btn2 = create_custom_button(
            master=self.frame,
            text="Annuler",
            font=my_font,
            icon_path="assets/icons/trash.png",
            icon_side="left",
            outlined=True,
            command=self.on_button_click
        )
        self.btn2.pack(pady=10)
        self.custom_components.append(self.btn2)  # Add to tracking list


    def on_button_click(self):
        self.label.configure(text="Button Clicked!")

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)
        # Update all custom components
        self.update_all_components()
    
    def update_all_components(self):
        """Update all custom components when appearance mode changes"""
        for component in self.custom_components:
            if hasattr(component, 'update_colors'):
                component.update_colors()

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        ctk.set_widget_scaling(new_scaling_float)

# --- Main Execution ---
if __name__ == "__main__":
    app = App()
    app.mainloop()