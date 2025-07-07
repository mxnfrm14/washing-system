import os
from tkinter import messagebox
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

        # Component icon paths (same as CircuitDesigner)
        self.component_icons = {
            "pump": "assets/icons/pump.png",
            "component": "assets/icons/component.png",
            "t_connector": "assets/icons/connector_t.png",
            "y_connector": "assets/icons/connector_y.png",
            "straight_connector": "assets/icons/connector_s.png"
        }
        
        # Load icons
        self.loaded_icons = {}
        self._load_icons()

        # Layout settings
        self.pump_x = 100  # X position for pumps
        self.connector_x = 400  # X position for connectors
        self.component_x = 700  # X position for components
        self.vertical_spacing = 150  # Spacing between circuits
        self.output_spacing = 80  # Spacing between pump outputs
        self.component_spacing = 60  # Spacing between components
        self.icon_size = 40  # Size of component icons

        # Connection routing
        self.connection_segments = []  # Store all connection segments for overlap detection

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

        # Canvas
        self.canvas = tk.Canvas(self.main_container, bg="white", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        # Draw the circuit when initialized
        self.canvas.after(100, self.draw_circuit)

    def _load_icons(self):
        """Load all component icons"""
        for comp_type, icon_path in self.component_icons.items():
            try:
                if os.path.exists(icon_path):
                    # Load icon with appropriate size
                    icon_image = open_image(icon_path, (self.icon_size, self.icon_size))
                    
                    if icon_image:
                        # Convert to PhotoImage for canvas
                        icon_photo = ImageTk.PhotoImage(icon_image)
                        self.loaded_icons[comp_type] = {
                            'light': icon_photo,
                            'dark': icon_photo  # Use same icon for both modes for now
                        }
                        print(f"Successfully loaded icon for {comp_type}")
                    else:
                        print(f"Failed to load image for {comp_type} from {icon_path}")
                else:
                    print(f"Icon file does not exist: {icon_path}")
            except Exception as e:
                print(f"Error loading icon {icon_path} for {comp_type}: {e}")
    
        print(f"Loaded icons: {list(self.loaded_icons.keys())}")

    def draw_circuit(self):
        """Draw the complete synthetic circuit with clean layout"""
        self.canvas.delete("all")
        self.connection_segments = []  # Reset connection segments
        
        # Get canvas dimensions
        self.canvas.update()
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        # Check if we have circuits
        if not self.circuits or not isinstance(self.circuits, dict):
            self.draw_no_circuit_message(width, height)
            return
        
        # Get circuit data and connection summary
        circuit_data = self.circuits.get("circuits", [])
        connection_summary = self.circuits.get("connection_summary", [])
        
        if not circuit_data:
            self.draw_no_circuit_message(width, height)
            return
        
        # Process and draw each circuit
        current_y = 100  # Starting Y position
        
        for i, pump_data in enumerate(connection_summary):
            if not isinstance(pump_data, dict):
                continue
                
            # Get the corresponding circuit data
            circuit = None
            for c in circuit_data:
                if c.get("pump_index") == pump_data.get("pump_index"):
                    circuit = c.get("circuit", {})
                    break
            
            if circuit:
                # Draw this pump's circuit
                circuit_height = self._draw_pump_circuit(
                    pump_data, 
                    circuit, 
                    current_y
                )
                current_y += circuit_height + self.vertical_spacing

    def _draw_pump_circuit(self, pump_data, circuit, start_y):
        """Draw a single pump circuit with clean layout"""
        pump_name = pump_data.get("pump_name", "Unknown Pump")
        outputs = pump_data.get("outputs", {})
        
        # Count total components to determine circuit height
        total_components = sum(len(comps) for comps in outputs.values())
        num_outputs = len(outputs)
        
        # Calculate pump position (centered for its outputs)
        if num_outputs == 0:
            pump_y = start_y
            circuit_height = 100
        else:
            # Calculate Y positions for outputs
            output_positions = {}
            current_comp_y = start_y
            
            for output_num in sorted(outputs.keys()):
                components = outputs[output_num]
                if components:
                    # Center of this output's components
                    output_center_y = current_comp_y + (len(components) - 1) * self.component_spacing / 2
                    output_positions[output_num] = output_center_y
                    current_comp_y += len(components) * self.component_spacing
                else:
                    output_positions[output_num] = current_comp_y
                    current_comp_y += self.component_spacing
            
            # Center pump between all outputs
            pump_y = sum(output_positions.values()) / len(output_positions)
            circuit_height = max(self.component_spacing, (total_components + 1) * self.component_spacing)
        
        # Draw pump
        pump_id = self._draw_component(self.pump_x, pump_y, "pump", pump_name)
        
        # Process each output
        component_positions = {}  # Track positions of all components
        
        for output_num, components in outputs.items():
            if not components:
                continue
                
            # Get connectors from circuit data
            connectors = self._find_connectors_for_output(circuit, pump_name, components)
            
            # Layout components for this output
            output_start_y = output_positions.get(output_num, start_y)
            
            # Draw connectors in middle
            connector_positions = []
            for i, connector in enumerate(connectors):
                conn_y = output_start_y + i * self.component_spacing * 0.7  # Slightly closer spacing
                conn_type = connector.get('type', 'straight_connector')
                conn_name = connector.get('name', f'Connector {i+1}')
                conn_id = self._draw_component(self.connector_x, conn_y, conn_type, conn_name)
                connector_positions.append((conn_id, self.connector_x, conn_y))
                component_positions[conn_name] = (self.connector_x, conn_y)
            
            # Draw washing components on right
            for i, component in enumerate(components):
                comp_y = output_start_y + i * self.component_spacing
                comp_name = component.get('name', f'Component {i+1}')
                comp_id = self._draw_component(self.component_x, comp_y, "component", comp_name)
                component_positions[comp_name] = (self.component_x, comp_y)
            
            # Draw connections with smart routing
            # 1. Connect pump to first connector or component
            if connector_positions:
                self._draw_smart_connection(
                    self.pump_x + self.icon_size//2, pump_y,
                    connector_positions[0][1] - self.icon_size//2, connector_positions[0][2]
                )
                
                # Connect connectors in sequence
                for i in range(len(connector_positions) - 1):
                    self._draw_smart_connection(
                        connector_positions[i][1] + self.icon_size//2, connector_positions[i][2],
                        connector_positions[i+1][1] - self.icon_size//2, connector_positions[i+1][2]
                    )
                
                # Connect last connector to components
                if components:
                    last_conn = connector_positions[-1]
                    for i, component in enumerate(components):
                        comp_y = output_start_y + i * self.component_spacing
                        self._draw_smart_connection(
                            last_conn[1] + self.icon_size//2, last_conn[2],
                            self.component_x - self.icon_size//2, comp_y
                        )
            else:
                # Direct connection from pump to components
                for i, component in enumerate(components):
                    comp_y = output_start_y + i * self.component_spacing
                    self._draw_smart_connection(
                        self.pump_x + self.icon_size//2, pump_y,
                        self.component_x - self.icon_size//2, comp_y
                    )
        
        return circuit_height

    def _find_connectors_for_output(self, circuit, pump_name, output_components):
        """Find connectors between pump and components for a specific output"""
        connectors = []
        components = circuit.get('components', [])
        connections = circuit.get('connections', [])
        
        # Find all connector components
        connector_comps = [c for c in components if c.get('type') in ['t_connector', 'y_connector', 'straight_connector']]
        
        # Simple heuristic: assign connectors based on connection patterns
        # This is a simplified version - you might need more sophisticated logic
        for connector in connector_comps:
            connectors.append({
                'name': connector.get('name'),
                'type': connector.get('type')
            })
        
        return connectors[:len(output_components)]  # Limit to reasonable number

    def _draw_component(self, x, y, comp_type, name):
        """Draw a component with its icon"""
        # Get the appropriate icon
        mode = ctk.get_appearance_mode().lower()
        icon = self.loaded_icons.get(comp_type, {}).get(mode)
        
        if icon:
            # Draw icon
            item_id = self.canvas.create_image(
                x, y,
                image=icon,
                anchor="center",
                tags=("component", comp_type)
            )
        else:
            # Debug: print why icon is not available
            print(f"Icon not available for {comp_type}, mode: {mode}")
            print(f"Available icons: {list(self.loaded_icons.keys())}")
            if comp_type in self.loaded_icons:
                print(f"Available modes for {comp_type}: {list(self.loaded_icons[comp_type].keys())}")
            
            # Try to load icon on demand
            icon_path = self.component_icons.get(comp_type)
            if icon_path and os.path.exists(icon_path):
                try:
                    icon_image = open_image(icon_path, (self.icon_size, self.icon_size))
                    if icon_image:
                        icon = ImageTk.PhotoImage(icon_image)
                        # Store for future use
                        if comp_type not in self.loaded_icons:
                            self.loaded_icons[comp_type] = {}
                        self.loaded_icons[comp_type][mode] = icon
                        
                        # Draw the icon
                        item_id = self.canvas.create_image(
                            x, y,
                            image=icon,
                            anchor="center",
                            tags=("component", comp_type)
                        )
                    else:
                        # Still fallback to shape if image loading fails
                        item_id = self._draw_fallback_shape(x, y, comp_type)
                except Exception as e:
                    print(f"Error loading icon on demand for {comp_type}: {e}")
                    item_id = self._draw_fallback_shape(x, y, comp_type)
            else:
                print(f"Icon path not found: {icon_path}")
                item_id = self._draw_fallback_shape(x, y, comp_type)
    
        # Draw label
        self.canvas.create_text(
            x, y + self.icon_size//2 + 10,
            text=name[:15] + "..." if len(name) > 15 else name,
            font=("Arial", 9),
            anchor="n"
        )
        
        return item_id

    def _draw_fallback_shape(self, x, y, comp_type):
        """Draw fallback shape when icon is not available"""
        size = self.icon_size // 2
        
        if comp_type == "pump":
            # Circle for pump
            item_id = self.canvas.create_oval(
                x - size, y - size, x + size, y + size,
                fill="#88D8FF", outline="#243783", width=2
            )
        elif comp_type == "component":
            # Rectangle for component
            item_id = self.canvas.create_rectangle(
                x - size, y - size, x + size, y + size,
                fill="#FF88B0", outline="#243783", width=2
            )
        else:
            # Diamond for connectors
            points = [x, y-size, x+size, y, x, y+size, x-size, y]
            item_id = self.canvas.create_polygon(
                points, fill="#88FFB8", outline="#243783", width=2
            )
        
        return item_id

    def _draw_smart_connection(self, x1, y1, x2, y2):
        """Draw connection with smart routing (0°, 45°, 90° angles only)"""
        # Determine best routing strategy
        dx = x2 - x1
        dy = y2 - y1
        
        # If nearly straight horizontal or vertical, use straight line
        if abs(dy) < 5:  # Horizontal
            self._draw_connection_segment(x1, y1, x2, y2, "#243783")
        elif abs(dx) < 5:  # Vertical
            self._draw_connection_segment(x1, y1, x2, y2, "#243783")
        else:
            # Use L-shaped routing (90° angles)
            # Determine if we should go horizontal-first or vertical-first
            mid_x = x1 + dx * 0.7  # Go 70% horizontally first
            
            # Draw first segment (horizontal)
            self._draw_connection_segment(x1, y1, mid_x, y1, "#243783")
            
            # Draw second segment (vertical)
            self._draw_connection_segment(mid_x, y1, mid_x, y2, "#243783")
            
            # Draw third segment (horizontal)
            self._draw_connection_segment(mid_x, y2, x2, y2, "#243783")

    def _draw_connection_segment(self, x1, y1, x2, y2, color):
        """Draw a single connection segment and store it for overlap detection"""
        line_id = self.canvas.create_line(
            x1, y1, x2, y2,
            fill=color,
            width=2,
            arrow="last" if x2 > x1 + 20 else None,  # Arrow only for significant horizontal movement
            smooth=False
        )
        
        # Store segment for overlap detection
        self.connection_segments.append({
            'id': line_id,
            'start': (x1, y1),
            'end': (x2, y2)
        })
        
        return line_id

    def draw_no_circuit_message(self, width, height):
        """Draw message when no circuits are available"""
        self.canvas.create_text(
            width//2, height//2,
            text="No circuits to display\nConfigure and save circuits first",
            font=("Arial", 16),
            fill="gray",
            anchor="center"
        )

    def download_image(self):
        """Save the canvas as an image file"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
                title="Save Circuit Image"
            )
            
            if filename:
                # Create postscript and convert to image
                ps = self.canvas.postscript(colormode='color')
                from PIL import Image, ImageDraw
                import io
                
                # Alternative method using screenshot
                self.canvas.update()
                x = self.canvas.winfo_rootx()
                y = self.canvas.winfo_rooty()
                width = self.canvas.winfo_width()
                height = self.canvas.winfo_height()
                
                # Import here to handle different platforms
                try:
                    import PIL.ImageGrab as ImageGrab
                    image = ImageGrab.grab((x, y, x + width, y + height))
                    image.save(filename)
                    print(f"Circuit image saved as {filename}")
                except ImportError:
                    # Fallback for systems without ImageGrab
                    messagebox.showwarning(
                        "Export Not Available",
                        "Image export requires PIL.ImageGrab which is not available on this system."
                    )
        except Exception as e:
            print(f"Error saving image: {e}")
            messagebox.showerror("Export Error", f"Failed to save image: {str(e)}")