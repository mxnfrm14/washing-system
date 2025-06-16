import customtkinter as ctk
from components.custom_button import CustomButton
from tkinter import messagebox
from components.custom_table import CustomTable
from components.pump_config_dialog import PumpConfigDialog
import uuid

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
            text="Next",
            font=controller.fonts.get("default", None),
            icon_path="assets/icons/next.png",
            icon_side="right",
            outlined=False,
            command=lambda: controller.show_page("circuits")
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

        self.add_button = CustomButton(
            self.content_frame,
            text="Add Pump",
            font=controller.fonts.get("default", None),
            icon_path="assets/icons/add.png",
            icon_side="left",
            outlined=False,
            command=self.show_add_dialog
        )
        self.add_button.grid(row=0, column=0, pady=(0, 30), sticky="n")

        # Define sample headers and data
        headers = ["Pump Category", "Number of output", "Pump Name", "Number of WC (O1)", "Number of WC (O2)"]
        
        # Start with empty data or some initial data
        data = []

        # Define custom column widths based on content needs
        # The values are proportional to the total table width
        column_widths = [
            140,  # Pump Category
            140,  # Number of output
            200,  # Pump Name
            160,  # Number of WC (O1)
            160,  # Number of WC (O2)
        ]

         # Create the custom table with specified column widths
        try:
            self.table = CustomTable(
                self.content_frame,
                headers=headers,
                data=data,
                width=800,
                edit_command=self.show_edit_dialog,
                delete_command=self.delete_row,
                appearance_mode=ctk.get_appearance_mode(),
                column_widths=column_widths,  # Add custom column widths
            )
            self.table.grid(row=1, column=0, sticky="nsew", padx=(0, 10), pady=(0, 10))
        except Exception as e:
            print(f"Error creating table: {e}")

    def show_add_dialog(self):
        """Show the pump configuration dialog for adding"""
        dialog = PumpConfigDialog(
            self,
            self.controller,
            on_save=self.add_pump_from_dialog
        )
        self.wait_window(dialog)
    
    def show_edit_dialog(self, index, row_data):
        """Show the pump configuration dialog for editing"""
        dialog = PumpConfigDialog(
            self,
            self.controller,
            on_save=lambda data: self.update_pump_from_dialog(index, data),
            edit_data=row_data
        )
        self.wait_window(dialog)
    
    def add_pump_from_dialog(self, pump_data):
        """Add a pump from the dialog data"""
        # Add unique ID if not present
        if 'id' not in pump_data:
            pump_data['id'] = f"pump_{uuid.uuid4().hex[:8]}"
        self.table.add_row(pump_data)
        print(f"Added pump: {pump_data}")
    
    def update_pump_from_dialog(self, index, pump_data):
        """Update a pump from the dialog data"""
        # Preserve existing ID if updating
        existing_data = self.table.get_row_data(index)
        if existing_data and 'id' in existing_data:
            pump_data['id'] = existing_data['id']
        elif 'id' not in pump_data:
            pump_data['id'] = f"pump_{uuid.uuid4().hex[:8]}"
        self.table.update_row(index, pump_data)
        print(f"Updated pump at index {index}: {pump_data}")
    
    def delete_row(self, index, row_data):
        """Handle delete button click"""
        # Confirm deletion
        if messagebox.askyesno("Delete Pump", f"Are you sure you want to delete this pump?\n\nPump: {row_data.get('Pump Name', 'Unknown')}"):
            self.table.remove_row(index)
            print(f"Deleted pump at index {index}")
    
    def update_appearance(self):
        """Update any appearance-dependent elements"""
        # Update table appearance if it exists
        if hasattr(self, 'table'):
            try:
                self.table.update_appearance()
            except Exception as e:
                print(f"Error updating table appearance: {e}")

    def get_configuration(self):
        """Get the current configuration from the table"""
        return self.table.get_all_data() if hasattr(self, 'table') else []

    def load_configuration(self, config_data):
        """Load configuration into the table"""
        try:
            pumps = config_data.get("pumps", [])
            if hasattr(self, 'table') and pumps:
                # Clear existing data
                self.table.clear_all_data()
                # Load new data
                for pump in pumps:
                    # Ensure each pump has an ID
                    if 'id' not in pump:
                        pump['id'] = f"pump_{uuid.uuid4().hex[:8]}"
                    self.table.add_row(pump)
        except Exception as e:
            print(f"Error loading pumps configuration: {e}")

    def save_configuration(self):
        """Save the configuration via the controller"""
        all_pumps = self.get_configuration()
        
        # Update controller's config data
        self.controller.update_config_data("pumps", all_pumps)
        
        print("Saving pump configuration...")
        print(f"Total pumps: {len(all_pumps)}")
        for i, pump in enumerate(all_pumps):
            print(f"Pump {i+1}: {pump}")
        
        # Save to disk
        if self.controller.save_whole_configuration():
            messagebox.showinfo("Success", f"Pump configuration saved successfully!\n\n{len(all_pumps)} pumps saved.")
        else:
            messagebox.showerror("Error", "Failed to save pump configuration!")