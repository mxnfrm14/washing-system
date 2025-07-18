import customtkinter as ctk
from tkinter import messagebox
from components.custom_button import CustomButton


class GeneralSettings(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        ctk.set_default_color_theme("theme.json")

        # Tank data dictionary (will be replaced with database later)
        # self.tank_data = {
        #     "Tank S": {"supplier": "ChemCorp Ltd", "volume": "50"},
        #     "Tank M": {"supplier": "FluidTech Inc", "volume": "150"},
        #     "Tank L": {"supplier": "AquaSystems Pro", "volume": "300"}
        # }

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
            command=self.save_to_disk
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
            command=lambda: self.save_and_next()
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

        # Get fluid data from DataManager
        fluid_data = controller.data_manager.get_fluids_data()
        fluid_names = []
        if fluid_data:
            for item in fluid_data:
                name = item.get('LLG Name')
                if name:
                    fluid_names.append(str(name))
        
        # Fallback to default values if no data found
        if not fluid_names:
            fluid_names = ["Water", "Detergent", "Solvent"]
        
        self.liquid_name_dropdown = ctk.CTkOptionMenu(
            self.form_container,
            values=fluid_names,
            font=controller.fonts.get("default", None),
            dropdown_font=controller.fonts.get("default", None),
            width=230
        )
        self.liquid_name_dropdown.set("Select liquid")
        self.liquid_name_dropdown.grid(row=0, column=1, columnspan=2, sticky="w", pady=10)

        self.vehicle_label = ctk.CTkLabel(
            self.form_container, 
            text="Vehicle Project", 
            font=controller.fonts.get("default", None),
            anchor="w"
        )
        self.vehicle_label.grid(row=0, column=3, sticky="w", pady=10)

        self.vehicle_entry = ctk.CTkEntry(
            self.form_container,
            placeholder_text="Vehicle Project Name",
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

        # self.tank_ref_label = ctk.CTkLabel(
        #     self.form_container, 
        #     text="Tank Ref.", 
        #     font=controller.fonts.get("default", None),
        #     anchor="w"
        # )
        # self.tank_ref_label.grid(row=1, column=3, sticky="w", pady=10)

        # self.tank_ref_dropdown = ctk.CTkOptionMenu(
        #     self.form_container,
        #     values=["Tank S", "Tank M", "Tank L"],
        #     font=controller.fonts.get("default", None),
        #     dropdown_font=controller.fonts.get("default", None),
        #     width=230,
        #     command=self.update_tank_details
        # )
        # self.tank_ref_dropdown.set("Select tank")
        # self.tank_ref_dropdown.grid(row=1, column=4, columnspan=2, sticky="w", pady=10)

        # # Tank ref details (Supplier and Volume)
        # self.tank_details_frame = ctk.CTkFrame(self.form_container, fg_color="transparent")
        # self.tank_details_frame.grid(row=2, column=3, columnspan=3, sticky="ew", pady=(0, 10))
        
        # self.supplier_label = ctk.CTkLabel(
        #     self.tank_details_frame,
        #     text="Supplier : XXXXXX",
        #     font=controller.fonts.get("default", None),
        #     text_color="gray"
        # )
        # self.supplier_label.pack(side="left", padx=(0, 30))
        
        # self.volume_label = ctk.CTkLabel(
        #     self.tank_details_frame,
        #     text="Volume : X L",
        #     font=controller.fonts.get("default", None),
        #     text_color="gray"
        # )
        # self.volume_label.pack(side="left")

        # Row 3: Liquid Volume
        self.liquid_volume_label = ctk.CTkLabel(
            self.form_container, 
            text="Liquid Volume (Tank)", 
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
        self.dirt_type_label.grid(row=1, column=3, sticky="w", pady=10)

        # Get dirt data from DataManager
        dirt_data = controller.data_manager.get_dirt_data()
        dirt_types = []
        if dirt_data:
            for item in dirt_data:
                dirt_type = item.get('Dirt Type')
                if dirt_type:
                    dirt_types.append(str(dirt_type))
        
        # Fallback to default values if no data found
        if not dirt_types:
            dirt_types = ["Dirt", "Autre"]
        
        self.dirt_type_dropdown = ctk.CTkOptionMenu(
            self.form_container,
            values=dirt_types,
            font=controller.fonts.get("default", None),
            dropdown_font=controller.fonts.get("default", None),
            width=230
        )
        self.dirt_type_dropdown.set("Select dirt type")
        self.dirt_type_dropdown.grid(row=1, column=4, sticky="w", pady=10)  

    
    # =========================== Methodes ==========================
    def get_configuration(self):
        """Get the current configuration from the form"""
        return {
            "liquid_name": self.liquid_name_dropdown.get(),
            "vehicle": self.vehicle_entry.get(),
            "liquid_temperature": {
                "value": self.liquid_temp_entry.get(),
                "unit": self.temp_unit_dropdown.get()
            },
            # "tank_ref": self.tank_ref_dropdown.get(),
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
    
    def load_configuration(self, config_data):
        """Load configuration into the form"""
        try:
            config = config_data.get("general_settings", {})
            # Clear all entry fields first to prevent duplication
            self.vehicle_entry.delete(0, 'end')
            self.liquid_temp_entry.delete(0, 'end')
            self.liquid_volume_entry.delete(0, 'end')
            self.power_voltage_entry.delete(0, 'end')

            self.vehicle_entry._activate_placeholder()
            self.liquid_temp_entry._activate_placeholder()
            self.liquid_volume_entry._activate_placeholder()
            self.power_voltage_entry._activate_placeholder()
            
            if config.get("liquid_name"):
                self.liquid_name_dropdown.set(config["liquid_name"])
            if config.get("vehicle"):
                self.vehicle_entry.insert(0, config["vehicle"])
            if config.get("liquid_temperature"):
                temp_config = config["liquid_temperature"]
                if temp_config.get("value"):
                    self.liquid_temp_entry.insert(0, temp_config["value"])
                if temp_config.get("unit"):
                    self.temp_unit_dropdown.set(temp_config["unit"])
                self.update_fahrenheit()
            # if config.get("tank_ref"):
            #     self.tank_ref_dropdown.set(config["tank_ref"])
            #     self.update_tank_details(config["tank_ref"])
            if config.get("liquid_volume"):
                volume_config = config["liquid_volume"]
                if volume_config.get("value"):
                    self.liquid_volume_entry.insert(0, volume_config["value"])
                if volume_config.get("unit"):
                    self.volume_unit_dropdown.set(volume_config["unit"])
            if config.get("power_voltage"):
                voltage_config = config["power_voltage"]
                if voltage_config.get("value"):
                    self.power_voltage_entry.insert(0, voltage_config["value"])
                if voltage_config.get("unit"):
                    self.voltage_unit_dropdown.set(voltage_config["unit"])
            if config.get("dirt_type"):
                self.dirt_type_dropdown.set(config["dirt_type"])
            
            
        except Exception as e:
            print(f"Error loading general settings configuration: {e}")

    def save_current_configuration(self):
        """Save the configuration via the controller"""
        config_data = self.get_configuration()

        # Update controller's config data
        self.controller.update_config_data("general_settings", config_data)
        

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

    # def update_tank_details(self, selected_tank):
    #     """Update supplier and volume labels based on selected tank"""
    #     if selected_tank in self.tank_data:
    #         tank_info = self.tank_data[selected_tank]
    #         self.supplier_label.configure(text=f"Supplier : {tank_info['supplier']}")
    #         self.volume_label.configure(text=f"Volume : {tank_info['volume']} L")
    #     else:
    #         self.supplier_label.configure(text="Supplier : XXXXXX")
    #         self.volume_label.configure(text="Volume : X L")
    
    def save_and_next(self):
        """Save configuration and navigate to the next page"""
        # Use the on_leave_page method to handle saving and validation
        self.on_leave_page()
        
        # Navigate to the next page
        self.controller.show_page("washing_components")
    
    def is_form_completed(self):
        """Check if the form is sufficiently completed to mark as done"""
        # Get the current form values
        config = self.get_configuration()
        
        # Check each field against its initial/default value and empty string
        required_fields = [
            config['liquid_name'] != "Select liquid",
            # config['tank_ref'] != "Select tank",
            config['vehicle'] != "" and config['vehicle'] is not None,
            config['liquid_temperature']['value'] != "" and config['liquid_temperature']['value'] is not None,
            config['liquid_volume']['value'] != "" and config['liquid_volume']['value'] is not None,
            config['power_voltage']['value'] != "" and config['power_voltage']['value'] is not None,
            config['dirt_type'] != "Select dirt type"
        ]
        
        # Return True if ALL of the required fields are filled
        return all(required_fields)
    
    def on_leave_page(self):
        """Called when navigating away from this page"""
        # Save the current configuration
        self.save_current_configuration()
        
        # Check if the form is still complete enough to be marked as completed
        if self.is_form_completed():
            self.controller.mark_page_completed("general_settings")
        else:
            # If it's no longer complete, mark as incomplete
            self.controller.mark_page_incomplete("general_settings")
    
    def on_show_page(self):
        """Called when the page is shown"""
        # Check if the form is still complete
        if self.is_form_completed():
            self.controller.mark_page_completed("general_settings")
        else:
            self.controller.mark_page_incomplete("general_settings")
    
    def reset_app(self):
        """Reset the application to its initial state"""
        self.liquid_name_dropdown.set("Select liquid")
        # self.tank_ref_dropdown.set("Select tank")
        self.vehicle_entry.delete(0, 'end')
        self.vehicle_entry._activate_placeholder()
        self.liquid_temp_entry.delete(0, 'end')
        self.liquid_temp_entry._activate_placeholder()
        self.liquid_volume_entry.delete(0, 'end')
        self.liquid_volume_entry._activate_placeholder()
        self.power_voltage_entry.delete(0, 'end')
        self.power_voltage_entry._activate_placeholder()
        self.dirt_type_dropdown.set("Select dirt type")
        self.temp_unit_dropdown.set("°C")
        self.volume_unit_dropdown.set("L")
        self.voltage_unit_dropdown.set("V")
        self.fareniheit_label.configure(text="0.0°F")
        # self.supplier_label.configure(text="Supplier : XXXXXX")
        # self.volume_label.configure(text="Volume : X L")