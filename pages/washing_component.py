import customtkinter as ctk
from custom_button import create_custom_button
from PIL import Image

class WashingComponent(ctk.CTkFrame):
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
            text="Configuration of the washing components", 
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
            command=lambda: controller.show_page("pumps")
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
            command=lambda: controller.show_page("general_settings")
        )
        self.back_button.pack(side="left")

        # ========================== Content Area ==========================
        # Form container
        self.content_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=150, pady=30)

        # Configure grid for form - consistent column structure
        self.content_frame.grid_rowconfigure(0, weight=0)          # Select
        self.content_frame.grid_rowconfigure(1, weight=0)          # Button
        self.content_frame.grid_rowconfigure(2, weight=1)          # Table
        self.content_frame.grid_columnconfigure((0, 1), weight=1)  

        # Select frame for component selection
        self.select_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.select_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 20), pady=(0, 20))
        
        self.select_frame.grid_rowconfigure((0,1), weight=1)
        self.select_frame.grid_columnconfigure((0, 1), weight=1)

        # Label for component selection
        self.use_case_label = ctk.CTkLabel(
            self.select_frame, 
            text="Use case", 
            font=controller.fonts.get("default", None),
            anchor="w"
        )
        self.use_case_label.grid(row=0, column=0, sticky="w", pady=10)

        self.use_case_dropdown = ctk.CTkOptionMenu(
            self.select_frame,
            values=["Highway", "Autre"],
            font=controller.fonts.get("default", None),
            dropdown_font=controller.fonts.get("default", None),
            width=200
        )
        self.use_case_dropdown.set("Select use case")  # Set default value
        self.use_case_dropdown.grid(row=0, column=1, sticky="w", pady=10)

        self.dirt_type_label = ctk.CTkLabel(
            self.select_frame, 
            text="Dirt type", 
            font=controller.fonts.get("default", None),
            anchor="w"
        )
        self.dirt_type_label.grid(row=1, column=0, sticky="w", pady=10)

        self.dirt_type_dropdown = ctk.CTkOptionMenu(
            self.select_frame,
            values=["Dirt", "Autre"],
            font=controller.fonts.get("default", None),
            dropdown_font=controller.fonts.get("default", None),
            width=200
        )
        self.dirt_type_dropdown.set("Select dirt type")
        self.dirt_type_dropdown.grid(row=1, column=1, sticky="w", pady=10)

        # Button to add a new component
        self.add_component_button = create_custom_button(
            self.content_frame,
            text="Add component",
            font=controller.fonts.get("default", None),
            icon_path="assets/icons/add.png",
            icon_side="left",
            outlined=False,
            command=self.add_component
        )
        self.add_component_button.grid(row=1, column=0, sticky="w", padx=20, pady=20)

        # Table for displaying components
        self.table_frame = ctk.CTkFrame(self.content_frame, fg_color="#F8F8F8")
        self.table_frame.grid(row=2, column=0, sticky="nsew", padx=(0, 20), pady=(0, 20))

        self.table_frame.grid_rowconfigure(0, weight=1)
        self.table_frame.grid_columnconfigure((0, 1, 2), weight=1)




        # Image
        self.image = ctk.CTkImage(light_image=Image.open("assets/images/image.png"),
                                  dark_image=Image.open("assets/images/image.png"), 
                                  size=(275, 390))
        self.image_label = ctk.CTkLabel(self.content_frame, text="", image=self.image, compound="top")
        self.image_label.grid(row=0, column=1, rowspan=3)



    
    def save_configuration(self):
        """Save the current configuration"""
        # Implement save functionality here
        print("Saving configuration...")
        # You can add file dialog and save logic here
        
    def update_appearance(self):
        """Update any appearance-dependent elements"""
        # If you have any appearance-dependent elements, update them here
        pass

    def add_component(self):
        """Add a new component to the configuration"""
        # Implement add component functionality here
        print("Adding new component")
        # You can add logic to create a new component entry in the table