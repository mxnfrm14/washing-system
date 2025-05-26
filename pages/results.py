import customtkinter as ctk
from components.custom_button import CustomButton
from components.tabview import ThemedTabview

class Results(ctk.CTkFrame):
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
            text="Results & Analysis", 
            font=controller.fonts.get("title", None), 
            anchor="w"
        )
        self.title_label.pack(side="left")

        # Save configuration button
        self.save_button = CustomButton(
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
        self.bottom_frame.pack(fill="x", pady=(10,20), padx=20, anchor="s", side="bottom")

        # Next button
        self.next_button = CustomButton(
            self.bottom_frame,
            text="Generate Report",
            font=controller.fonts.get("default", None),
            icon_path="assets/icons/file.png",
            icon_side="left",
            outlined=False,
            command=lambda: print("Report generated!")
        )
        self.next_button.pack(side="right")

        # Back button
        self.back_button = CustomButton(
            self.bottom_frame,
            text="Back",
            font=controller.fonts.get("default", None),
            icon_path="assets/icons/back.png",
            icon_side="left",
            outlined=True,
            command=lambda: controller.show_page("sequence")
        )
        self.back_button.pack(side="left")

        # ========================== Content Area ==========================
        # Content frame for the main content
        self.content_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=70, pady=10)

        self.tab_view = ThemedTabview(self.content_frame)
        self.tab_view.pack(fill="both", expand=True)
        self.tab1 = self.tab_view.add("Configuration Results")
        self.tab2 = self.tab_view.add("Comparative Analysis")

        # Add widgets to the tabs
        label2 = ctk.CTkLabel(self.tab1, text="Configuration Content")
        label2.pack(pady=20)
        
        label3 = ctk.CTkLabel(self.tab2, text="Results Content")
        label3.pack(pady=20)


    
    def update_appearance(self):
        """Update any appearance-dependent elements"""
        # If you have any appearance-dependent elements, update them here
        pass

    def save_configuration(self):
        """Save the configuration via the controller"""
        print("Configuration saved!")