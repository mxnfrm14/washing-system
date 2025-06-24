import customtkinter as ctk
from tkinter import messagebox
from components.custom_button import CustomButton
from PIL import Image
from components.custom_table import CustomTable
from components.component_config_dialog import ComponentConfigDialog
import uuid

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
        self.save_button = CustomButton(
            self.top_frame,
            text="Save configuration",
            font=controller.fonts.get("default", None),
            icon_path="assets/icons/save.png",
            icon_side="left",
            outlined=False,
            command=self.save_to_disk
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
            text="Next",
            font=controller.fonts.get("default", None),
            icon_path="assets/icons/next.png",
            icon_side="right",
            outlined=False,
            command=lambda: self.save_and_next()
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
            command=lambda: self.save_and_back()
        )
        self.back_button.pack(side="left")

        # ========================== Content Area ==========================
        # Content frame for the main content
        self.content_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=40, pady=30)

        self.content_frame.grid_rowconfigure(0, weight=0)
        self.content_frame.grid_rowconfigure(1, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(1, weight=0, minsize=300)

        # Define sample headers and data
        headers = ["Component", "Nozzle Ref", "D_C_N (mm)", "DZ_P_N (mm)", "Intergration Angle", "Targeted Washing Preformance"]
        
        # Start with empty data or some initial data
        data = []

        # Create the add button
        self.add_button = CustomButton(
            self.content_frame,
            text="Add component",
            font=controller.fonts.get("default", None),
            icon_path="assets/icons/add.png",
            icon_side="left",
            outlined=False,
            command=self.show_add_dialog
        )
        self.add_button.grid(row=0, column=0, sticky="w", padx=(0, 10), pady=(0, 30))

        # Define custom column widths based on content needs
        column_widths = [
            130,  # Component
            100,  # Nozzle Ref
            100,  # D_C_N (mm)
            100,  # DZ_P_N (mm)
            140,  # Integration Angle
            200,  # Targeted Washing Performance
        ]

        # Create the custom table with specified column widths
        try:
            self.table = CustomTable(
                self.content_frame,
                headers=headers,
                data=data,
                width=700,
                edit_command=self.show_edit_dialog,
                delete_command=self.delete_row,
                appearance_mode=ctk.get_appearance_mode(),
                column_widths=column_widths,
            )
            self.table.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        except Exception as e:
            print(f"Error creating table: {e}")

        # Image
        self.image = ctk.CTkImage(light_image=Image.open("assets/images/image.png"),
                                  dark_image=Image.open("assets/images/image.png"), 
                                  size=(275, 350))
        self.image_label = ctk.CTkLabel(self.content_frame, text="", image=self.image, compound="top")
        self.image_label.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=(10, 0), pady=(0, 10))

    def show_add_dialog(self):
        """Show the component configuration dialog for adding"""
        dialog = ComponentConfigDialog(
            self,
            self.controller,
            on_save=self.add_component_from_dialog
        )
        self.wait_window(dialog)
    
    def show_edit_dialog(self, index, row_data):
        """Show the component configuration dialog for editing"""
        dialog = ComponentConfigDialog(
            self,
            self.controller,
            on_save=lambda data: self.update_component_from_dialog(index, data),
            edit_data=row_data
        )
        self.wait_window(dialog)
    
    def add_component_from_dialog(self, component_data):
        """Add a component from the dialog data"""
        # Add unique ID if not present
        if 'id' not in component_data:
            component_data['id'] = f"component_{uuid.uuid4().hex[:8]}"
        self.table.add_row(component_data)
        print(f"Added component: {component_data}")
    
    def update_component_from_dialog(self, index, component_data):
        """Update a component from the dialog data"""
        # Preserve existing ID if updating
        existing_data = self.table.get_row_data(index)
        if existing_data and 'id' in existing_data:
            component_data['id'] = existing_data['id']
        elif 'id' not in component_data:
            component_data['id'] = f"component_{uuid.uuid4().hex[:8]}"
        self.table.update_row(index, component_data)
        print(f"Updated component at index {index}: {component_data}")
    
    def delete_row(self, index, row_data):
        """Handle delete button click"""
        # Confirm deletion
        if messagebox.askyesno("Delete Component", f"Are you sure you want to delete this component?\n\nComponent: {row_data.get('Component', 'Unknown')}"):
            self.table.remove_row(index)
            print(f"Deleted component at index {index}")
            
            self.save_current_configuration()
        
            # Check if there are components configured
            if self.is_completed():
                # Mark this page as completed
                self.controller.mark_page_completed("washing_components")
            else:
                self.controller.mark_page_incomplete("washing_components")
                self.controller.show_page("washing_components")
        


    def get_configuration(self):
        """Get the current configuration from the table"""
        return self.table.get_all_data() if hasattr(self, 'table') else []

    def load_configuration(self, config_data):
        """Load configuration into the table"""
        try:
            components = config_data.get("washing_components", [])
            if hasattr(self, 'table') and components:
                # Clear existing data
                self.table.clear_all_data()
                # Load new data
                for component in components:
                    # Ensure each component has an ID
                    if 'id' not in component:
                        component['id'] = f"component_{uuid.uuid4().hex[:8]}"
                    self.table.add_row(component)
        except Exception as e:
            print(f"Error loading washing components configuration: {e}")

    def save_current_configuration(self):
        """Save the current configuration"""
        all_components = self.get_configuration()
        
        # Update controller's config data
        self.controller.update_config_data("washing_components", all_components)
        
        # print(f"Total components: {len(all_components)}")
        # for i, component in enumerate(all_components):
        #     print(f"Component {i+1}: {component}")
        
    
    def save_to_disk(self):
        """Save the current configuration to disk"""
        self.save_current_configuration()
        
        # Save to disk
        if self.controller.save_whole_configuration():
            messagebox.showinfo("Success", "Configuration saved successfully!")
        else:
            messagebox.showerror("Error", "Failed to save configuration!")   

    def update_appearance(self):
        """Update any appearance-dependent elements"""
        # Update table appearance if it exists
        if hasattr(self, 'table'):
            try:
                self.table.update_appearance()
            except Exception as e:
                print(f"Error updating table appearance: {e}")
    
    def save_and_next(self):
        """Save configuration and navigate to the next page"""
        self.on_leave_page()
        self.controller.show_page("pumps")
    
    def save_and_back(self):
        """Save configuration and navigate to the previous page"""
        self.on_leave_page()
        self.controller.show_page("general_settings")

    def on_leave_page(self):
        """Called when navigating away from this page"""
        # Save the current configuration
        self.save_current_configuration()
        
        # Check if the form is still complete enough to be marked as completed
        if self.is_completed():
            self.controller.mark_page_completed("washing_components")
        else:
            # If it's no longer complete, mark as incomplete
            self.controller.mark_page_incomplete("washing_components")
    
    def on_show_page(self):
        """Called when the page is shown"""
        # Check if the form is still complete
        if self.is_completed():
            self.controller.mark_page_completed("washing_components")
        else:
            self.controller.mark_page_incomplete("washing_components")

    def is_completed(self):
        """Check if the component configuration is completed"""
        if len(self.get_configuration()) > 0:
            return True
        return False