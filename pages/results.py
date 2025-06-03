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

        # Edit configuration button
        self.edit_button = CustomButton(
            self.top_frame,
            text="Edit configuration",
            font=controller.fonts.get("default", None),
            icon_path="assets/icons/edit.png",
            icon_side="left",
            outlined=True,
            command=self.edit_configuration
        )
        self.edit_button.pack(side="right", padx=(0, 10))

        # Divider
        self.divider = ctk.CTkFrame(self.main_container, height=2, corner_radius=0, fg_color="#F8F8F8")
        self.divider.pack(pady=(0, 20), fill="x")

        # ========================== Content Area ==========================
        # Content frame for the main content
        self.content_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.tab_view = ThemedTabview(self.content_frame)
        self.tab_view.pack(fill="both", expand=True)
        self.tab1 = self.tab_view.add("Configuration Results")
        self.tab2 = self.tab_view.add("Comparative Analysis")

        # ======================== TAB 1 - Configuration Results ========================
        
        self.scrollable_frame = ctk.CTkScrollableFrame(self.tab1, width=500, height=300, fg_color="transparent")
        self.scrollable_frame.pack(fill="both", expand=True, padx=20, pady=20)
        # Example content in the scrollable frame
        for i in range(20):
            label = ctk.CTkLabel(self.scrollable_frame, text=f"Result {i+1}", font=controller.fonts.get("default", None))
            label.pack(pady=5, padx=10, anchor="w")

        
        # Bottom frame for buttons in tab1
        self.bottom_frame_tab1 = ctk.CTkFrame(self.tab1, fg_color="transparent")
        self.bottom_frame_tab1.pack(fill="x", pady=(10,20), padx=20, anchor="s", side="bottom")

        # Generate Report button
        self.next_button = CustomButton(
            self.bottom_frame_tab1,
            text="Generate Report",
            font=controller.fonts.get("default", None),
            icon_path="assets/icons/file.png",
            icon_side="left",
            outlined=False,
            command=lambda: print("Report generated!")
        )
        self.next_button.pack(side="right")



        # ======================== TAB 2 - Comparative Analysis ========================
        
        label3 = ctk.CTkLabel(self.tab2,
                            text="Load configuraiton to compare them",
                            font=controller.fonts.get("title", None),)
        label3.pack(pady=20)
        label4 = ctk.CTkLabel(self.tab2, text="The configurations must have the same number of pump, the same number of output, the same tension and temperature",
                              font=controller.fonts.get("default", None))
        label4.pack(pady=10)

        #Load configuration button
        self.load_button = CustomButton(
            self.tab2,
            text="Load Configuration",
            font=controller.fonts.get("default", None),
            icon_path="assets/icons/upload.png",
            icon_side="left",
            outlined=False,
            command=lambda: print("Configuration loaded!")
        )
        self.load_button.pack(pady=20)

        #Load configuration button
        self.load_button = CustomButton(
            self.tab2,
            text="Load Configuration",
            font=controller.fonts.get("default", None),
            icon_path="assets/icons/upload.png",
            icon_side="left",
            outlined=True,
            command=lambda: print("Configuration loaded!")
        )
        self.load_button.pack(pady=(0,20))
        
        
        # Bottom frame for buttons in tab2
        self.bottom_frame_tab2 = ctk.CTkFrame(self.tab2, fg_color="transparent")
        self.bottom_frame_tab2.pack(fill="x", pady=(10,20), padx=20, anchor="s", side="bottom")

        # Next button
        self.next_button = CustomButton(
            self.bottom_frame_tab2,
            text="Next",
            font=controller.fonts.get("default", None),
            icon_path="assets/icons/next.png",
            icon_side="left",
            outlined=False,
            command=lambda: print("Next step in analysis!")
        )
        self.next_button.pack(side="right")



    
    def update_appearance(self):
        """Update any appearance-dependent elements"""
        # If you have any appearance-dependent elements, update them here
        pass

    def save_configuration(self):
        """Save the configuration via the controller"""
        print("Configuration saved!")

    def edit_configuration(self):
        """Edit the configuration via the controller"""
        print("Editing configuration...")