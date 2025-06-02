import customtkinter as ctk
from typing import Dict, Any, Callable, Optional
from components.custom_button import CustomButton
from utils.appearance_manager import AppearanceManager
from utils.open_image import open_icon

class PumpConfigDialog(ctk.CTkToplevel):
    """
    Dialog window for configuring pump details
    """
    def __init__(self, parent, controller, on_save: Callable[[Dict[str, Any]], None], edit_data: Optional[Dict[str, Any]] = None):
        super().__init__(parent)
        self.controller = controller
        self.on_save = on_save
        self.edit_data = edit_data  # If provided, we're editing existing data
        self.result = None
        
        # Configure window
        self.title("Pump Configuration" if edit_data is None else "Edit Pump")
        self.geometry("500x450")
        self.resizable(False, False)
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        # Center window on parent
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.winfo_screenheight() // 2) - (450 // 2)
        self.geometry(f"+{x}+{y}")
        
        # Register with appearance manager
        AppearanceManager.register(self)
        
        # Initialize pump data
        self.ref_number = "xxx-xxx-xxx"
        self.supplier_value = "XXXXXXX"
        self.num_outputs = "X"
        
        # Create UI
        self._create_ui()
        
        # Load edit data if provided
        if self.edit_data:
            self._load_edit_data()
        
        # Update appearance
        self.update_appearance()
        
        # Focus on first input
        self.category_dropdown.focus()
    
    def _create_ui(self):
        """Create the dialog UI"""
        # Main container
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        self.title_label = ctk.CTkLabel(
            self.main_container,
            text="Pump configuration",
            font=self.controller.fonts.get("title", None),
            anchor="w"
        )
        self.title_label.pack(pady=(0, 20))
        
        # Form frame
        self.form_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.form_frame.pack(fill="both", expand=True)
        
        # Configure grid
        self.form_frame.grid_columnconfigure(0, weight=0, minsize=200)
        self.form_frame.grid_columnconfigure(1, weight=1)
        
        row = 0
        
        # Pump category dropdown
        self._create_field(
            row, "Pump category", 
            self._create_category_dropdown()
        )
        row += 1
        
        # Pump Name dropdown
        self._create_field(
            row, "Pump Name",
            self._create_pump_name_dropdown()
        )
        row += 1
        
        # Info labels row (Ref, Supplier, Number of outputs)
        self._create_info_labels_row(row)
        row += 1
        
        # Number of washing components for Output 1
        self._create_field(
            row, "Number of washing component (Output1)",
            self._create_output_dropdown("output1")
        )
        row += 1
        
        # Number of washing components for Output 2
        self.output2_label = ctk.CTkLabel(
            self.form_frame,
            text="Number of Washing component (Output 2)",
            font=self.controller.fonts.get("default", None),
            anchor="w"
        )
        self.output2_dropdown = self._create_output_dropdown("output2")
        
        # Initially hide Output 2 if only 1 output
        if self.num_outputs == "1":
            self.output2_label.grid_forget()
            self.output2_dropdown.grid_forget()
        else:
            self._create_field(row, "Number of Washing component (Output 2)", self.output2_dropdown)
            row += 1
        
        # Buttons frame
        self.buttons_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.buttons_frame.pack(fill="x", pady=(30, 0))
        
        # Cancel button
        self.cancel_button = CustomButton(
            self.buttons_frame,
            text="Cancel",
            font=self.controller.fonts.get("default", None),
            icon_path='assets/icons/back.png',
            outlined=True,
            command=self.cancel
        )
        self.cancel_button.pack(side="left", padx=(0, 10))
        
        # Add/Save button
        button_text = "Update pump" if self.edit_data else "Add pump"
        button_icon = "assets/icons/save.png" if self.edit_data else "assets/icons/add.png"
        
        self.save_button = CustomButton(
            self.buttons_frame,
            text=button_text,
            font=self.controller.fonts.get("default", None),
            icon_path=button_icon,
            icon_side="left",
            outlined=False,
            command=self.save
        )
        self.save_button.pack(side="right")
    
    def _create_field(self, row: int, label_text: str, field_widget):
        """Create a field with label"""
        # Label
        label = ctk.CTkLabel(
            self.form_frame,
            text=label_text,
            font=self.controller.fonts.get("default", None),
            anchor="w"
        )
        label.grid(row=row, column=0, sticky="w", pady=10, padx=(0, 10))
        
        # Field widget
        field_widget.grid(row=row, column=1, sticky="ew", pady=10)
        
        # Store label reference if it's output2
        if "Output 2" in label_text:
            self.output2_label = label
    
    def _create_category_dropdown(self):
        """Create pump category dropdown"""
        self.category_var = ctk.StringVar(value="Select category")
        dropdown = ctk.CTkOptionMenu(
            self.form_frame,
            variable=self.category_var,
            values=["Category A", "Category B", "Category C"],
            font=self.controller.fonts.get("default", None),
            dropdown_font=self.controller.fonts.get("default", None),
            width=250
        )
        self.category_dropdown = dropdown
        return dropdown
    
    def _create_pump_name_dropdown(self):
        """Create pump name dropdown"""
        self.pump_name_var = ctk.StringVar(value="Select pump")
        dropdown = ctk.CTkOptionMenu(
            self.form_frame,
            variable=self.pump_name_var,
            values=["AWEKL 123133112 DE", "BWEKL 456789123 FR", "CWEKL 789456123 UK"],
            font=self.controller.fonts.get("default", None),
            dropdown_font=self.controller.fonts.get("default", None),
            width=250,
            command=self._on_pump_name_change
        )
        return dropdown
    
    def _create_output_dropdown(self, output_id: str):
        """Create number of washing components dropdown"""
        if output_id == "output1":
            self.output1_var = ctk.StringVar(value="Select number")
            var = self.output1_var
        else:
            self.output2_var = ctk.StringVar(value="Select number")
            var = self.output2_var
        
        dropdown = ctk.CTkOptionMenu(
            self.form_frame,
            variable=var,
            values=["0", "1", "2", "3", "4", "5"],
            font=self.controller.fonts.get("default", None),
            dropdown_font=self.controller.fonts.get("default", None),
            width=250
        )
        return dropdown
    
    def _create_info_labels_row(self, row: int):
        """Create pump info labels (Ref, Supplier, Number of outputs)"""
        # Create container for alignment
        info_container = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        info_container.grid(row=row, column=0, columnspan=2, sticky="ew", pady=10)
        
        # Configure grid
        info_container.grid_columnconfigure(0, weight=0, minsize=200)
        info_container.grid_columnconfigure(1, weight=1)
        
        # Empty label for alignment
        empty_label = ctk.CTkLabel(info_container, text="", width=200)
        empty_label.grid(row=0, column=0)
        
        # Create info frame with subtle background
        info_frame = ctk.CTkFrame(info_container, fg_color='transparent', height=40)
        info_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        info_frame.grid_propagate(False)
        
        # Configure grid for 3 labels
        info_frame.grid_columnconfigure(0, weight=1)
        info_frame.grid_columnconfigure(1, weight=1)
        info_frame.grid_columnconfigure(2, weight=1)
        
        # Ref number label
        self.ref_label = ctk.CTkLabel(
            info_frame,
            text=f"Ref n° : {self.ref_number}",
            font=ctk.CTkFont(family="Encode Sans Expanded", size=12),
            text_color=("gray30", "gray70"),
            anchor="w"
        )
        self.ref_label.grid(row=0, column=0, sticky="w", padx=10, pady=10)
        
        # Supplier label
        self.supplier_label = ctk.CTkLabel(
            info_frame,
            text=f"Supplier: {self.supplier_value}",
            font=ctk.CTkFont(family="Encode Sans Expanded", size=12),
            text_color=("gray30", "gray70"),
            anchor="center"
        )
        self.supplier_label.grid(row=0, column=1, sticky="ew", padx=5, pady=10)
        
        # Number of outputs label
        self.outputs_label = ctk.CTkLabel(
            info_frame,
            text=f"Number of output : {self.num_outputs}",
            font=ctk.CTkFont(family="Encode Sans Expanded", size=12),
            text_color=("gray30", "gray70"),
            anchor="e"
        )
        self.outputs_label.grid(row=0, column=2, sticky="e", padx=10, pady=10)
    
    def _on_pump_name_change(self, value):
        """Update pump info based on pump name selection"""
        # Simulate pump data lookup
        pump_data = {
            "AWEKL 123133112 DE": {
                "ref": "123-133-112",
                "supplier": "Bosch DE",
                "outputs": "2"
            },
            "BWEKL 456789123 FR": {
                "ref": "456-789-123",
                "supplier": "Valeo FR",
                "outputs": "1"
            },
            "CWEKL 789456123 UK": {
                "ref": "789-456-123",
                "supplier": "Dyson UK",
                "outputs": "2"
            }
        }
        
        data = pump_data.get(value, {"ref": "xxx-xxx-xxx", "supplier": "XXXXXXX", "outputs": "X"})
        self.ref_number = data["ref"]
        self.supplier_value = data["supplier"]
        self.num_outputs = data["outputs"]
        
        # Update labels
        if hasattr(self, 'ref_label'):
            self.ref_label.configure(text=f"Ref n° : {self.ref_number}")
        if hasattr(self, 'supplier_label'):
            self.supplier_label.configure(text=f"Supplier: {self.supplier_value}")
        if hasattr(self, 'outputs_label'):
            self.outputs_label.configure(text=f"Number of output : {self.num_outputs}")
        
        # Show/hide Output 2 based on number of outputs
        if hasattr(self, 'output2_label') and hasattr(self, 'output2_dropdown'):
            if self.num_outputs == "1":
                self.output2_label.grid_forget()
                self.output2_dropdown.grid_forget()
                self.output2_var.set("0")  # Reset to 0 when hidden
            else:
                self.output2_label.grid(row=4, column=0, sticky="w", pady=10, padx=(0, 10))
                self.output2_dropdown.grid(row=4, column=1, sticky="ew", pady=10)
    
    def _load_edit_data(self):
        """Load data for editing"""
        if not self.edit_data:
            return
        
        # Map table data to dialog fields
        self.category_var.set(self.edit_data.get("Pump Category", ""))
        self.pump_name_var.set(self.edit_data.get("Pump Name", ""))
        
        # Update pump info (will trigger _on_pump_name_change)
        self._on_pump_name_change(self.edit_data.get("Pump Name", ""))
        
        # Set output values
        self.output1_var.set(self.edit_data.get("Number of WC (O1)", "0"))
        self.output2_var.set(self.edit_data.get("Number of WC (O2)", "0"))
    
    def save(self):
        """Save the pump configuration"""
        # Validate inputs
        if self.category_var.get() == "Select category":
            self._show_error("Please select a pump category")
            return
        
        if self.pump_name_var.get() == "Select pump":
            self._show_error("Please select a pump name")
            return
        
        if self.output1_var.get() == "Select number":
            self._show_error("Please select number of washing components for Output 1")
            return
        
        # Validate Output 2 if pump has 2 outputs
        if self.num_outputs == "2" and self.output2_var.get() == "Select number":
            self._show_error("Please select number of washing components for Output 2")
            return
        
        # Prepare data for table
        self.result = {
            "Pump Category": self.category_var.get(),
            "Number of output": self.num_outputs,
            "Pump Name": self.pump_name_var.get(),
            "Number of WC (O1)": self.output1_var.get(),
            "Number of WC (O2)": self.output2_var.get() if self.num_outputs == "2" else "0"
        }
        
        # Call the save callback
        if self.on_save:
            self.on_save(self.result)
        
        self.destroy()
    
    def cancel(self):
        """Cancel and close dialog"""
        self.result = None
        self.destroy()
    
    def _show_error(self, message: str):
        """Show error message"""
        error_dialog = ctk.CTkToplevel(self)
        error_dialog.title("Error")
        error_dialog.geometry("300x100")
        error_dialog.transient(self)
        error_dialog.grab_set()
        
        # Center on parent
        error_dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - 150
        y = self.winfo_y() + (self.winfo_height() // 2) - 50
        error_dialog.geometry(f"+{x}+{y}")
        
        label = ctk.CTkLabel(error_dialog, text=message)
        label.pack(pady=20)
        
        ok_button = ctk.CTkButton(
            error_dialog,
            text="OK",
            command=error_dialog.destroy,
            width=80
        )
        ok_button.pack()
    
    def update_appearance(self, mode=None):
        """Update appearance based on theme"""
        # The dialog will automatically inherit appearance from parent
        pass
    
    def destroy(self):
        """Clean up when destroying"""
        AppearanceManager.unregister(self)
        super().destroy()