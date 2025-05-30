import customtkinter as ctk
from components.custom_button import CustomButton
from tkinter import messagebox
from components.custom_table import CustomTable

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
            command=self.add_row
        )
        self.add_button.grid(row=0, column=0, pady=(0, 30), sticky="n")

        # Define sample headers and data
        headers = ["Pump Category", "Number of output", "Pump Name", "Number of WC (O1)", "Number of WC (O2)"]
        data = [
            {
                "Pump Category": "Pump Category",
                "Number of output": "2",
                "Pump Name": "AWEKL 123133112 DE",
                "Number of WC (O1)": "3",
                "Number of WC (O2)": "1"
            },
            {
                "Pump Category": "Pump Category",
                "Number of output": "1",
                "Pump Name": "AWEKL 123133112 DE",
                "Number of WC (O1)": "2",
                "Number of WC (O2)": "0"
            },
            {
                "Pump Category": "Pump Category",
                "Number of output": "1",
                "Pump Name": "AWEKL 123133112 DE",
                "Number of WC (O1)": "2",
                "Number of WC (O2)": "0"
            }
        ]

        # Define custom column widths based on content needs
        # The values are proportional to the total table width
        column_widths = [
            140,  # Pump Category
            140,  # Number of output
            140,  # Pump Name
            140,  # Number of WC (O1)
            140,  # Number of WC (O2)
        ]

         # Create the custom table with specified column widths
        try:
            self.table = CustomTable(
                self.content_frame,
                headers=headers,
                data=data,
                width=800,
                edit_command=self.edit_row,
                delete_command=self.delete_row,
                appearance_mode=ctk.get_appearance_mode(),
                # column_widths=column_widths,  # Add custom column widths
            )
            self.table.grid(row=1, column=0, sticky="nsew", padx=(0, 10), pady=(0, 10))
        except Exception as e:
            print(f"Error creating table: {e}")


    def add_row(self):
        """Add a new row to the table"""
        new_data = {
            "Pump Category": "New Pump Category",
            "Number of output": "2",
            "Pump Name": "Pump Name",
            "Number of WC (O1)": "1",
            "Number of WC (O2)": "2"
        }
        self.table.add_row(new_data)
    
    def edit_row(self, index, row_data):
        """Handle edit button click"""
        # In a real app, you'd show a dialog to edit the data
        # For this example, we'll just show a message and update the row
        messagebox.showinfo("Edit Row", f"Editing row {index}: {row_data}")
        
        # Update the row with new data (in a real app, this would come from a dialog)
        updated_data = row_data.copy()
        updated_data["Number of output"] = "edited"
        self.table.update_row(index, updated_data)
    
    def delete_row(self, index, row_data):
        """Handle delete button click"""
        # Confirm deletion
        if messagebox.askyesno("Delete Row", f"Delete row {index}?"):
            self.table.remove_row(index)
    
    def update_appearance(self):
        """Update any appearance-dependent elements"""
        # Update table appearance if it exists
        if hasattr(self, 'table'):
            try:
                self.table.update_appearance()
            except Exception as e:
                print(f"Error updating table appearance: {e}")

    def save_configuration(self):
        """Save the configuration via the controller"""
        print("Configuration saved!")