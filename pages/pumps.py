import customtkinter as ctk
from custom_button import create_custom_button

class Pumps(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        ctk.set_default_color_theme("theme.json")

         # Create main container for better layout control
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True)

        # ============================ Title and Save Button ==========================
        # Top frame for title and save button
        self.top_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.top_frame.pack(fill="x", padx=40, pady=30)

        # Title
        self.title_label = ctk.CTkLabel(
            self.top_frame, 
            text="Configuration of pumps", 
            font=controller.fonts.get("title", None), 
            anchor="w"
        )
        self.title_label.pack(side="left")

        # Save configuration button
        self.save_button = create_custom_button(
            self.top_frame,
            text="Save configuration",
            font=controller.fonts.get("default", None),
            icon_path="assets/icons/save.png",
            icon_side="left",
            outlined=False,
            command=self.save_configuration
        )
        self.save_button.pack(side="right")

        # Divider
        self.divider = ctk.CTkFrame(self.main_container, height=2, corner_radius=0, fg_color="#F8F8F8")
        self.divider.pack(pady=(0, 20), fill="x")


        # =========================== Navigation Buttons ==========================
        # Bottom frame for navigation buttons
        self.bottom_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.bottom_frame.pack(fill="x", pady=30, padx=20, anchor="s", side="bottom")

        # Next button
        self.next_button = create_custom_button(
            self.bottom_frame,
            text="Next",
            font=controller.fonts.get("default", None),
            icon_path="assets/icons/next.png",
            icon_side="right",
            outlined=False,
            command=lambda: controller.show_page("circuits")
        )
        self.next_button.pack(side="right")

        # Back button
        self.back_button = create_custom_button(
            self.bottom_frame,
            text="Back",
            font=controller.fonts.get("default", None),
            icon_path="assets/icons/back.png",
            icon_side="left",
            outlined=True,
            command=lambda: controller.show_page("washing_components")
        )
        self.back_button.pack(side="left")

        # ========================== Content Area ==========================
        # Content frame for the main content
        self.content_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=150, pady=30)

        # Configure grid for content frame
        self.content_frame.grid_rowconfigure(0, weight=0)         # Button
        self.content_frame.grid_rowconfigure(1, weight=1)         # Table
        self.content_frame.grid_columnconfigure(0, weight=1)       # Button

        self.add_button = create_custom_button(
            self.content_frame,
            text="Add Pump",
            font=controller.fonts.get("default", None),
            icon_path="assets/icons/add.png",
            icon_side="left",
            outlined=False,
            command=self.add_pump
        )
        self.add_button.grid(row=0, column=0, pady=(0, 20), sticky="n")

        # Table for displaying pump configurations
        self.pump_table = ctk.CTkFrame(self.content_frame, fg_color="#F8F8F8")
        self.pump_table.grid(row=1, column=0, sticky="nsew")
    
    def update_appearance(self):
        """Update any appearance-dependent elements"""
        # If you have any appearance-dependent elements, update them here
        pass

    def save_configuration(self):
        """Save the configuration via the controller"""
        print("Configuration saved!")

    def add_pump(self):
        """Add a new pump to the configuration"""
        print("Pump added!")