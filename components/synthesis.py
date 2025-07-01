import os
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
from components.custom_button import CustomButton
import math
from PIL import Image, ImageTk

from utils.open_image import open_image

class Synthesis(ctk.CTkFrame):
    def __init__(self, parent, controller, circuits):
        super().__init__(parent)
        self.controller = controller
        self.circuits = circuits

        self.component_icons = {
            "pump": "assets/icons/pump.png",
            "component": "assets/icons/component.png",
            "t_connector": "assets/icons/connector_t.png",
            "y_connector": "assets/icons/connector_y.png",
            "straight_connector": "assets/icons/connector_s.png"
        }

        # Grid settings
        self.grid_size = 20
        self.component_spacing = 120
        self.line_width = 2
        self.component_size = 60

        # Main container for the synthesis
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Control panel
        self.control_panel = ctk.CTkFrame(self.main_container, height=70)
        self.control_panel.pack(fill="x", pady=(0, 10))
        self.control_panel.pack_propagate(False)

        # Download button
        self.download_btn = CustomButton(
            master=self.control_panel,
            text="Download Circuit Image",
            font=controller.fonts.get("default", None),
            icon_path="assets/icons/upload.png",
            icon_side="left",
            outlined=False,
            command=self.download_image
        )
        self.download_btn.pack(side="right", padx=10)

        # Refresh button
        self.refresh_btn = ctk.CTkButton(
            self.control_panel,
            text="Refresh Circuit",
            command=self.draw_circuit
        )
        self.refresh_btn.pack(side="right", padx=(0, 10), pady=10)

        self.canva = tk.Canvas(self.main_container, bg="white")
        self.canva.pack(fill="both", expand=True)
        
        # Draw the circuit when initialized
        self.canva.after(100, self.draw_circuit)

    def snap_to_grid(self, x, y):
        """Snap coordinates to grid"""
        return (round(x / self.grid_size) * self.grid_size,
                round(y / self.grid_size) * self.grid_size)

    def draw_grid(self):
        """Draw a light grid for reference"""
        width = self.canva.winfo_width()
        height = self.canva.winfo_height()
        
        for x in range(0, width, self.grid_size):
            self.canva.create_line(x, 0, x, height, fill="#f0f0f0", width=1)
        for y in range(0, height, self.grid_size):
            self.canva.create_line(0, y, width, y, fill="#f0f0f0", width=1)

    def draw_pump(self, x, y, name=""):
        """Draw a pump component"""
        x, y = self.snap_to_grid(x, y)
        size = self.component_size
        
        # Pump body (circle)
        self.canva.create_oval(x - size//2, y - size//2, x + size//2, y + size//2,
                              outline="blue", fill="lightblue", width=self.line_width)
        
        # Impeller (inner circle with lines)
        inner_size = size // 3
        self.canva.create_oval(x - inner_size//2, y - inner_size//2, 
                              x + inner_size//2, y + inner_size//2,
                              outline="darkblue", width=2)
        
        # Impeller blades
        for angle in [0, 45, 90, 135]:
            rad = math.radians(angle)
            x1 = x + (inner_size//3) * math.cos(rad)
            y1 = y + (inner_size//3) * math.sin(rad)
            x2 = x + (inner_size//2) * math.cos(rad)
            y2 = y + (inner_size//2) * math.sin(rad)
            self.canva.create_line(x1, y1, x2, y2, fill="darkblue", width=2)
        
        # Connection points
        self.canva.create_oval(x - 3, y - size//2 - 3, x + 3, y - size//2 + 3, 
                              fill="red", outline="darkred")  # Input
        self.canva.create_oval(x - 3, y + size//2 - 3, x + 3, y + size//2 + 3, 
                              fill="green", outline="darkgreen")  # Output
        
        # Label
        self.canva.create_text(x, y + size//2 + 20, text=name[:15] + "..." if len(name) > 15 else name, 
                              font=("Arial", 8), anchor="n")

    def draw_component(self, x, y, name="", comp_type="component"):
        """Draw a generic component"""
        x, y = self.snap_to_grid(x, y)
        size = self.component_size
        
        # Component body (rectangle)
        self.canva.create_rectangle(x - size//2, y - size//3, x + size//2, y + size//3,
                                   outline="black", fill="lightgray", width=self.line_width)
        
        # Connection points
        self.canva.create_oval(x - size//2 - 3, y - 3, x - size//2 + 3, y + 3, 
                              fill="red", outline="darkred")  # Input
        self.canva.create_oval(x + size//2 - 3, y - 3, x + size//2 + 3, y + 3, 
                              fill="green", outline="darkgreen")  # Output
        
        # Label
        self.canva.create_text(x, y + size//2 + 10, text=name[:12] + "..." if len(name) > 12 else name, 
                              font=("Arial", 8), anchor="n")

    def draw_connection_line(self, x1, y1, x2, y2, parameters=None):
        """Draw connection lines with 90-degree angles only"""
        x1, y1 = self.snap_to_grid(x1, y1)
        x2, y2 = self.snap_to_grid(x2, y2)
        
        # Create L-shaped connection (horizontal then vertical)
        if abs(x2 - x1) > abs(y2 - y1):
            # Horizontal first
            mid_x = x2
            mid_y = y1
        else:
            # Vertical first
            mid_x = x1
            mid_y = y2
        
        # Draw the connection lines
        line_color = "black"
        if parameters and parameters.get("type"):
            # Color code by pipe type
            pipe_type = parameters.get("type", "").lower()
            if "a" in pipe_type:
                line_color = "red"
            elif "b" in pipe_type:
                line_color = "blue"
            elif "c" in pipe_type:
                line_color = "green"
        
        self.canva.create_line(x1, y1, mid_x, mid_y, fill=line_color, width=self.line_width + 1)
        self.canva.create_line(mid_x, mid_y, x2, y2, fill=line_color, width=self.line_width + 1)
        
        # Add parameter info if available
        if parameters:
            mid_point_x = (x1 + x2) // 2
            mid_point_y = (y1 + y2) // 2
            info_text = f"Ø{parameters.get('diameter', 'N/A')}mm\nL:{parameters.get('length', 'N/A')}m"
            self.canva.create_text(mid_point_x, mid_point_y - 20, text=info_text, 
                                  font=("Arial", 7), fill="purple", anchor="center")

    def draw_circuit(self):
        """Draw the complete synthetic circuit"""
        self.canva.delete("all")
        
        # Draw grid
        self.canva.update()
        self.draw_grid()
        
        # Get canvas dimensions
        width = self.canva.winfo_width()
        height = self.canva.winfo_height()
        
        if not self.circuits or not self.circuits.get("circuits"):
            self.draw_no_circuit_message(width, height)
            return
        
        # Draw each circuit
        y_offset = 100
        for circuit_data in self.circuits["circuits"]:
            circuit = circuit_data.get("circuit", {})
            self.draw_single_circuit(circuit, y_offset, width)
            y_offset += 300  # Space between circuits

    def draw_no_circuit_message(self, width, height):
        """Draw message when no circuits are available"""
        self.canva.create_text(width//2, height//2, 
                              text="No circuits to display\nLoad a circuit configuration to view", 
                              font=("Arial", 16), fill="gray", anchor="center")

    def draw_single_circuit(self, circuit, y_offset, canvas_width):
        """Draw a single circuit with proper formatting"""
        components = circuit.get("components", [])
        connections = circuit.get("connections", [])
        
        if not components:
            return
        
        # Calculate grid layout
        max_components_per_row = 4
        component_positions = {}
        
        # Position components in a grid
        for i, component in enumerate(components):
            row = i // max_components_per_row
            col = i % max_components_per_row
            
            x = 150 + col * self.component_spacing
            y = y_offset + row * self.component_spacing
            
            # Snap to grid
            x, y = self.snap_to_grid(x, y)
            component_positions[component["id"]] = (x, y)
            
            # Draw component based on type
            if component["type"] == "pump":
                self.draw_pump(x, y, component["name"])
            else:
                self.draw_component(x, y, component["name"], component["type"])
        
        # Draw connections
        for connection in connections:
            from_id = connection["from"]
            to_id = connection["to"]
            parameters = connection.get("parameters", {})
            
            if from_id in component_positions and to_id in component_positions:
                from_pos = component_positions[from_id]
                to_pos = component_positions[to_id]
                
                # Adjust connection points to component edges
                from_x = from_pos[0] + self.component_size//2
                from_y = from_pos[1]
                to_x = to_pos[0] - self.component_size//2
                to_y = to_pos[1]
                
                self.draw_connection_line(from_x, from_y, to_x, to_y, parameters)


    def download_image(self):
        """Save the canvas as an image file"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
                title="Save Circuit Image"
            )
            
            if filename:
                # Get canvas size
                self.canva.update()
                x = self.canva.winfo_rootx()
                y = self.canva.winfo_rooty()
                width = self.canva.winfo_width()
                height = self.canva.winfo_height()
                
                # Take screenshot of canvas area
                import PIL.ImageGrab as ImageGrab
                image = ImageGrab.grab((x, y, x + width, y + height))
                image.save(filename)
                
                print(f"Circuit image saved as {filename}")
        except Exception as e:
            print(f"Error saving image: {e}")



