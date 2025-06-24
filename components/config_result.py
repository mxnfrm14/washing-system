import customtkinter as ctk
from components.custom_button import CustomButton


class ConfigResult(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.config = self.controller.get_config_data()

        # Main vertical layout
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # --- General Settings Block ---
        self._create_general_settings_block()

        # --- Circuits Blocks ---
        circuits = self.config.get("circuits", [])
        for idx, circuit in enumerate(circuits):
            self._create_circuit_block(circuit, idx+1)

    def _create_general_settings_block(self):
        general = self.config.get("general_settings", {})
        block = ctk.CTkFrame(self.main_container, corner_radius=10, border_width=1, border_color="#cccccc", fg_color="transparent")
        block.pack(fill="x", pady=(0, 10), padx=5)

        title = ctk.CTkLabel(block, text="General settings", font=self.controller.fonts.get("subtitle", None), anchor="w")
        title.grid(row=0, column=0, sticky="w", padx=10, pady=(8, 2), columnspan=6)

        # Display fields in two rows
        labels = [
            ("Vehicle", "Vehicule name"),
            ("Tank Name", "Tank Name"),
            ("Tank Ref.", "Tank Ref."),
            ("Power Voltage", "Power Voltage"),
            ("Liquid Name", "Liquid Name"),
            ("Liquid Temperature", "Liquid Temperature"),
            ("Liquid Volume", "Liquid Volume"),
        ]
        # First row: Vehicle, Tank Name, Tank Ref., Power Voltage
        for i, (label, key) in enumerate(labels[:4]):
            ctk.CTkLabel(block, text=label, font=self.controller.fonts.get("bold", None)).grid(row=1, column=i, sticky="w", padx=10, pady=(0,2))
            ctk.CTkLabel(block, text=general.get(key, ""), font=self.controller.fonts.get("default", None)).grid(row=2, column=i, sticky="w", padx=10)
        # Second row: Liquid Name, Liquid Temperature, Liquid Volume
        for i, (label, key) in enumerate(labels[4:]):
            ctk.CTkLabel(block, text=label, font=self.controller.fonts.get("bold", None)).grid(row=3, column=i, sticky="w", padx=10, pady=(8,2))
            ctk.CTkLabel(block, text=general.get(key, ""), font=self.controller.fonts.get("default", None)).grid(row=4, column=i, sticky="w", padx=10)

    def _create_circuit_block(self, circuit, idx):
        block = ctk.CTkFrame(self.main_container, corner_radius=10, border_width=1, border_color="#cccccc", fg_color="#f8f8f8")
        block.pack(fill="x", pady=(0, 10), padx=5)

        # Circuit title
        ctk.CTkLabel(block, text=f"CIRCUIT {idx}", font=self.controller.fonts.get("subtitle", None), anchor="w").pack(anchor="w", padx=10, pady=(8, 2))

        # Horizontal layout for the circuit diagram
        diagram = ctk.CTkFrame(block, fg_color="#f8f8f8")
        diagram.pack(fill="x", padx=10, pady=8)

        # --- Pump ---
        pump_frame = ctk.CTkFrame(diagram, fg_color="transparent")
        pump_frame.pack(side="left", padx=(0, 20))
        ctk.CTkLabel(pump_frame, text="🦾", font=("Arial", 22)).pack()
        ctk.CTkLabel(pump_frame, text="Pump", text_color="#2a3a6c", font=("Arial", 11, "bold")).pack()
        ctk.CTkLabel(pump_frame, text=circuit.get("pump_name", "PpumpOUT"), font=("Arial", 10)).pack()

        # --- Flow rate & Pressure loss (left) ---
        left_info = ctk.CTkFrame(diagram, fg_color="transparent")
        left_info.pack(side="left", padx=(0, 10))
        ctk.CTkLabel(left_info, text="Flow rate", text_color="green", font=("Arial", 10)).pack(anchor="w")
        ctk.CTkLabel(left_info, text="perte de pression", text_color="red", font=("Arial", 10)).pack(anchor="w")

        # --- Connector ---
        connector_frame = ctk.CTkFrame(diagram, fg_color="transparent")
        connector_frame.pack(side="left", padx=(0, 10))
        ctk.CTkLabel(connector_frame, text="⎯■⎯", font=("Arial", 18)).pack()
        ctk.CTkLabel(connector_frame, text="Connector", text_color="#2a3a6c", font=("Arial", 11, "bold")).pack()
        ctk.CTkLabel(connector_frame, text="perte de pression", text_color="red", font=("Arial", 10)).pack()

        # --- Flow rate & Pressure loss (right) ---
        right_info = ctk.CTkFrame(diagram, fg_color="transparent")
        right_info.pack(side="left", padx=(0, 10))
        ctk.CTkLabel(right_info, text="Flow rate", text_color="green", font=("Arial", 10)).pack(anchor="w")
        ctk.CTkLabel(right_info, text="perte de pression", text_color="red", font=("Arial", 10)).pack(anchor="w")

        # --- Nozzle ---
        nozzle_frame = ctk.CTkFrame(diagram, fg_color="transparent")
        nozzle_frame.pack(side="left", padx=(0, 10))
        ctk.CTkLabel(nozzle_frame, text="))", font=("Arial", 18)).pack()
        ctk.CTkLabel(nozzle_frame, text="Nozzle", text_color="#2a3a6c", font=("Arial", 11, "bold")).pack()
        ctk.CTkLabel(nozzle_frame, text="Pression IN\nvitesse en sortie\nvitesse sortie / v max\nliquid consumed", font=("Arial", 10), anchor="w", justify="left").pack()

        # --- Component WC ---
        wc_frame = ctk.CTkFrame(diagram, fg_color="transparent")
        wc_frame.pack(side="left", padx=(0, 10))
        ctk.CTkLabel(wc_frame, text="◆◆\n◆◆", font=("Arial", 18)).pack()
        ctk.CTkLabel(wc_frame, text="component WC", text_color="#2a3a6c", font=("Arial", 11, "bold")).pack()
        ctk.CTkLabel(wc_frame, text="Cleanliness", font=("Arial", 10)).pack()
