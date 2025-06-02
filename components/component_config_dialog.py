import customtkinter as ctk
from typing import Dict, Any, Callable, Optional
from components.custom_button import CustomButton
from utils.appearance_manager import AppearanceManager
from utils.open_image import open_icon

class ComponentConfigDialog(ctk.CTkToplevel):
    """
    Dialog window for configuring component details
    """
    def __init__(self, parent, controller, on_save: Callable[[Dict[str, Any]], None], edit_data: Optional[Dict[str, Any]] = None):
        super().__init__(parent)
        self.controller = controller
        self.on_save = on_save
        self.edit_data = edit_data  # If provided, we're editing existing data
        self.result = None
        
        # Configure window
        self.title("Component Configuration" if edit_data is None else "Edit Component")
        self.geometry("500x580")
        self.resizable(False, False)
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        # Center window on parent
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.winfo_screenheight() // 2) - (580 // 2)
        self.geometry(f"+{x}+{y}")
        
        # Register with appearance manager
        AppearanceManager.register(self)
        
        # Create UI
        self._create_ui()
        
        # Load edit data if provided
        if self.edit_data:
            self._load_edit_data()
        
        # Update appearance
        self.update_appearance()
        
        # Focus on first input
        self.component_dropdown.focus()
    
    def _create_ui(self):
        """Create the dialog UI"""
        # Main container
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        self.title_label = ctk.CTkLabel(
            self.main_container,
            text="Component configuration",
            font=self.controller.fonts.get("title", None),
            anchor="w"
        )
        self.title_label.pack(pady=(0, 20))
        
        # Form frame
        self.form_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.form_frame.pack(fill="both", expand=True)
        
        # Configure grid
        self.form_frame.grid_columnconfigure(0, weight=0, minsize=180)
        self.form_frame.grid_columnconfigure(1, weight=1)
        
        row = 0
        
        # Component dropdown
        self._create_field_with_info(
            row, "Component", 
            self._create_component_dropdown(),
            info_tooltip=None
        )
        row += 1
        
        # Number of nozzles
        self._create_field_with_info(
            row, "Number of nozzles",
            self._create_nozzles_dropdown(),
            info_tooltip=None
        )
        row += 1
        
        # Nozzle Reference
        self._create_field_with_info(
            row, "Nozzle Reference",
            self._create_nozzle_ref_dropdown(),
            info_tooltip=None
        )
        row += 1
        
        # Supplier and Type labels on the same row
        self._create_info_labels_row(row)
        row += 1
        
        # Min washing performance
        self._create_field_with_info(
            row, "Min. washing performance (%)",
            self._create_performance_entry(),
            info_tooltip=None
        )
        row += 1
        
        # D Component Nozzle with info icon
        self._create_field_with_info(
            row, "D Component Nozzle",
            self._create_measurement_field("d_component"),
            info_tooltip="Distance between component and nozzle"
        )
        row += 1
        
        # DZ Pump Nozzle with info icon
        self._create_field_with_info(
            row, "DZ Pump Nozzle",
            self._create_measurement_field("dz_pump"),
            info_tooltip="Distance between pump and nozzle"
        )
        row += 1
        
        # Integration Angle with info icon
        self._create_field_with_info(
            row, "Integration Angle",
            self._create_measurement_field("angle"),
            info_tooltip="Angle of integration"
        )
        row += 1
        
        # Buttons frame
        self.buttons_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.buttons_frame.pack(fill="x", pady=(30, 0))
        
        # Cancel button
        self.cancel_button = CustomButton(
            self.buttons_frame,
            text="Cancel",
            font=self.controller.fonts.get("default", None),
            icon_path=None,
            outlined=True,
            command=self.cancel
        )
        self.cancel_button.pack(side="left", padx=(0, 10))
        
        # Add/Save button
        button_text = "Update component" if self.edit_data else "Add component"
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
    
    def _create_field_with_info(self, row: int, label_text: str, field_widget, info_tooltip: Optional[str] = None):
        """Create a field with label and optional info icon"""
        # Label frame (to hold label and optional info icon)
        label_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        label_frame.grid(row=row, column=0, sticky="w", pady=10, padx=(0, 10))
        
        # Label
        label = ctk.CTkLabel(
            label_frame,
            text=label_text,
            font=self.controller.fonts.get("default", None),
            anchor="w"
        )
        label.pack(side="left")
        
        # Info icon if tooltip provided
        if info_tooltip:
            info_icon = open_icon("assets/icons/info.png", size=(16, 16))
            if info_icon:
                info_label = ctk.CTkLabel(
                    label_frame,
                    text="",
                    image=info_icon,
                    width=16,
                    height=16
                )
                info_label.pack(side="left", padx=(5, 0))
                
                # Bind tooltip hover (you could implement a proper tooltip widget)
                info_label.bind("<Enter>", lambda e: self._show_tooltip(e, info_tooltip))
                info_label.bind("<Leave>", lambda e: self._hide_tooltip())
        
        # Field widget
        field_widget.grid(row=row, column=1, sticky="ew", pady=10)
    
    def _create_component_dropdown(self):
        """Create component dropdown"""
        self.component_var = ctk.StringVar(value="Select component")
        dropdown = ctk.CTkOptionMenu(
            self.form_frame,
            variable=self.component_var,
            values=["Component A", "Component B", "Component C", "Component D"],
            font=self.controller.fonts.get("default", None),
            dropdown_font=self.controller.fonts.get("default", None),
            width=250
        )
        self.component_dropdown = dropdown
        return dropdown
    
    def _create_nozzles_dropdown(self):
        """Create number of nozzles dropdown"""
        self.nozzles_var = ctk.StringVar(value="Select number")
        dropdown = ctk.CTkOptionMenu(
            self.form_frame,
            variable=self.nozzles_var,
            values=["1", "2", "3", "4", "5"],
            font=self.controller.fonts.get("default", None),
            dropdown_font=self.controller.fonts.get("default", None),
            width=250
        )
        return dropdown
    
    def _create_nozzle_ref_dropdown(self):
        """Create nozzle reference dropdown"""
        self.nozzle_ref_var = ctk.StringVar(value="Select reference")
        dropdown = ctk.CTkOptionMenu(
            self.form_frame,
            variable=self.nozzle_ref_var,
            values=["Nozzle Type A", "Nozzle Type B", "Nozzle Type C"],
            font=self.controller.fonts.get("default", None),
            dropdown_font=self.controller.fonts.get("default", None),
            width=250,
            command=self._on_nozzle_ref_change
        )
        return dropdown
    
    def _create_info_labels_row(self, row: int):
        """Create supplier and type info labels on the same row"""
        # Create a subtle info container that spans both columns
        info_container = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        info_container.grid(row=row, column=0, columnspan=2, sticky="ew", pady=10)
        
        # Configure grid
        info_container.grid_columnconfigure(0, weight=0, minsize=180)
        info_container.grid_columnconfigure(1, weight=1)
        
        # Empty label for alignment with other rows
        empty_label = ctk.CTkLabel(info_container, text="", width=180)
        empty_label.grid(row=0, column=0)
        
        # Create info frame in the second column to align with other fields
        info_frame = ctk.CTkFrame(info_container, fg_color='transparent', height=40)
        info_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        info_frame.grid_propagate(False)
        
        # Configure grid for the info frame
        info_frame.grid_columnconfigure(0, weight=1)
        info_frame.grid_columnconfigure(1, weight=1)
        
        # Initialize supplier value
        self.supplier_value = "XXXXXX"
        
        # Supplier label
        self.supplier_label = ctk.CTkLabel(
            info_frame,
            text=f"Supplier: {self.supplier_value}",
            font=ctk.CTkFont(family="Encode Sans Expanded", size=13),
            text_color=("gray30", "gray70"),
            anchor="w"
        )
        self.supplier_label.grid(row=0, column=0, sticky="w", padx=12, pady=10)
        
        # Type label (always "fixed")
        self.type_label = ctk.CTkLabel(
            info_frame,
            text="Type: fixed",
            font=ctk.CTkFont(family="Encode Sans Expanded", size=13),
            text_color=("gray30", "gray70"),
            anchor="w"
        )
        self.type_label.grid(row=0, column=1, sticky="e", padx=12, pady=10)
    
    def _create_performance_entry(self):
        """Create performance entry field"""
        self.performance_var = ctk.StringVar()
        entry = ctk.CTkEntry(
            self.form_frame,
            textvariable=self.performance_var,
            placeholder_text="Enter percentage",
            font=self.controller.fonts.get("default", None),
            width=250
        )
        return entry
    
    def _create_measurement_field(self, field_type: str):
        """Create measurement field with value and unit dropdown"""
        frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        
        # Entry
        if field_type == "d_component":
            self.d_component_var = ctk.StringVar()
            entry_var = self.d_component_var
            self.d_component_unit_var = ctk.StringVar(value="mm")
            unit_var = self.d_component_unit_var
        elif field_type == "dz_pump":
            self.dz_pump_var = ctk.StringVar()
            entry_var = self.dz_pump_var
            self.dz_pump_unit_var = ctk.StringVar(value="mm")
            unit_var = self.dz_pump_unit_var
        else:  # angle
            self.angle_var = ctk.StringVar()
            entry_var = self.angle_var
            self.angle_unit_var = ctk.StringVar(value="deg")
            unit_var = self.angle_unit_var
        
        entry = ctk.CTkEntry(
            frame,
            textvariable=entry_var,
            placeholder_text="Value",
            font=self.controller.fonts.get("default", None),
            width=150
        )
        entry.pack(side="left", padx=(0, 10))
        
        # Unit dropdown
        units = ["mm", "cm", "m"] if field_type != "angle" else ["deg", "rad"]
        unit_dropdown = ctk.CTkOptionMenu(
            frame,
            variable=unit_var,
            values=units,
            font=self.controller.fonts.get("default", None),
            dropdown_font=self.controller.fonts.get("default", None),
            width=90
        )
        unit_dropdown.pack(side="left")
        
        return frame
    
    def _on_nozzle_ref_change(self, value):
        """Update supplier based on nozzle reference selection"""
        # Simulate supplier lookup based on nozzle type
        supplier_map = {
            "Nozzle Type A": "Supplier ABC",
            "Nozzle Type B": "Supplier XYZ",
            "Nozzle Type C": "Supplier DEF"
        }
        self.supplier_value = supplier_map.get(value, "XXXXXX")
        
        # Update the supplier label
        if hasattr(self, 'supplier_label'):
            self.supplier_label.configure(text=f"Supplier: {self.supplier_value}")
    
    def _show_tooltip(self, event, text):
        """Show tooltip (simplified version)"""
        # In a real implementation, you'd create a proper tooltip widget
        print(f"Tooltip: {text}")
    
    def _hide_tooltip(self):
        """Hide tooltip"""
        pass
    
    def _load_edit_data(self):
        """Load data for editing"""
        if not self.edit_data:
            return
        
        # Map table columns to dialog fields
        self.component_var.set(self.edit_data.get("Component", ""))
        
        # Extract numeric values from strings
        d_c_n = self.edit_data.get("D_C_N (mm)", "")
        dz_p_n = self.edit_data.get("DZ_P_N (mm)", "")
        angle = self.edit_data.get("Intergration Angle", "")
        performance = self.edit_data.get("Targeted Washing Preformance", "")
        
        self.d_component_var.set(d_c_n)
        self.dz_pump_var.set(dz_p_n)
        self.angle_var.set(angle)
        self.performance_var.set(performance)
        
        # Set nozzle ref
        self.nozzle_ref_var.set(self.edit_data.get("Nozzle Ref", ""))
    
    def _convert_to_mm(self, value: float, unit: str) -> float:
        """Convert a distance value to millimeters"""
        if unit == "cm":
            return value * 10
        elif unit == "m":
            return value * 1000
        return value  # already in mm
    
    def _convert_to_degrees(self, value: float, unit: str) -> float:
        """Convert an angle value to degrees"""
        import math
        if unit == "rad":
            return math.degrees(value)
        return value  # already in degrees
    
    def save(self):
        """Save the component configuration"""
        # Validate inputs
        if self.component_var.get() == "Select component":
            self._show_error("Please select a component")
            return
        
        if self.nozzles_var.get() == "Select number":
            self._show_error("Please select number of nozzles")
            return
        
        if self.nozzle_ref_var.get() == "Select reference":
            self._show_error("Please select nozzle reference")
            return
        
        # Validate numeric fields
        try:
            performance = float(self.performance_var.get())
            if not 0 <= performance <= 100:
                self._show_error("Performance must be between 0 and 100")
                return
        except ValueError:
            self._show_error("Please enter a valid performance percentage")
            return
        
        try:
            d_component = float(self.d_component_var.get())
            dz_pump = float(self.dz_pump_var.get())
            angle = float(self.angle_var.get())
        except ValueError:
            self._show_error("Please enter valid numeric values for measurements")
            return
        
        # Convert values to standard units
        d_component_mm = self._convert_to_mm(d_component, self.d_component_unit_var.get())
        dz_pump_mm = self._convert_to_mm(dz_pump, self.dz_pump_unit_var.get())
        angle_deg = self._convert_to_degrees(angle, self.angle_unit_var.get())
        
        # Prepare data for table
        self.result = {
            "Component": self.component_var.get(),
            "Nozzle Ref": self.nozzle_ref_var.get(),
            "D_C_N (mm)": str(d_component_mm),
            "DZ_P_N (mm)": str(dz_pump_mm),
            "Intergration Angle": str(angle_deg),
            "Targeted Washing Preformance": str(performance)
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