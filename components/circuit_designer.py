import customtkinter as ctk
import tkinter as tk
import tkinter.messagebox as messagebox
import math
import os
from PIL import Image, ImageTk
from utils.appearance_manager import AppearanceManager
from utils.open_image import open_image
from components.pipe_config_dialog import PipeConfigDialog

class CircuitDesigner(ctk.CTkFrame):
    """Circuit designer canvas with icon-based components"""
    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Register with appearance manager
        AppearanceManager.register(self)
        
        # Component properties - MUST BE DEFINED FIRST
        self.component_properties = {
            "pump": {
                'max_connections': 3,
                'direction': 'out',
                'flow_rate': 100,
                'size': (40, 40)
            },
            "component": {
                'max_connections': 1,
                'direction': 'in',
                'size': (30, 30)
            },
            "t_connector": {
                'max_connections': 3,
                'direction': 'both',
                'flow_division': True,
                'size': (35, 35)
            },
            "y_connector": {
                'max_connections': 3,
                'direction': 'both',
                'flow_division': True,
                'size': (35, 35)
            },
            "straight_connector": {
                'max_connections': 2,
                'direction': 'both',
                'flow_division': True,
                'size': (35, 35)
            }
        }
        
        # Component icons paths
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
        
        # Canvas state
        self.current_mode = {"mode": "move", "component": None}
        self.selected_component = None
        self.placed_items = {}
        self.connectors = []
        self.first_connection_item_id = None
        self.mode_selector = None
        self.detail_list = None  # Reference to detail list for component tracking
        self.circuits_controller = None  # Reference to circuits page controller for cross-tab syncing
        
        # Drag state
        self._drag_data = {"x": 0, "y": 0, "item": None, "offset_x": 0, "offset_y": 0}
        
        self._create_ui()
        self.update_appearance()
    
    def _load_icons(self):
        """Load all component icons"""
        for comp_type, icon_path in self.component_icons.items():
            try:
                # Check if file exists
                if not os.path.exists(icon_path):
                    print(f"Icon file not found: {icon_path}")
                    continue
                
                # Get size from component properties
                size = self.component_properties.get(comp_type, {}).get('size', (30, 30))
                
                # Load icon with appropriate size
                icon_light = open_image(icon_path, size)
                icon_dark = open_image(icon_path, size)
                
                if icon_light and icon_dark:
                    # Convert to PhotoImage for canvas
                    self.loaded_icons[comp_type] = {
                        'light': ImageTk.PhotoImage(icon_light),
                        'dark': ImageTk.PhotoImage(icon_dark)
                    }
                    print(f"Successfully loaded icon for {comp_type}")
                else:
                    print(f"Failed to load icon for {comp_type} from {icon_path}")
            except Exception as e:
                print(f"Error loading icon {icon_path} for {comp_type}: {e}")
    
    def _create_ui(self):
        """Create the canvas UI"""
        # Canvas frame
        self.canvas_frame = ctk.CTkFrame(self, corner_radius=8)
        self.canvas_frame.pack(fill="both", expand=True)
        
        # Create canvas
        self.canvas = tk.Canvas(
            self.canvas_frame,
            bg="white",
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Add reset button on canvas (top-right corner)
        from components.custom_button import CustomButton
        
        # Create a frame for the button to ensure proper styling
        self.button_frame = ctk.CTkFrame(self.canvas, fg_color="transparent")
        
        self.reset_button = ctk.CTkButton(
            self.button_frame,
            text="Reset",
            font=self.controller.fonts.get("default", None) if hasattr(self.controller, 'fonts') else None,
            command=self._handle_reset,
            fg_color="#243783",
            text_color="#F8F8F8",
            hover_color="#12205C",
            width=90,
            height=32
        )
        self.reset_button.pack()
        
        # Create window for button frame on canvas
        self.canvas.create_window(
            10, 10,  # Will be updated when canvas resizes
            window=self.button_frame,
            anchor="nw",
            tags=("reset_button",)
        )
        
        # Bind events
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.canvas.bind("<Motion>", self.on_canvas_hover)
        self.canvas.bind("<Configure>", self._on_canvas_resize)
        
        # Grid overlay (optional)
        self._draw_grid()
    
    def _on_canvas_resize(self, event):
        """Reposition reset button when canvas resizes"""
        # Position button at top-right with padding
        x = event.width - 100  # Button width + padding
        y = 10
        self.canvas.coords("reset_button", x, y)
    
    def _handle_reset(self):
        """Handle reset button click with confirmation"""
        result = messagebox.askyesno(
            "Reset Canvas", 
            "Are you sure you want to clear all components and connections?"
        )
        if result:
            self.reset_canvas()
    
    def _draw_grid(self):
        """Draw a grid overlay on the canvas"""
        grid_size = 20
        width = 800 * 20  # Default size
        height = 600
        
        # Draw vertical lines
        for x in range(0, width, grid_size):
            self.canvas.create_line(x, 0, x, height, fill="#E0E0E0", tags="grid")
        
        # Draw horizontal lines
        for y in range(0, height, grid_size):
            self.canvas.create_line(0, y, width, y, fill="#E0E0E0", tags="grid")
        
        # Send grid to back
        self.canvas.tag_lower("grid")
        
        # Ensure reset button stays on top
        self.canvas.tag_raise("reset_button")
    
    def set_mode(self, mode_data):
        """Set current mode from mode selector"""
        self.current_mode = mode_data
        
        # If mode contains a component (connector), set it as selected
        if mode_data.get("component"):
            self.selected_component = mode_data["component"]
        
        self.reset_connection_state()
        self.reset_drag_state()
        
        # Update cursor
        if mode_data["mode"] == "place":
            self.canvas.config(cursor="crosshair")
        elif mode_data["mode"] == "delete":
            self.canvas.config(cursor="X_cursor")
        elif mode_data["mode"] == "connect":
            self.canvas.config(cursor="hand2")
        else:
            self.canvas.config(cursor="arrow")
    
    def set_selected_component(self, component):
        """Set component selected from detail list"""
        self.selected_component = component
    
    def set_detail_list(self, detail_list):
        """Set reference to detail list for component tracking"""
        self.detail_list = detail_list
    
    def set_circuits_controller(self, circuits_controller):
        """Set reference to circuits page controller for cross-tab syncing"""
        self.circuits_controller = circuits_controller
    
    def on_canvas_click(self, event):
        """Handle canvas click based on current mode"""
        # Check if click is on the reset button area
        widget = event.widget.winfo_containing(event.x_root, event.y_root)
        if widget != self.canvas:
            return  # Click was on a button, not the canvas
        
        x, y = event.x, event.y
        
        # Don't place if clicking too close to reset button
        canvas_width = self.canvas.winfo_width()
        if x > canvas_width - 120 and y < 50:  # Reset button area
            return
        
        target_item = self.find_item_at(x, y)
        
        mode = self.current_mode["mode"]
        
        if mode == "place":
            if self.selected_component:
                self.place_component(x, y, self.selected_component)
                # Clear connector selection after placing
                if self.mode_selector and hasattr(self.mode_selector, 'clear_connector_selection'):
                    self.mode_selector.clear_connector_selection()
                # Switch back to move mode after placing a connector
                if self.selected_component.get("type") == "connector":
                    self.mode_selector.set_mode("move")
        elif mode == "move":
            if target_item:
                self.start_drag(target_item, x, y)
        elif mode == "connect":
            if target_item:
                self.handle_connection_click(target_item)
            else:
                # Check if clicking on a connection line
                connection = self.find_connection_at(x, y)
                if connection:
                    self.edit_connection(connection)
        elif mode == "delete":
            if target_item:
                self.delete_item(target_item)
            else:
                # Check if clicking on a connection line
                connection = self.find_connection_at(x, y)
                if connection:
                    self.delete_connection(connection)
    
    def on_canvas_drag(self, event):
        """Handle canvas drag"""
        if self.current_mode["mode"] == "move" and self._drag_data["item"]:
            self.perform_drag(event.x, event.y)
    
    def on_canvas_release(self, event):
        """Handle canvas release"""
        if self.current_mode["mode"] == "move" and self._drag_data["item"]:
            self.end_drag()
    
    def on_canvas_hover(self, event):
        """Handle hover effects"""
        item = self.find_item_at(event.x, event.y)
        connection = self.find_connection_at(event.x, event.y)
        mode = self.current_mode["mode"]
        
        # Update hover cursor based on mode and item
        if item:
            if mode == "delete":
                self.canvas.config(cursor="X_cursor")
            elif mode == "connect":
                self.canvas.config(cursor="pencil")
            elif mode == "move":
                self.canvas.config(cursor="fleur")
            else:
                self.canvas.config(cursor="arrow")
        elif connection:
            if mode == "connect":
                # Show hand cursor for editable connections
                self.canvas.config(cursor="hand2")
                # Highlight connection on hover
                self.canvas.itemconfig(connection['line_id'], width=3)
            elif mode == "delete":
                # Show delete cursor for deletable connections
                self.canvas.config(cursor="X_cursor")
                # Highlight connection in red
                self.canvas.itemconfig(connection['line_id'], fill="#FF0000", width=3)
        else:
            # Reset connection appearance
            for conn in self.connectors:
                self.canvas.itemconfig(conn['line_id'], width=2, fill="#243783")
            
            # Reset to mode cursor when not over an item
            if mode == "place":
                self.canvas.config(cursor="crosshair")
            elif mode == "delete":
                self.canvas.config(cursor="arrow")
            elif mode == "connect":
                self.canvas.config(cursor="arrow")
            else:
                self.canvas.config(cursor="arrow")
    
    def find_item_at(self, x, y):
        """Find component at coordinates"""
        items = self.canvas.find_overlapping(x-2, y-2, x+2, y+2)
        for item in items:
            # Skip the reset button window
            if self.canvas.type(item) == "window":
                continue
            if item in self.placed_items:
                return item
        return None
    
    def find_connection_at(self, x, y):
        """Find connection line at coordinates"""
        items = self.canvas.find_overlapping(x-5, y-5, x+5, y+5)
        for item in items:
            # Check if it's a connection line
            for conn in self.connectors:
                if conn['line_id'] == item:
                    return conn
        return None
    
    def place_component(self, x, y, component):
        """Place a component on the canvas with improved boundary handling for restoration"""
        # Determine component type
        comp_type = None
        
        # Check if it's a connector with subtype
        if component.get("type") == "connector" and component.get("subtype"):
            comp_type = component.get("subtype")
        elif component.get("type") == "pump":
            comp_type = "pump"
        elif component.get("type") == "component":
            comp_type = "component"
        else:
            # Try to infer from name
            name = component.get("name", "").lower()
            if "pump" in name:
                comp_type = "pump"
            elif "component" in name or "component" in name:
                comp_type = "component"
            elif "t-connector" in name:
                comp_type = "t_connector"
            elif "y-connector" in name:
                comp_type = "y_connector"
            elif "cross-connector" in name:
                comp_type = "straight_connector"
            else:
                print(f"Unknown component type: {component}")
                return
        
        # Check if we have the component type defined
        if comp_type not in self.component_properties:
            print(f"Component type '{comp_type}' not defined in properties")
            return
        
        # Get canvas dimensions with fallback for uninitialized canvas
        self.canvas.update_idletasks()
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # Handle case where canvas is not yet properly sized
        if canvas_width <= 1 or canvas_height <= 1:
            print(f"⚠️ Canvas not properly sized ({canvas_width}x{canvas_height}), using default size")
            canvas_width = 800  # Default width
            canvas_height = 600  # Default height
            # Try to configure canvas size
            self.canvas.configure(width=canvas_width, height=canvas_height)
            self.canvas.update_idletasks()
        
        comp_size = self.component_properties.get(comp_type, {}).get('size', (30, 30))
        half_width = comp_size[0] // 2
        half_height = comp_size[1] // 2
        
        # Constrain position within canvas boundaries with more generous margins
        min_x = half_width + 10
        max_x = canvas_width - half_width - 10
        min_y = half_height + 10
        max_y = canvas_height - half_height - 70  # Extra space for labels
        
        # Ensure boundaries are valid (for very small canvases)
        if max_x <= min_x:
            max_x = max(canvas_width - 10, min_x + 50)
        if max_y <= min_y:
            max_y = max(canvas_height - 10, min_y + 50)
        
        # Apply constraints only if canvas is reasonably sized
        if canvas_width > 100 and canvas_height > 100:
            original_x, original_y = x, y
            x = max(min_x, min(x, max_x))
            y = max(min_y, min(y, max_y))
            
            # Log significant position adjustments
            if abs(x - original_x) > 10 or abs(y - original_y) > 10:
                print(f"🔄 Position adjusted from ({original_x}, {original_y}) to ({x}, {y}) for canvas {canvas_width}x{canvas_height}")
        else:
            # For very small canvases, just ensure minimum distance from edges
            x = max(50, x)
            y = max(50, y)
            print(f"📍 Canvas too small, placing at ({x}, {y}) without constraints")
        
        # Get icon
        mode = ctk.get_appearance_mode().lower()
        icon = self.loaded_icons.get(comp_type, {}).get(mode)
        
        if not icon:
            print(f"No icon loaded for {comp_type} - creating placeholder shape")
            item_id = self._create_placeholder_shape(x, y, comp_type)
        else:
            item_id = self.canvas.create_image(
                x, y,
                image=icon,
                anchor="center",
                tags=("component", comp_type)
            )
        
        # FIXED: Separate original name from display name
        original_name = component.get('name', comp_type)  # Original name without suffixes
        display_name = component.get('display_name', original_name)  # Display name with suffixes
        
        # Create label using display name for UI
        props = self.component_properties.get(comp_type, {})
        if comp_type == "pump" and component.get("max_connections"):
            max_connections = component.get("max_connections")
        else:
            max_connections = props.get('max_connections', 0)
                
        label_text = f"{display_name}\n0/{max_connections}"  # Use display name in UI
        label_id = self.canvas.create_text(
            x, y + 30,
            text=label_text,
            font=("Arial", 9),
            anchor="n",
            tags=("label",)
        )
        
        # FIXED: Store component data with original name for saving
        self.placed_items[item_id] = {
            'type': comp_type,
            'id': component.get('id', ''),
            'name': original_name,  # ← Store original name for saving (no suffixes)
            'display_name': display_name,  # Store display name for UI
            'coords': (x, y),
            'label_id': label_id,
            'current_connections': 0,
            'max_connections': max_connections,
            'direction': props.get('direction', 'both'),
            'component_data': component
        }
        
        # Bring to front
        self.canvas.tag_raise(item_id)
        self.canvas.tag_raise(label_id)
        self.canvas.tag_raise("reset_button")
        
        print(f"Placed {comp_type} '{original_name}' at ({x}, {y}) on canvas {canvas_width}x{canvas_height}")
        
        # Notify about component placement (only for pumps and components, not connectors)
        if comp_type in ["pump", "component"]:
            component_id = component.get('id', component.get('name', comp_type))
            
            if self.circuits_controller and hasattr(self.circuits_controller, '_on_component_placement'):
                self.circuits_controller._on_component_placement(component_id, placed=True)
                self.set_mode({"mode": "move", "component": None})
            elif self.detail_list:
                self.detail_list.mark_component_placed(component_id)


    def _create_placeholder_shape(self, x, y, comp_type):
        """Create a placeholder shape when icon is not available"""
        size = 20  # Default size
        
        if comp_type == "pump":
            # Create a square for pump
            item_id = self.canvas.create_rectangle(
                x - size, y - size, x + size, y + size,
                fill="#88D8FF", outline="#243783", width=2,
                tags=("component", comp_type)
            )
            # Add "P" text
            self.canvas.create_text(
                x, y, text="P", font=("Arial", 16, "bold"),
                fill="#243783", tags=("component", comp_type)
            )
        elif comp_type == "component":
            # Create a triangle for component
            points = [x, y-size, x-size, y+size, x+size, y+size]
            item_id = self.canvas.create_polygon(
                points, fill="#FF88B0", outline="#243783", width=2,
                tags=("component", comp_type)
            )
        elif comp_type in ["t_connector", "y_connector", "straight_connector"]:
            # Create a circle for connectors
            item_id = self.canvas.create_oval(
                x - size, y - size, x + size, y + size,
                fill="#88FFB8", outline="#243783", width=2,
                tags=("component", comp_type)
            )
            # Add connector type indicator
            symbol = {"t_connector": "T", "y_connector": "Y", "straight_connector": "+"}.get(comp_type, "?")
            self.canvas.create_text(
                x, y, text=symbol, font=("Arial", 14, "bold"),
                fill="#243783", tags=("component", comp_type)
            )
        else:
            # Default rectangle
            item_id = self.canvas.create_rectangle(
                x - size, y - size, x + size, y + size,
                fill="#808080", outline="#404040", width=2,
                tags=("component", comp_type)
            )
        
        return item_id
    
    def reset_canvas(self):
        """Clear all components and connections from the canvas"""
        # Collect components that need to be marked as available
        components_to_free = []
        for item_id, item_data in self.placed_items.items():
            if item_data['type'] in ["pump", "component"]:
                components_to_free.append(item_data.get('id', item_data['name']))
        
        # Delete all connections
        for conn in self.connectors[:]:  # Use slice to avoid modifying list while iterating
            self.canvas.delete(conn['line_id'])
        self.connectors.clear()
        
        # Delete all components and their labels
        for item_id, item_data in list(self.placed_items.items()):
            # Delete label
            if 'label_id' in item_data:
                self.canvas.delete(item_data['label_id'])
            # Delete component
            self.canvas.delete(item_id)
        self.placed_items.clear()
        
        # Notify about components being freed
        if self.circuits_controller and hasattr(self.circuits_controller, '_on_component_placement'):
            # Use circuits controller to sync all tabs
            for component_id in components_to_free:
                self.circuits_controller._on_component_placement(component_id, placed=False)
        elif self.detail_list:
            # Just update local detail list
            for component_id in components_to_free:
                self.detail_list.mark_component_available(component_id)
        
        # Reset states
        self.reset_connection_state()
        self.reset_drag_state()
        self.selected_component = None
        
        print("Canvas cleared")
    
    def handle_connection_click(self, item_id):
        """Handle connection between components"""
        if self.first_connection_item_id is None:
            # Start connection - check if component can accept more connections
            item_data = self.placed_items[item_id]
            if item_data['current_connections'] >= item_data['max_connections']:
                messagebox.showwarning(
                    "Connection Limit",
                    f"Component '{item_data['name']}' has reached its maximum number of connections ({item_data['max_connections']})."
                )
                return
            
            self.first_connection_item_id = item_id
            self.highlight_item(item_id, True)
        elif self.first_connection_item_id != item_id:
            # Check both components before proceeding
            from_item = self.placed_items[self.first_connection_item_id]
            to_item = self.placed_items[item_id]
            
            # Check if either component has reached its limit
            if from_item['current_connections'] >= from_item['max_connections']:
                messagebox.showwarning(
                    "Connection Limit",
                    f"Component '{from_item['name']}' has reached its maximum number of connections ({from_item['max_connections']})."
                )
                self.reset_connection_state()
                return
            
            if to_item['current_connections'] >= to_item['max_connections']:
                messagebox.showwarning(
                    "Connection Limit",
                    f"Component '{to_item['name']}' has reached its maximum number of connections ({to_item['max_connections']})."
                )
                self.reset_connection_state()
                return
            
            # Check if connection already exists
            if self.connection_exists(self.first_connection_item_id, item_id):
                messagebox.showwarning(
                    "Duplicate Connection",
                    f"A connection already exists between '{from_item['name']}' and '{to_item['name']}'."
                )
                self.reset_connection_state()
                return

            # Determine correct direction for display
            display_from_id, display_to_id = self._determine_connection_direction(self.first_connection_item_id, item_id)
            
            if display_from_id is None:
                self.reset_connection_state()
                return  # Invalid connection, error already shown
            
            display_from_item = self.placed_items[display_from_id]
            display_to_item = self.placed_items[display_to_id]

            self.highlight_item(item_id, True)  # Highlight target item
            
            # Store temporary variables to capture current state
            current_from_id = self.first_connection_item_id
            current_to_id = item_id
            
            # Use the logically correct order for display
            dialog = PipeConfigDialog(
                self,
                self.controller,
                from_component=display_from_item['name'],  # Use logical direction
                to_component=display_to_item['name'],      # Use logical direction
                on_save=lambda params: self.complete_connection(
                    current_from_id,  # But keep original click order for connection
                    current_to_id, 
                    params
                )
            )
            
            # Bind dialog close event to reset connection state
            dialog.bind("<Destroy>", lambda e: self.on_dialog_closed())
            # Don't reset connection state here
        else:
            # Cancel connection
            self.reset_connection_state()

    def connection_exists(self, from_id, to_id):
        """Check if a connection already exists between two components"""
        for conn in self.connectors:
            if (conn['from_id'] == from_id and conn['to_id'] == to_id) or \
               (conn['from_id'] == to_id and conn['to_id'] == from_id):
                return True
        return False
    
    def complete_connection(self, from_id, to_id, params):
        """Complete the connection and reset state"""
        self.create_connection(from_id, to_id, params)
        self.highlight_item(from_id, False)
        self.highlight_item(to_id, False)
        self.reset_connection_state()
        
        # Clear any selected components and reset mode
        self.selected_component = None
        if self.mode_selector:
            self.mode_selector.set_mode("move")
    
    def create_connection(self, from_id, to_id, parameters=None):
        """Create a connection between two components"""
        if from_id not in self.placed_items or to_id not in self.placed_items:
            print("Error: One or both components not found")
            return False
        
        from_item = self.placed_items[from_id]
        to_item = self.placed_items[to_id]
        
        # Double-check connection limits (safety check)
        if from_item['current_connections'] >= from_item['max_connections']:
            messagebox.showerror(
                "Connection Error",
                f"Cannot connect: {from_item['name']} has reached its maximum connections ({from_item['max_connections']})."
            )
            return False
        
        if to_item['current_connections'] >= to_item['max_connections']:
            messagebox.showerror(
                "Connection Error",
                f"Cannot connect: {to_item['name']} has reached its maximum connections ({to_item['max_connections']})."
            )
            return False
        
        # Check for duplicate connections
        if self.connection_exists(from_id, to_id):
            messagebox.showwarning(
                "Duplicate Connection",
                f"A connection already exists between {from_item['name']} and {to_item['name']}."
            )
            return False
        
        # Determine correct direction based on component types
        actual_from_id, actual_to_id = self._determine_connection_direction(from_id, to_id)
        
        if actual_from_id is None:
            return False  # Invalid connection
        
        actual_from_item = self.placed_items[actual_from_id]
        actual_to_item = self.placed_items[actual_to_id]
        
        # Create visual connection with correct direction
        x1, y1 = actual_from_item['coords']
        x2, y2 = actual_to_item['coords']
        
        # Create line with arrow pointing in the correct direction
        line_id = self.canvas.create_line(
            x1, y1, x2, y2,
            fill="#243783",
            width=2,
            arrow="last",
            smooth=True,
            tags=("connection",)
        )
        
        # Send to back (but above grid)
        self.canvas.tag_lower(line_id)
        self.canvas.tag_lower("grid")
        
        # Keep reset button on top
        self.canvas.tag_raise("reset_button")
        
        # Store connection with parameters (using actual direction)
        connection_data = {
            'line_id': line_id,
            'from_id': actual_from_id,
            'to_id': actual_to_id,
            'from_name': actual_from_item['name'],
            'to_name': actual_to_item['name'],
            'parameters': parameters or {}
        }
        self.connectors.append(connection_data)
        
        # Update connection counts for both original items
        from_item['current_connections'] += 1
        to_item['current_connections'] += 1
        
        # Update labels
        self.update_component_label(from_id)
        self.update_component_label(to_id)
        
        print(f"Connection created: {actual_from_item['name']} -> {actual_to_item['name']}")
        return True

    def _determine_connection_direction(self, item1_id, item2_id):
        """Determine the correct direction for a connection based on component types"""
        item1 = self.placed_items[item1_id]
        item2 = self.placed_items[item2_id]
        
        direction1 = item1['direction']
        direction2 = item2['direction']
        type1 = item1['type']
        type2 = item2['type']
        
        # Check for invalid connections
        if direction1 == 'out' and direction2 == 'out':
            messagebox.showerror(
                "Invalid Connection",
                f"Cannot connect two output components: {item1['name']} and {item2['name']}"
            )
            return None, None
        
        if direction1 == 'in' and direction2 == 'in':
            messagebox.showerror(
                "Invalid Connection", 
                f"Cannot connect two input components: {item1['name']} and {item2['name']}"
            )
            return None, None
        
        # Determine correct direction
        if direction1 == 'out' and direction2 == 'in':
            # item1 (pump) -> item2 (component)
            return item1_id, item2_id
        elif direction1 == 'in' and direction2 == 'out':
            # item2 (pump) -> item1 (component)
            return item2_id, item1_id
        elif direction1 == 'out' and direction2 == 'both':
            # item1 (pump) -> item2 (connector)
            return item1_id, item2_id
        elif direction1 == 'both' and direction2 == 'out':
            # item2 (pump) -> item1 (connector)
            return item2_id, item1_id
        elif direction1 == 'in' and direction2 == 'both':
            # item2 (connector) -> item1 (component)
            return item2_id, item1_id
        elif direction1 == 'both' and direction2 == 'in':
            # item1 (connector) -> item2 (component)
            return item1_id, item2_id
        elif direction1 == 'both' and direction2 == 'both':
            # Both are connectors - use original order but show warning
            messagebox.showinfo(
                "Connector Connection",
                f"Connected {item1['name']} to {item2['name']}. Flow direction: {item1['name']} -> {item2['name']}"
            )
            return item1_id, item2_id
        else:
            messagebox.showerror(
                "Invalid Connection",
                f"Cannot determine connection direction between {item1['name']} and {item2['name']}"
            )
            return None, None
    
    def edit_connection(self, connection):
        """Edit an existing connection"""
        dialog = PipeConfigDialog(
            self,
            self.controller,
            from_component=connection['from_name'],
            to_component=connection['to_name'],
            on_save=lambda params: self.update_connection_parameters(connection, params),
            edit_data=connection
        )
    
    def update_connection_parameters(self, connection, new_params):
        """Update connection parameters"""
        connection['parameters'] = new_params
        print(f"Updated connection parameters: {new_params}")
    
    def update_component_label(self, item_id):
        """Update component label with connection info"""
        if item_id not in self.placed_items:
            return
        
        item = self.placed_items[item_id]
        label_id = item['label_id']
        
        label_text = f"{item['name']}\n{item['current_connections']}/{item['max_connections']}"
        self.canvas.itemconfig(label_id, text=label_text)
    
    def delete_connection(self, connection):
        """Delete a specific connection"""
        # Delete the line
        self.canvas.delete(connection['line_id'])
        
        # Update connection counts
        from_id = connection['from_id']
        to_id = connection['to_id']
        
        if from_id in self.placed_items:
            self.placed_items[from_id]['current_connections'] -= 1
            self.update_component_label(from_id)
        
        if to_id in self.placed_items:
            self.placed_items[to_id]['current_connections'] -= 1
            self.update_component_label(to_id)
        
        # Remove from list
        self.connectors.remove(connection)
        print(f"Deleted connection between {connection.get('from_name', 'Unknown')} and {connection.get('to_name', 'Unknown')}")
    
    def delete_item(self, item_id):
        """Delete a component and its connections"""
        if item_id not in self.placed_items:
            return
        
        item = self.placed_items[item_id]
        
        # Delete connections
        connectors_to_remove = []
        for conn in self.connectors:
            if conn['from_id'] == item_id or conn['to_id'] == item_id:
                # Delete line
                self.canvas.delete(conn['line_id'])
                connectors_to_remove.append(conn)
                
                # Update other component's connection count
                other_id = conn['to_id'] if conn['from_id'] == item_id else conn['from_id']
                if other_id in self.placed_items:
                    self.placed_items[other_id]['current_connections'] -= 1
                    self.update_component_label(other_id)
        
        # Remove connections from list
        for conn in connectors_to_remove:
            self.connectors.remove(conn)
        
        # Delete label
        self.canvas.delete(item['label_id'])
        
        # Delete item
        self.canvas.delete(item_id)
        
        # Notify about component removal (only for pumps and components)
        if item['type'] in ["pump", "component"]:
            component_id = item.get('id', item['name'])
            
            # If we have a circuits controller, use it to sync all tabs
            if self.circuits_controller and hasattr(self.circuits_controller, '_on_component_placement'):
                self.circuits_controller._on_component_placement(component_id, placed=False)
            # Otherwise, just update local detail list
            elif self.detail_list:
                self.detail_list.mark_component_available(component_id)
        
        del self.placed_items[item_id]
    
    def highlight_item(self, item_id, highlight=True):
        """Highlight or unhighlight an item"""
        if highlight:
            # Create highlight rectangle
            bbox = self.canvas.bbox(item_id)
            if bbox:
                x1, y1, x2, y2 = bbox
                padding = 5
                self.highlight_rect = self.canvas.create_rectangle(
                    x1-padding, y1-padding, x2+padding, y2+padding,
                    outline="#FF0000",
                    width=2,
                    tags=("highlight",)
                )
                self.canvas.tag_lower(self.highlight_rect, item_id)
        else:
            # Remove highlight
            self.canvas.delete("highlight")
    
    def start_drag(self, item_id, x, y):
        """Start dragging a component"""
        self._drag_data["item"] = item_id
        self._drag_data["x"] = x
        self._drag_data["y"] = y
        item_x, item_y = self.placed_items[item_id]['coords']
        self._drag_data["offset_x"] = x - item_x
        self._drag_data["offset_y"] = y - item_y
        # self.canvas.config(cursor="grab")
    
    def perform_drag(self, x, y):
        """Perform drag operation with boundary constraints"""
        item_id = self._drag_data["item"]
        if not item_id or item_id not in self.placed_items:
            return
        
        # Calculate new position
        new_x = x - self._drag_data["offset_x"]
        new_y = y - self._drag_data["offset_y"]
        
        # Get canvas dimensions
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # Get component size for boundary calculation
        comp_type = self.placed_items[item_id]['type']
        comp_size = self.component_properties.get(comp_type, {}).get('size', (30, 30))
        half_width = comp_size[0] // 2
        half_height = comp_size[1] // 2
        
        # Constrain position within canvas boundaries
        min_x = half_width + 5  # 5px padding from edge
        max_x = canvas_width - half_width - 5
        min_y = half_height + 5
        max_y = canvas_height - half_height - 60  # Extra space for label
        
        # Apply constraints
        new_x = max(min_x, min(new_x, max_x))
        new_y = max(min_y, min(new_y, max_y))
        
        # Update position
        old_x, old_y = self.placed_items[item_id]['coords']
        dx = new_x - old_x
        dy = new_y - old_y
        
        # Only move if there's actual displacement
        if dx != 0 or dy != 0:
            # Move component
            self.canvas.move(item_id, dx, dy)
            
            # Move label
            label_id = self.placed_items[item_id]['label_id']
            self.canvas.move(label_id, dx, dy)
            
            # Update stored position
            self.placed_items[item_id]['coords'] = (new_x, new_y)
            
            # Update connections
            self.update_connections_for_item(item_id)
            
            # Keep reset button on top
            self.canvas.tag_raise("reset_button")
    
    def end_drag(self):
        """End drag operation"""
        self.reset_drag_state()
        self.canvas.config(cursor="arrow")
    
    def update_connections_for_item(self, item_id):
        """Update connection lines when component moves"""
        for conn in self.connectors:
            if conn['from_id'] == item_id or conn['to_id'] == item_id:
                # Get new coordinates
                from_coords = self.placed_items[conn['from_id']]['coords']
                to_coords = self.placed_items[conn['to_id']]['coords']
                
                # Update line
                self.canvas.coords(
                    conn['line_id'],
                    from_coords[0], from_coords[1],
                    to_coords[0], to_coords[1]
                )
    
    def reset_connection_state(self):
        """Reset connection state"""
        if self.first_connection_item_id:
            self.highlight_item(self.first_connection_item_id, False)
            self.first_connection_item_id = None
    
    def on_dialog_closed(self):
        """Handle when pipe configuration dialog is closed"""
        # Reset connection state and clear selections
        self.reset_connection_state()
        self.selected_component = None
        
        # Reset mode to move
        if self.mode_selector:
            self.mode_selector.set_mode("move")
    
    def reset_drag_state(self):
        """Reset drag state"""
        self._drag_data = {"x": 0, "y": 0, "item": None, "offset_x": 0, "offset_y": 0}
    
    def get_placed_components(self):
        """Get list of all placed component IDs (pumps and components only)"""
        placed = []
        for item_data in self.placed_items.values():
            if item_data['type'] in ["pump", "component"]:
                placed.append(item_data.get('id', item_data['name']))
        return placed
    
    def get_circuit_data(self):
        """Get circuit data for saving - use original names without suffixes"""
        components_data = []
        connections_data = []
        
        # FIXED: Save components with original names
        for item_id, data in self.placed_items.items():
            component_info = {
                'id': item_id,  # Canvas item ID (integer)
                'type': data['type'],
                'name': data['name'],  # ← Use original name (no suffixes)
                'position': list(data['coords']),
                'connections': data['current_connections']
            }
            components_data.append(component_info)
        
        # FIXED: Save connections with original names
        for conn in self.connectors:
            # Get original names from placed_items
            from_name = conn.get('from_name', '')
            to_name = conn.get('to_name', '')
            
            if conn['from_id'] in self.placed_items:
                from_name = self.placed_items[conn['from_id']]['name']  # Original name
            
            if conn['to_id'] in self.placed_items:
                to_name = self.placed_items[conn['to_id']]['name']  # Original name
            
            connection_info = {
                'from': conn['from_id'],
                'to': conn['to_id'], 
                'from_name': from_name,
                'to_name': to_name,
                'parameters': conn.get('parameters', {})
            }
            connections_data.append(connection_info)
        
        return {
            'components': components_data,
            'connections': connections_data
        }
    
    def update_appearance(self, mode=None):
        """Update appearance based on theme"""
        # Update canvas background
        # bg_color = "#1A1A1A" if ctk.get_appearance_mode() == "Dark" else "white"
        # self.canvas.configure(bg=bg_color)
        
        # # Update grid color
        # grid_color = "#333333" if ctk.get_appearance_mode() == "Dark" else "#E0E0E0"
        # for item in self.canvas.find_withtag("grid"):
        #     self.canvas.itemconfig(item, fill=grid_color)
        
        # # Update connection colors
        # conn_color = "#4A90E2" if ctk.get_appearance_mode() == "Dark" else "#243783"
        # for conn in self.connectors:
        #     self.canvas.itemconfig(conn['line_id'], fill=conn_color)
        
        # Update component icons if needed
        mode = ctk.get_appearance_mode().lower()
        for item_id, data in self.placed_items.items():
            comp_type = data['type']
            if comp_type in self.loaded_icons:
                icon = self.loaded_icons[comp_type].get(mode)
                if icon:
                    self.canvas.itemconfig(item_id, image=icon)
    
    def destroy(self):
        """Clean up when destroying"""
        AppearanceManager.unregister(self)
        super().destroy()