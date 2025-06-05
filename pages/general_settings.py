import customtkinter as ctk
from components.custom_button import CustomButton
import json

class GeneralSettings(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        ctk.set_default_color_theme("theme.json")

        # Tank data dictionary (will be replaced with database later)
        self.tank_data = {
            "Tank S": {"supplier": "ChemCorp Ltd", "volume": "50"},
            "Tank M": {"supplier": "FluidTech Inc", "volume": "150"},
            "Tank L": {"supplier": "AquaSystems Pro", "volume": "300"}
        }

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
            text="General Settings", 
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

        self.divider = ctk.CTkFrame(self.main_container, height=2, corner_radius=0, fg_color="#F8F8F8")
        self.divider.pack(pady=(0, 20), fill="x")


        # =========================== Navigation button ==========================
        # Bottom frame for next button
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
            command=lambda: controller.show_page("washing_components")
        )
        self.next_button.pack(side="right")

        # =========================== Content Area ==========================
        # Form container
        self.form_container = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.form_container.pack(fill="both", expand=True, padx=200, pady=(40, 40))

        # Configure grid for form - consistent column structure
        self.form_container.grid_columnconfigure(0, weight=0, minsize=150)  # Left label column
        self.form_container.grid_columnconfigure(1, weight=1)               # Left input column start
        self.form_container.grid_columnconfigure(2, weight=0)               # Left input column end
        self.form_container.grid_columnconfigure(3, weight=0, minsize=150)  # Right label column
        self.form_container.grid_columnconfigure(4, weight=1)               # Right input column start
        self.form_container.grid_columnconfigure(5, weight=0)               # Right input column end

        # Row 1: Liquid Name and Vehicle
        self.liquid_name_label = ctk.CTkLabel(
            self.form_container, 
            text="Liquid Name", 
            font=controller.fonts.get("default", None),
            anchor="w"
        )
        self.liquid_name_label.grid(row=0, column=0, sticky="w", pady=10)

        self.liquid_name_dropdown = ctk.CTkOptionMenu(
            self.form_container,
            values=["Water", "Detergent", "Solvent"],
            font=controller.fonts.get("default", None),
            dropdown_font=controller.fonts.get("default", None),
            width=230
        )
        self.liquid_name_dropdown.set("Select liquid")
        self.liquid_name_dropdown.grid(row=0, column=1, columnspan=2, sticky="w", pady=10)

        self.vehicle_label = ctk.CTkLabel(
            self.form_container, 
            text="Vehicle", 
            font=controller.fonts.get("default", None),
            anchor="w"
        )
        self.vehicle_label.grid(row=0, column=3, sticky="w", pady=10)

        self.vehicle_entry = ctk.CTkEntry(
            self.form_container,
            placeholder_text="Vehicle",
            font=controller.fonts.get("default", None),
            width=230
        )
        self.vehicle_entry.grid(row=0, column=4, columnspan=2, sticky="w", pady=10)

        # Row 2: Liquid Temperature and Tank Ref
        self.liquid_temp_label = ctk.CTkLabel(
            self.form_container, 
            text="Liquid Temperature", 
            font=controller.fonts.get("default", None),
            anchor="w"
        )
        self.liquid_temp_label.grid(row=1, column=0, sticky="w", pady=10)

        self.temp_frame = ctk.CTkFrame(self.form_container, fg_color="transparent")
        self.temp_frame.grid(row=1, column=1, columnspan=2, sticky="w", pady=10)
        
        self.liquid_temp_entry = ctk.CTkEntry(
            self.temp_frame,
            placeholder_text="Temperature",
            font=controller.fonts.get("default", None),
            width=140
        )
        self.liquid_temp_entry.pack(side="left", padx=(0, 10))

        self.temp_unit_dropdown = ctk.CTkOptionMenu(
            self.temp_frame,
            values=["°K", "°C"],
            font=controller.fonts.get("default", None),
            dropdown_font=controller.fonts.get("default", None),
            width=80
        )
        self.temp_unit_dropdown.set("°C")
        self.temp_unit_dropdown.pack(side="left")

        # Fahrenheit conversion label
        self.fareniheit_label = ctk.CTkLabel(
            self.form_container,
            text="0.0°F",
            font=controller.fonts.get("default", None),
            text_color="gray"
        )
        self.fareniheit_label.grid(row=2, column=1, columnspan=2, sticky="w", pady=(0, 10))
        
        # Add bindings to update the Fahrenheit value
        self.liquid_temp_entry.bind("<KeyRelease>", self.update_fahrenheit)
        self.temp_unit_dropdown.configure(command=self.update_fahrenheit)

        self.tank_ref_label = ctk.CTkLabel(
            self.form_container, 
            text="Tank Ref.", 
            font=controller.fonts.get("default", None),
            anchor="w"
        )
        self.tank_ref_label.grid(row=1, column=3, sticky="w", pady=10)

        self.tank_ref_dropdown = ctk.CTkOptionMenu(
            self.form_container,
            values=["Tank S", "Tank M", "Tank L"],
            font=controller.fonts.get("default", None),
            dropdown_font=controller.fonts.get("default", None),
            width=230,
            command=self.update_tank_details
        )
        self.tank_ref_dropdown.set("Select tank")
        self.tank_ref_dropdown.grid(row=1, column=4, columnspan=2, sticky="w", pady=10)

        # Tank ref details (Supplier and Volume)
        self.tank_details_frame = ctk.CTkFrame(self.form_container, fg_color="transparent")
        self.tank_details_frame.grid(row=2, column=3, columnspan=3, sticky="ew", pady=(0, 10))
        
        self.supplier_label = ctk.CTkLabel(
            self.tank_details_frame,
            text="Supplier : XXXXXX",
            font=controller.fonts.get("default", None),
            text_color="gray"
        )
        self.supplier_label.pack(side="left", padx=(0, 30))
        
        self.volume_label = ctk.CTkLabel(
            self.tank_details_frame,
            text="Volume : X L",
            font=controller.fonts.get("default", None),
            text_color="gray"
        )
        self.volume_label.pack(side="left")

        # Row 3: Liquid Volume
        self.liquid_volume_label = ctk.CTkLabel(
            self.form_container, 
            text="Liquid Volume", 
            font=controller.fonts.get("default", None),
            anchor="w"
        )
        self.liquid_volume_label.grid(row=3, column=0, sticky="w", pady=10)

        self.volume_frame = ctk.CTkFrame(self.form_container, fg_color="transparent")
        self.volume_frame.grid(row=3, column=1, columnspan=2, sticky="w", pady=10)
        
        self.liquid_volume_entry = ctk.CTkEntry(
            self.volume_frame,
            placeholder_text="Volume",
            font=controller.fonts.get("default", None),
            width=140
        )
        self.liquid_volume_entry.pack(side="left", padx=(0, 10))

        self.volume_unit_dropdown = ctk.CTkOptionMenu(
            self.volume_frame,
            values=["L", "mL"],
            font=controller.fonts.get("default", None),
            dropdown_font=controller.fonts.get("default", None),
            width=80
        )
        self.volume_unit_dropdown.set("L")
        self.volume_unit_dropdown.pack(side="left")

        # Row 4: Power Voltage
        self.power_voltage_label = ctk.CTkLabel(
            self.form_container, 
            text="Power Voltage", 
            font=controller.fonts.get("default", None),
            anchor="w"
        )
        self.power_voltage_label.grid(row=4, column=0, sticky="w", pady=10)

        self.voltage_frame = ctk.CTkFrame(self.form_container, fg_color="transparent")
        self.voltage_frame.grid(row=4, column=1, columnspan=2, sticky="w", pady=10)
        
        self.power_voltage_entry = ctk.CTkEntry(
            self.voltage_frame,
            placeholder_text="Voltage",
            font=controller.fonts.get("default", None),
            width=140
        )
        self.power_voltage_entry.pack(side="left", padx=(0, 10))

        self.voltage_unit_dropdown = ctk.CTkOptionMenu(
            self.voltage_frame,
            values=["V", "mV"],
            font=controller.fonts.get("default", None),
            dropdown_font=controller.fonts.get("default", None),
            width=80
        )
        self.voltage_unit_dropdown.set("V")
        self.voltage_unit_dropdown.pack(side="left")

        self.dirt_type_label = ctk.CTkLabel(
            self.form_container, 
            text="Dirt type", 
            font=controller.fonts.get("default", None),
            anchor="w"
        )
        self.dirt_type_label.grid(row=3, column=3, sticky="w", pady=10)

        self.dirt_type_dropdown = ctk.CTkOptionMenu(
            self.form_container,
            values=["Dirt", "Autre"],
            font=controller.fonts.get("default", None),
            dropdown_font=controller.fonts.get("default", None),
            width=230
        )
        self.dirt_type_dropdown.set("Select dirt type")
        self.dirt_type_dropdown.grid(row=3, column=4, sticky="w", pady=10)  

    
    # =========================== Methodes ==========================
    def save_configuration(self):
        """Save the current configuration"""
        # Collect all form values
        config_data = {
            "liquid_name": self.liquid_name_dropdown.get(),
            "vehicle": self.vehicle_entry.get(),
            "liquid_temperature": {
                "value": self.liquid_temp_entry.get(),
                "unit": self.temp_unit_dropdown.get()
            },
            "tank_ref": self.tank_ref_dropdown.get(),
            "liquid_volume": {
                "value": self.liquid_volume_entry.get(),
                "unit": self.volume_unit_dropdown.get()
            },
            "power_voltage": {
                "value": self.power_voltage_entry.get(),
                "unit": self.voltage_unit_dropdown.get()
            },
            "dirt_type": self.dirt_type_dropdown.get()
        }

        # Print individual values
        print("=== Configuration Values ===")
        print(f"Liquid Name: {config_data['liquid_name']}")
        print(f"Vehicle: {config_data['vehicle']}")
        print(f"Liquid Temperature: {config_data['liquid_temperature']['value']} {config_data['liquid_temperature']['unit']}")
        print(f"Tank Reference: {config_data['tank_ref']}")
        print(f"Liquid Volume: {config_data['liquid_volume']['value']} {config_data['liquid_volume']['unit']}")
        print(f"Power Voltage: {config_data['power_voltage']['value']} {config_data['power_voltage']['unit']}")
        print(f"Dirt Type: {config_data['dirt_type']}")

        # Convert to JSON and print
        config_json = json.dumps(config_data, indent=2)
        print("\n=== JSON Configuration ===")
        print(config_json)
        
    def update_appearance(self):
        """Update any appearance-dependent elements"""
        # If you have any appearance-dependent elements, update them here
        pass

    def convert_temp(self, temp):
        """Convert Celsius or Kelvin to Fahrenheit"""
        try:
            temp_value = float(temp)
            if self.temp_unit_dropdown.get() == "°K":
                return (temp_value - 273.15)* 9/5 + 32
            elif self.temp_unit_dropdown.get() == "°C":
                return (temp_value * 9/5) + 32
            return temp_value  # Default case
        except ValueError:
            return 0  # Return default value if conversion fails
    
    def update_fahrenheit(self, *args):
            """Update the Fahrenheit conversion label"""
            try:
                fahrenheit = self.convert_temp(self.liquid_temp_entry.get())
                self.fareniheit_label.configure(text=f"{fahrenheit:.1f}°F")
            except:
                self.fareniheit_label.configure(text="0.0°F")

    def update_tank_details(self, selected_tank):
        """Update supplier and volume labels based on selected tank"""
        if selected_tank in self.tank_data:
            tank_info = self.tank_data[selected_tank]
            self.supplier_label.configure(text=f"Supplier : {tank_info['supplier']}")
            self.volume_label.configure(text=f"Volume : {tank_info['volume']} L")
        else:
            self.supplier_label.configure(text="Supplier : XXXXXX")
            self.volume_label.configure(text="Volume : X L")