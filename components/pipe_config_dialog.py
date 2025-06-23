import customtkinter as ctk
from typing import Dict, Any, Callable, Optional
from components.custom_button import CustomButton
from utils.appearance_manager import AppearanceManager

class PipeConfigDialog(ctk.CTkToplevel):
    """
    Dialog window for configuring pipe/connection details
    """
    def __init__(self, parent, controller, from_component: str, to_component: str, 
                 on_save: Callable[[Dict[str, Any]], None], edit_data: Optional[Dict[str, Any]] = None):
        super().__init__(parent)
        self.controller = controller
        self.from_component = from_component
        self.to_component = to_component
        self.on_save = on_save
        self.edit_data = edit_data  # If provided, we're editing existing connection
        self.result = None
        
        # Configure window
        self.title("Pipe configuration")
        self.geometry("450x500")
        self.resizable(False, False)
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        # Center window on parent
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (450 // 2)
        y = (self.winfo_screenheight() // 2) - (500 // 2)
        self.geometry(f"+{x}+{y}")
        
        # Register with appearance manager
        AppearanceManager.register(self)
        
        # Initialize pipe data
        self.ref_number = "xxx-xxx-xxx"
        self.supplier_value = "xxxxxxxx"
        
        # Create UI
        self._create_ui()
        
        # Load edit data if provided
        if self.edit_data:
            self._load_edit_data()
        
        # Update appearance
        self.update_appearance()
        
        # Focus on first input
        self.diameter_entry.focus()

    def _create_ui(self):
        """Create the dialog UI"""
        # Main container
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        self.title_label = ctk.CTkLabel(
            self.main_container,
            text="Pipe configuration",
            font=self.controller.fonts.get("title", None),
            anchor="w"
        )
        self.title_label.pack(pady=(0, 10))
        
        # Connection info
        self.connection_label = ctk.CTkLabel(
            self.main_container,
            text=f"{self.from_component} → {self.to_component}",
            font=self.controller.fonts.get("subtitle", None),
            anchor="w"
        )
        self.connection_label.pack(pady=(0, 20))
        
        # Form frame
        self.form_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.form_frame.pack(fill="both", expand=True)
        
        # Configure grid
        self.form_frame.grid_columnconfigure(0, weight=0, minsize=120)
        self.form_frame.grid_columnconfigure(1, weight=1)
        
        row = 0
        
        # Diameter
        self._create_field(
            row, "Diameter (mm)",
            self._create_diameter_entry()
        )
        row += 1
        
        # Type
        self._create_field(
            row, "Type",
            self._create_type_dropdown()
        )
        row += 1
        
        # Info labels (Ref and Supplier)
        self._create_info_labels(row)
        row += 1
        
        # Length
        self._create_field(
            row, "Length",
            self._create_length_field()
        )
        row += 1
        
        # Inclination
        self._create_field(
            row, "Inclination",
            self._create_inclination_field()
        )
        row += 1
        
        # Bend Radius (initially hidden)
        self.bend_radius_label = ctk.CTkLabel(
            self.form_frame,
            text="Bend Radius",
            font=self.controller.fonts.get("default", None),
            anchor="w"
        )
        self.bend_radius_frame = self._create_bend_radius_field()
        
        # Initially hide bend radius if straight
        if not hasattr(self, 'inclination_var') or self.inclination_var.get() == "straight":
            self.bend_radius_label.grid_forget()
            self.bend_radius_frame.grid_forget()
        else:
            self._create_field(row, "Bend Radius", self.bend_radius_frame)
        
        # Buttons frame
        self.buttons_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.buttons_frame.pack(fill="x", pady=(30, 0))
        
        # OK button (centered)
        self.ok_button = ctk.CTkButton(
            self.buttons_frame,
            text="OK",
            font=self.controller.fonts.get("default", None),
            command=self.save,
            width=100
        )
        self.ok_button.pack()
    
    def _create_field(self, row: int, label_text: str, field_widget):
        """Create a field with label"""
        # Label
        label = ctk.CTkLabel(
            self.form_frame,
            text=label_text,
            font=self.controller.fonts.get("default", None),
            anchor="w"
        )
        label.grid(row=row, column=0, sticky="w", pady=8, padx=(0, 10))
        
        # Field widget
        field_widget.grid(row=row, column=1, sticky="ew", pady=8)
        
        # Store label reference if it's bend radius
        if "Bend Radius" in label_text:
            self.bend_radius_label = label
    
    def _create_diameter_entry(self):
        """Create diameter entry field (replaces dropdown)"""
        self.diameter_var = ctk.StringVar()
        entry = ctk.CTkEntry(
            self.form_frame,
            textvariable=self.diameter_var,
            placeholder_text="Enter diameter",
            font=self.controller.fonts.get("default", None),
            width=250
        )
        self.diameter_entry = entry
        return entry
    
    def _create_type_dropdown(self):
        """Create pipe type dropdown"""
        self.type_var = ctk.StringVar(value="Placeholder")
        dropdown = ctk.CTkOptionMenu(
            self.form_frame,
            variable=self.type_var,
            values=["Type A", "Type B", "Type C", "Type D"],
            font=self.controller.fonts.get("default", None),
            dropdown_font=self.controller.fonts.get("default", None),
            width=250,
            command=self._on_type_change
        )
        return dropdown
    
    def _create_info_labels(self, row: int):
        """Create Ref and Supplier info labels"""
        info_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        info_frame.grid(row=row, column=0, columnspan=2, sticky="ew", pady=5)
        
        # Configure grid
        info_frame.grid_columnconfigure(0, weight=0, minsize=120)
        info_frame.grid_columnconfigure(1, weight=1)
        
        # Empty space for alignment
        ctk.CTkLabel(info_frame, text="", width=120).grid(row=0, column=0)
        
        # Info container
        info_container = ctk.CTkFrame(info_frame, fg_color="transparent")
        info_container.grid(row=0, column=1, sticky="w")
        
        # Ref label
        self.ref_label = ctk.CTkLabel(
            info_container,
            text=f"Ref n° : {self.ref_number}",
            font=ctk.CTkFont(family="Encode Sans Expanded", size=11),
            text_color=("gray30", "gray70")
        )
        self.ref_label.pack(side="left", padx=(0, 30))
        
        # Supplier label
        self.supplier_label = ctk.CTkLabel(
            info_container,
            text=f"Supplier: {self.supplier_value}",
            font=ctk.CTkFont(family="Encode Sans Expanded", size=11),
            text_color=("gray30", "gray70")
        )
        self.supplier_label.pack(side="left")
    
    def _create_length_field(self):
        """Create length field with unit dropdown"""
        frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        
        # Entry
        self.length_var = ctk.StringVar()
        entry = ctk.CTkEntry(
            frame,
            textvariable=self.length_var,
            placeholder_text="Placeholder",
            font=self.controller.fonts.get("default", None),
            width=160
        )
        entry.pack(side="left", padx=(0, 10))
        
        # Unit dropdown
        self.length_unit_var = ctk.StringVar(value="mm")
        unit_dropdown = ctk.CTkOptionMenu(
            frame,
            variable=self.length_unit_var,
            values=["mm", "cm", "m"],
            font=self.controller.fonts.get("default", None),
            dropdown_font=self.controller.fonts.get("default", None),
            width=80
        )
        unit_dropdown.pack(side="left")
        
        return frame
    
    def _create_inclination_field(self):
        """Create inclination radio buttons"""
        frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        
        self.inclination_var = ctk.StringVar(value="straight")
        
        # Straight button
        self.straight_button = ctk.CTkButton(
            frame,
            text="Straight",
            font=self.controller.fonts.get("default", None),
            command=lambda: self._set_inclination("straight"),
            fg_color="#243783",
            text_color="white",
            width=100
        )
        self.straight_button.pack(side="left", padx=(0, 20))
        
        # Bent button
        self.bent_button = ctk.CTkButton(
            frame,
            text="Bent",
            font=self.controller.fonts.get("default", None),
            command=lambda: self._set_inclination("bent"),
            fg_color="transparent",
            text_color="#243783",
            width=100
        )
        self.bent_button.pack(side="left")
        
        return frame
    
    def _create_bend_radius_field(self):
        """Create bend radius field with unit dropdown"""
        frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        
        # Entry
        self.bend_radius_var = ctk.StringVar()
        entry = ctk.CTkEntry(
            frame,
            textvariable=self.bend_radius_var,
            placeholder_text="Placeholder",
            font=self.controller.fonts.get("default", None),
            width=160
        )
        entry.pack(side="left", padx=(0, 10))
        
        # Unit dropdown
        self.bend_radius_unit_var = ctk.StringVar(value="mm")
        unit_dropdown = ctk.CTkOptionMenu(
            frame,
            variable=self.bend_radius_unit_var,
            values=["mm", "cm", "m"],
            font=self.controller.fonts.get("default", None),
            dropdown_font=self.controller.fonts.get("default", None),
            width=80
        )
        unit_dropdown.pack(side="left")
        
        return frame
    
    def _set_inclination(self, value):
        """Set inclination and update UI"""
        self.inclination_var.set(value)
        
        # Update button styles
        if value == "straight":
            self.straight_button.configure(fg_color="#243783", text_color="white")
            self.bent_button.configure(fg_color="transparent", text_color="#243783")
            # Hide bend radius
            self.bend_radius_label.grid_forget()
            self.bend_radius_frame.grid_forget()
        else:
            self.straight_button.configure(fg_color="transparent", text_color="#243783")
            self.bent_button.configure(fg_color="#243783", text_color="white")
            # Show bend radius
            self.bend_radius_label.grid(row=5, column=0, sticky="w", pady=8, padx=(0, 10))
            self.bend_radius_frame.grid(row=5, column=1, sticky="ew", pady=8)
    
    def _on_type_change(self, value):
        """Update ref and supplier based on type selection"""
        # Simulate pipe data lookup
        pipe_data = {
            "Type A": {"ref": "PIP-001-A", "supplier": "FlowTech"},
            "Type B": {"ref": "PIP-002-B", "supplier": "AquaPipe"},
            "Type C": {"ref": "PIP-003-C", "supplier": "HydroSys"},
            "Type D": {"ref": "PIP-004-D", "supplier": "PipeMax"}
        }
        
        data = pipe_data.get(value, {"ref": "xxx-xxx-xxx", "supplier": "xxxxxxxx"})
        self.ref_number = data["ref"]
        self.supplier_value = data["supplier"]
        
        # Update labels
        self.ref_label.configure(text=f"Ref n° : {self.ref_number}")
        self.supplier_label.configure(text=f"Supplier: {self.supplier_value}")
    
    def _convert_to_mm(self, value: float, unit: str) -> float:
        """Convert a distance value to millimeters"""
        if unit == "cm":
            return value * 10
        elif unit == "m":
            return value * 1000
        return value  # already in mm
    
    def _load_edit_data(self):
        """Load data for editing"""
        if not self.edit_data:
            return
        
        params = self.edit_data.get('parameters', {})
        
        # Set values from saved data
        diameter_str = str(params.get('diameter', ''))
        self.diameter_var.set(diameter_str)
        
        self.type_var.set(params.get('type', 'Placeholder'))
        self._on_type_change(params.get('type', ''))
        
        # Length - convert back from mm to display unit
        length_mm = params.get('length', 0)
        # For editing, we'll show in the unit that makes most sense
        if length_mm >= 1000:
            self.length_var.set(str(length_mm / 1000))
            self.length_unit_var.set("m")
        elif length_mm >= 100:
            self.length_var.set(str(length_mm / 10))
            self.length_unit_var.set("cm")
        else:
            self.length_var.set(str(length_mm))
            self.length_unit_var.set("mm")
        
        # Inclination
        inclination = params.get('inclination', 'straight')
        self._set_inclination(inclination)
        
        # Bend radius
        if inclination == 'bent':
            bend_radius_mm = params.get('bend_radius', 0)
            if bend_radius_mm >= 1000:
                self.bend_radius_var.set(str(bend_radius_mm / 1000))
                self.bend_radius_unit_var.set("m")
            elif bend_radius_mm >= 100:
                self.bend_radius_var.set(str(bend_radius_mm / 10))
                self.bend_radius_unit_var.set("cm")
            else:
                self.bend_radius_var.set(str(bend_radius_mm))
                self.bend_radius_unit_var.set("mm")
    
    def save(self):
        """Save the pipe configuration"""
        # Validate inputs
        if not self.diameter_var.get():
            self._show_error("Please enter a diameter")
            return
        
        try:
            diameter = float(self.diameter_var.get())
            if diameter <= 0:
                self._show_error("Diameter must be positive")
                return
        except ValueError:
            self._show_error("Please enter a valid diameter")
            return
        
        if self.type_var.get() == "Placeholder":
            self._show_error("Please select a pipe type")
            return
        
        try:
            length = float(self.length_var.get())
            if length <= 0:
                self._show_error("Length must be positive")
                return
        except ValueError:
            self._show_error("Please enter a valid length")
            return
        
        if self.length_unit_var.get() not in ["mm", "cm", "m"]:
            self._show_error("Please select a length unit")
            return
        
        # Validate bend radius if bent
        bend_radius_mm = 0
        if self.inclination_var.get() == "bent":
            try:
                bend_radius = float(self.bend_radius_var.get())
                if bend_radius <= 0:
                    self._show_error("Bend radius must be positive")
                    return
                if self.bend_radius_unit_var.get() not in ["mm", "cm", "m"]:
                    self._show_error("Please select a bend radius unit")
                    return
                # Convert to mm
                bend_radius_mm = self._convert_to_mm(bend_radius, self.bend_radius_unit_var.get())
            except ValueError:
                self._show_error("Please enter a valid bend radius")
                return
        
        # Convert length to mm
        length_mm = self._convert_to_mm(length, self.length_unit_var.get())
        
        # Prepare result (all distances in mm)
        self.result = {
            'diameter': diameter,  # Already in mm
            'type': self.type_var.get(),
            'length': length_mm,
            'inclination': self.inclination_var.get(),
            'bend_radius': bend_radius_mm,
            'ref_number': self.ref_number,
            'supplier': self.supplier_value
        }
        
        # Call the save callback
        if self.on_save:
            self.on_save(self.result)
        
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
        # Update inclination buttons based on current state
        if hasattr(self, 'inclination_var'):
            self._set_inclination(self.inclination_var.get())
    
    def destroy(self):
        """Clean up when destroying"""
        AppearanceManager.unregister(self)
        super().destroy()