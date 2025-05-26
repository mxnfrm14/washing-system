import customtkinter as ctk
import tkinter as tk
import math
import tkinter.messagebox as messagebox

# Define component types
class ComponentType:
    PUMP = "Pump"
    PIPE_CONNECTOR = "Connector"  # Water divider
    NOZZLE = "Nozzle"

# Define interaction modes
class Mode:
    PLACE = "PLACE"
    CONNECT = "CONNECT"
    DRAG_MOVE = "DRAG_MOVE"
    DELETE = "DELETE"

class CircuitDesigner:
    def __init__(self, parent, controller):
        self.parent = parent  # This will be the tab frame
        self.controller = controller  # Page controller
        
        # --- Data ---
        self.item_types = [ComponentType.PUMP, ComponentType.PIPE_CONNECTOR, ComponentType.NOZZLE]
        
        # Define properties for each component type
        self.component_properties = {
            ComponentType.PUMP: {
                'max_connections': 1,  # Output only
                'direction': 'out',    # Pumps only output water
                'flow_rate': 100,      # Base flow rate
                'color': '#88D8FF'     # Light blue in CustomTkinter style
            },
            ComponentType.PIPE_CONNECTOR: {
                'max_connections': 5,  # 1 input, multiple outputs
                'direction': 'both',   # Can have inputs and outputs
                'flow_division': True, # Divides flow among outputs
                'color': '#88FFB8'     # Light green in CustomTkinter style
            },
            ComponentType.NOZZLE: {
                'max_connections': 1,  # Input only
                'direction': 'in',     # Nozzles only receive water
                'color': '#FF88B0'     # Light coral in CustomTkinter style
            }
        }
        
        # Update max_connections to use component properties
        self.max_connections = {
            component: props['max_connections'] for component, props in self.component_properties.items()
        }
        
        # Add connection directionality tracking
        # Format: [(line_id, from_id, to_id, flow_rate)]
        self.connectors = []
        
        # Add system state
        self.system_calculated = False  # Track if flow calculations are current

        self.selected_item_type = tk.StringVar(parent, value="")
        # Stores info: {canvas_id: {'type': type, 'coords': (cx, cy), 'id': canvas_id, 'size': size, 
        #                          'label_id': label_id, 'current_connections': 0, 'max_connections': max}}
        self.placed_items = {}
        # ID of the first item clicked in CONNECT mode
        self.first_connection_item_id = None 

        # --- Mode State ---
        self.current_mode = tk.StringVar(parent, value=Mode.DRAG_MOVE) # Default mode

        # --- Drag State ---
        self._drag_data = {"x": 0, "y": 0, "item": None, "offset_x": 0, "offset_y": 0}
        
        # Create the UI
        self.create_ui()
        
    def create_ui(self):
        """Create the UI components for the circuit designer"""
        # Create main container that fills the parent
        self.main_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True)
        
        # Split into left panel (controls) and right panel (canvas)
        self.main_frame.grid_columnconfigure(0, weight=1)  # Left control panel
        self.main_frame.grid_columnconfigure(1, weight=3)  # Canvas panel
        self.main_frame.grid_rowconfigure(0, weight=1)     # Main row
        
        # --- Left Frame (Controls) ---
        self.controls_frame = ctk.CTkScrollableFrame(self.main_frame)
        self.controls_frame.grid(row=0, column=0, sticky="nswe", padx=5, pady=5)
        self.controls_frame.grid_columnconfigure(0, weight=1)  # Allow controls to expand horizontally
        
        # Mode Selection Radio Buttons
        mode_frame = ctk.CTkFrame(self.controls_frame)
        mode_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        ctk.CTkLabel(mode_frame, text="Mode", 
                    font=self.controller.fonts.get("bold")).grid(row=0, column=0, 
                                                                sticky="w", padx=5, pady=5)
        
        modes = [
            ("Place Item", Mode.PLACE),
            ("Connect Items", Mode.CONNECT),
            ("Move/Drag", Mode.DRAG_MOVE),
            ("Delete Item", Mode.DELETE)
        ]
        
        for i, (text, mode_val) in enumerate(modes):
            rb = ctk.CTkRadioButton(mode_frame, text=text, variable=self.current_mode,
                                   value=mode_val, command=self.on_mode_change)
            rb.grid(row=i+1, column=0, sticky="w", padx=20, pady=2)
        
        # Item Selection Frame with CustomTkinter styling
        item_list_frame = ctk.CTkFrame(self.controls_frame)
        item_list_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=10)
        
        ctk.CTkLabel(item_list_frame, text="Component Type", 
                    font=self.controller.fonts.get("bold")).grid(row=0, column=0, 
                                                                sticky="w", padx=5, pady=5)
        
        # Use CTk radio buttons for component selection
        for i, item_type in enumerate(self.item_types):
            rb = ctk.CTkRadioButton(item_list_frame, text=item_type, variable=self.selected_item_type,
                                  value=item_type)
            rb.grid(row=i+1, column=0, sticky="w", padx=20, pady=5)
        
        # System Analysis buttons
        calc_frame = ctk.CTkFrame(self.controls_frame)
        calc_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=10)
        
        ctk.CTkLabel(calc_frame, text="System Analysis", 
                    font=self.controller.fonts.get("bold")).grid(row=0, column=0, 
                                                              sticky="w", padx=5, pady=5)
        
        self.calc_button = ctk.CTkButton(calc_frame, text="Calculate Flow Paths",
                                       command=self.calculate_flow_rates)
        self.calc_button.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        
        self.path_button = ctk.CTkButton(calc_frame, text="Show Flow Paths",
                                      command=self.show_path_details)
        self.path_button.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        
        # --- Right Frame (Canvas) ---
        self.canvas_frame = ctk.CTkFrame(self.main_frame)
        self.canvas_frame.grid(row=0, column=1, sticky="nswe", padx=5, pady=5)
        self.canvas_frame.grid_rowconfigure(0, weight=1)
        self.canvas_frame.grid_columnconfigure(0, weight=1)
        
        # Canvas needs to be a regular Tkinter Canvas for drawing operations
        self.canvas = ctk.CTkCanvas(self.canvas_frame, bg="white", cursor="arrow")
        self.canvas.grid(row=0, column=0, sticky="nswe")
        
        # --- Canvas Event Bindings ---
        self.canvas.bind("<Button-1>", self.on_canvas_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.canvas.bind("<B1-Motion>", self.on_canvas_motion)
        
        # Initialize UI state based on default mode
        self.on_mode_change()
    
    # --- Mode and Selection Changes ---
    def on_mode_change(self):
        """Called when the mode radio button changes."""
        mode = self.current_mode.get()
        print(f"Mode changed to: {mode}")
        
        # Reset potentially conflicting states when changing mode
        self.reset_connection_state()
        self.reset_drag_state()
        
        # Update UI elements based on mode
        if mode == Mode.PLACE:
            self.canvas.config(cursor="crosshair")  # Indicate placement
        elif mode == Mode.DELETE:
            self.canvas.config(cursor="X_cursor")  # Indicate deletion
        elif mode == Mode.CONNECT:
            self.canvas.config(cursor="hand2")  # Indicate connection possibility
        else:  # DRAG_MOVE or others
            self.canvas.config(cursor="arrow")  # Default arrow or grab cursor
    
    # --- Canvas Interaction (Unified Handlers) ---
    def on_canvas_press(self, event):
        """Handles the initial press of the left mouse button on the canvas."""
        mode = self.current_mode.get()
        x, y = event.x, event.y
        target_item_id = self.find_item_at(x, y)
        
        if target_item_id:
            # --- Clicked on an existing item ---
            if mode == Mode.DRAG_MOVE:
                self.start_drag(target_item_id, x, y)
            elif mode == Mode.CONNECT:
                self.handle_connection_click(target_item_id)
            elif mode == Mode.DELETE:
                self.delete_item_and_connectors(target_item_id)
            elif mode == Mode.PLACE:
                # Clicking an item in place mode does nothing for now
                print("Clicked item while in Place mode.")
                pass
        else:
            # --- Clicked on the background ---
            if mode == Mode.PLACE:
                item_to_place = self.selected_item_type.get()
                if item_to_place:
                    self.place_item(x, y, item_to_place)
                else:
                    print("Place mode: Clicked background, but no item type selected.")
            else:
                # Clicking background in other modes usually cancels pending actions
                print(f"Clicked background in {mode} mode.")
                self.reset_connection_state()  # Cancel connection attempt
    
    def on_canvas_motion(self, event):
        """Handles mouse movement while the left button is pressed."""
        # Only relevant if currently dragging
        if self.current_mode.get() == Mode.DRAG_MOVE and self._drag_data["item"] is not None:
            self.perform_drag(event.x, event.y)
    
    def on_canvas_release(self, event):
        """Handles the release of the left mouse button."""
        # Only relevant if currently dragging
        if self.current_mode.get() == Mode.DRAG_MOVE and self._drag_data["item"] is not None:
            self.end_drag(event.x, event.y)
    
    # --- Action Functions ---
    def handle_connection_click(self, clicked_item_id):
        """Manages the logic for connecting items when an item is clicked in CONNECT mode."""
        print(f"Connect mode: Clicked on item {clicked_item_id}")
        if self.first_connection_item_id is None:
            # Start connection
            self.first_connection_item_id = clicked_item_id
            self.canvas.itemconfig(clicked_item_id, outline='red', width=2)  # Visual feedback
            print(f"Starting connection from item: {clicked_item_id}")
        elif self.first_connection_item_id != clicked_item_id:
            # Complete connection
            print(f"Connecting item {self.first_connection_item_id} to item {clicked_item_id}")
            self.create_connector(self.first_connection_item_id, clicked_item_id)
            self.reset_connection_state()  # Resets visual feedback and ID
        else:  # Clicked the same item again
            print("Connection cancelled (Clicked same item).")
            self.reset_connection_state()
    
    def start_drag(self, item_id, x, y):
        """Initiates the dragging process for an item."""
        if item_id in self.placed_items:
            print(f"Starting drag for item {item_id}")
            self._drag_data["item"] = item_id
            self._drag_data["x"] = x
            self._drag_data["y"] = y
            item_center_x, item_center_y = self.placed_items[item_id]['coords']
            self._drag_data["offset_x"] = x - item_center_x
            self._drag_data["offset_y"] = y - item_center_y
            self.canvas.tag_raise(item_id)  # Bring item to top while dragging
            self.canvas.config(cursor="grabbing")  # Change cursor during drag
    
    def perform_drag(self, x, y):
        """Updates item position during drag."""
        item_id = self._drag_data["item"]
        if not item_id or item_id not in self.placed_items:
            self.reset_drag_state()
            return
        
        new_center_x = x - self._drag_data["offset_x"]
        new_center_y = y - self._drag_data["offset_y"]
        
        old_center_x, old_center_y = self.placed_items[item_id]['coords']
        delta_x = new_center_x - old_center_x
        delta_y = new_center_y - old_center_y
        
        # Check if canvas exists before moving
        if not self.canvas.winfo_exists():
            self.reset_drag_state()
            return
        
        try:
            # Move the item
            self.canvas.move(item_id, delta_x, delta_y)
            self.placed_items[item_id]['coords'] = (new_center_x, new_center_y)
            
            # Move the label too
            label_id = self.placed_items[item_id].get('label_id')
            if label_id:
                self.canvas.move(label_id, delta_x, delta_y)
            
            self.update_connectors_for_item(item_id)
        except Exception as e:
            print(f"Error moving item {item_id} during drag: {e}")
            self.reset_drag_state()
    
    def end_drag(self, x, y):
        """Finalizes the drag operation."""
        item_id = self._drag_data["item"]
        print(f"Finished dragging item {item_id}")
        if item_id and item_id in self.placed_items:
            # Recalculate final position based on current mouse pos and offset
            final_x = x - self._drag_data["offset_x"]
            final_y = y - self._drag_data["offset_y"]
            self.placed_items[item_id]['coords'] = (final_x, final_y)
            # Final connector update might be needed if motion events skipped
            self.update_connectors_for_item(item_id)
        
        self.reset_drag_state()
        # Reset cursor based on current mode after drag finishes
        self.on_mode_change()
    
    def delete_item_and_connectors(self, item_id):
        """Deletes an item and any connectors attached to it."""
        if item_id not in self.placed_items:
            print(f"Item {item_id} not found for deletion.")
            return
        
        print(f"Deleting item {item_id} ({self.placed_items[item_id]['type']}) in Delete mode.")
        
        # Get the label id before deleting
        label_id = self.placed_items[item_id].get('label_id')
        
        # Keep track of items that need connection count updates
        connected_items = set()
        
        # Use a list comprehension to find connectors to remove, avoiding modification during iteration issues
        connectors_to_remove_indices = [
            i for i, (line_id, id1, id2) in enumerate(self.connectors)
            if id1 == item_id or id2 == item_id
        ]
        
        # Iterate backwards through indices to remove them safely
        for index in sorted(connectors_to_remove_indices, reverse=True):
            line_id, id1, id2 = self.connectors[index]
            
            # Add the other connected item to our update set
            if id1 == item_id and id2 in self.placed_items:
                connected_items.add(id2)
            elif id2 == item_id and id1 in self.placed_items:
                connected_items.add(id1)
            
            print(f"Deleting connector: {line_id}")
            try:
                if self.canvas.winfo_exists():
                    self.canvas.delete(line_id)
            except Exception as e:
                print(f"Warning: Error deleting connector {line_id}: {e}")
            del self.connectors[index]  # Remove from the list
        
        # Update connection counts for connected items
        for connected_id in connected_items:
            if connected_id in self.placed_items:
                self.placed_items[connected_id]['current_connections'] -= 1
                self.update_connection_label(connected_id)
        
        # If the item being deleted was the start of a connection, reset state
        if self.first_connection_item_id == item_id:
            self.first_connection_item_id = None
            print("Resetting connection state because selected item was deleted.")
        
        # Delete the item shape itself
        try:
            if self.canvas.winfo_exists():
                self.canvas.delete(item_id)
                # Also delete the label
                if label_id:
                    self.canvas.delete(label_id)
        except Exception as e:
            print(f"Warning: Error deleting item {item_id}: {e}")
        
        # Remove item data from our dictionary
        del self.placed_items[item_id]
        print(f"Item {item_id} deleted.")
    
    # --- Item Placement and Connectors ---
    def find_item_at(self, x, y):
        """Finds the canvas ID of a placeable item at coordinates (x, y)."""
        search_radius = 3
        overlapping = self.canvas.find_overlapping(x - search_radius, y - search_radius, 
                                                x + search_radius, y + search_radius)
        for item_id in reversed(overlapping):
            if item_id in self.placed_items:
                return item_id
        return None
    
    def place_item(self, x, y, item_type):
        """Places a water system component on the canvas."""
        size = 20
        item_id = None
        properties = self.component_properties.get(item_type, {})
        color = properties.get('color', 'gray')
        tags = ("item", item_type)
        
        try:
            if item_type == ComponentType.PUMP:
                # Create pump (rectangle with "P")
                item_id = self.canvas.create_rectangle(
                    x - size, y - size, x + size, y + size,
                    fill=color, outline="black", tags=tags
                )
                # Add letter P to identify it as a pump
                self.canvas.create_text(x, y, text="P", tags=tags)
            
            elif item_type == ComponentType.PIPE_CONNECTOR:
                # Create connector (circle with multiple connection points)
                item_id = self.canvas.create_oval(
                    x - size, y - size, x + size, y + size,
                    fill=color, outline="black", tags=tags
                )
                # Add "+" symbol to indicate it connects multiple pipes
                self.canvas.create_text(x, y, text="+", tags=tags)
            
            elif item_type == ComponentType.NOZZLE:
                # Create nozzle (triangle pointing outward)
                p1 = (x, y - size)
                p2 = (x - size, y + size * 0.8)
                p3 = (x + size, y + size * 0.8)
                item_id = self.canvas.create_polygon(
                    p1, p2, p3,
                    fill=color, outline="black", tags=tags
                )
                # Add spray line in front of nozzle
                spray_lines = []
                for i in range(3):
                    offset = (i - 1) * 5
                    spray_lines.append(x + offset)
                    spray_lines.append(y - size)
                    spray_lines.append(x + offset)
                    spray_lines.append(y - size * 1.5)
                self.canvas.create_line(*spray_lines, tags=tags)
            
            # Store component-specific properties
            if item_id:
                max_conn = properties.get('max_connections', 0)
                direction = properties.get('direction', 'both')
                
                # Create label text
                label_text = f"{item_type}: 0/{max_conn}"
                label_y = y + size + 10
                
                # Create the label
                label_id = self.canvas.create_text(
                    x, label_y, text=label_text,
                    fill="black", font=("Arial", 8), tags=("label",)
                )
                
                # Store item data with properties
                self.placed_items[item_id] = {
                    'type': item_type,
                    'coords': (x, y),
                    'id': item_id,
                    'size': size,
                    'label_id': label_id,
                    'current_connections': 0,
                    'max_connections': max_conn,
                    'direction': direction
                }
                
                # Mark system as needing recalculation
                self.system_calculated = False
        
        except Exception as e:
            print(f"Error creating component: {e}")
    
    def create_connector(self, item1_id, item2_id):
        """Creates a directional connection between items based on their types."""
        if item1_id not in self.placed_items or item2_id not in self.placed_items:
            print("Error: One or both items don't exist")
            return
        
        item1 = self.placed_items[item1_id]
        item2 = self.placed_items[item2_id]
        
        # Determine direction based on component types
        item1_type = item1['type']
        item2_type = item2['type']
        item1_props = self.component_properties[item1_type]
        item2_props = self.component_properties[item2_type]
        
        # First, check existing connections
        for _, from_id, to_id in self.connectors:
            if (from_id == item1_id and to_id == item2_id) or (from_id == item2_id and to_id == item1_id):
                print("Connection already exists.")
                return
        
        # Determine direction of flow
        if item1_props['direction'] == 'out' and item2_props['direction'] in ['both', 'in']:
            # Flow from item1 to item2
            from_item, to_item = item1, item2
            from_id, to_id = item1_id, item2_id
        elif item2_props['direction'] == 'out' and item1_props['direction'] in ['both', 'in']:
            # Flow from item2 to item1
            from_item, to_item = item2, item1
            from_id, to_id = item2_id, item1_id
        elif item1_props['direction'] == 'both' and item2_props['direction'] == 'in':
            # Flow from item1 to item2
            from_item, to_item = item1, item2
            from_id, to_id = item1_id, item2_id
        elif item2_props['direction'] == 'both' and item1_props['direction'] == 'in':
            # Flow from item2 to item1
            from_item, to_item = item2, item1
            from_id, to_id = item2_id, item1_id
        else:
            print(f"Cannot determine flow direction between {item1_type} and {item2_type}")
            return
        
        # Check connection limits
        if from_item['current_connections'] >= from_item['max_connections']:
            print(f"Cannot connect: {from_item['type']} has reached maximum connections")
            return
        
        if to_item['current_connections'] >= to_item['max_connections']:
            print(f"Cannot connect: {to_item['type']} has reached maximum connections")
            return
        
        # Create the visual connector with an arrow to show direction
        try:
            # Get coordinates
            coords1 = from_item['coords']
            coords2 = to_item['coords']
            
            # Create arrow line
            line_id = self.canvas.create_line(
                coords1[0], coords1[1],
                coords2[0], coords2[1],
                fill="blue", width=2,
                arrow="last",  # Add arrow pointing to destination
                tags="connector"
            )
            
            # Store connection with direction
            self.connectors.append((line_id, from_id, to_id))
            
            # Update connection counts
            from_item['current_connections'] += 1
            to_item['current_connections'] += 1
            self.update_connection_label(from_id)
            self.update_connection_label(to_id)
            
            print(f"Directional connector created: {line_id} from {from_id} to {to_id}")
            
            # Mark system as needing recalculation
            self.system_calculated = False
        
        except Exception as e:
            print(f"Error creating connector: {e}")
    
    def update_connection_label(self, item_id):
        """Updates the label text with current connection count."""
        if item_id in self.placed_items:
            item = self.placed_items[item_id]
            label_id = item.get('label_id')
            
            if label_id and self.canvas.winfo_exists():
                try:
                    label_text = f"{item['type']}: {item['current_connections']}/{item['max_connections']}"
                    self.canvas.itemconfig(label_id, text=label_text)
                except Exception as e:
                    print(f"Error updating label for item {item_id}: {e}")
    
    def update_connectors_for_item(self, item_id):
        """Updates the endpoints of all connectors attached to the given item_id."""
        if item_id not in self.placed_items:
            return
        
        # Ensure canvas exists
        if not self.canvas.winfo_exists():
            return
        
        new_coords = self.placed_items[item_id]['coords']
        
        for line_id, id1, id2 in self.connectors:
            try:
                # Check if line still exists before trying to modify it
                line_coords = self.canvas.coords(line_id)
                if not line_coords or len(line_coords) < 4:
                    continue  # Skip if coords invalid/deleted
                
                current_line_coords = list(line_coords)
                
                if id1 == item_id:
                    current_line_coords[0] = new_coords[0]
                    current_line_coords[1] = new_coords[1]
                    self.canvas.coords(line_id, *current_line_coords)
                elif id2 == item_id:
                    current_line_coords[2] = new_coords[0]
                    current_line_coords[3] = new_coords[1]
                    self.canvas.coords(line_id, *current_line_coords)
            except Exception as e:
                print(f"Warning: Error updating connector {line_id}: {e}")
    
    # --- State Management ---
    def reset_connection_state(self):
        """Resets any ongoing connection attempt."""
        if self.first_connection_item_id:
            first_id = self.first_connection_item_id
            self.first_connection_item_id = None
            print(f"Resetting connection state (was pending for {first_id}).")
            try:
                # Check if item still exists and canvas is available
                if (self.canvas.winfo_exists() and first_id in self.placed_items and
                        first_id in self.canvas.find_all()):
                    self.canvas.itemconfig(first_id, outline='black', width=1)  # Reset visual feedback
            except Exception as e:
                print(f"Warning: Error resetting visual state for item {first_id}: {e}")
    
    def reset_drag_state(self):
        """Resets the drag operation state."""
        if self._drag_data["item"]:  # Only print if a drag was actually in progress
            print(f"Resetting drag state for item {self._drag_data['item']}.")
        self._drag_data["item"] = None
        self._drag_data["x"] = 0
        self._drag_data["y"] = 0
        self._drag_data["offset_x"] = 0
        self._drag_data["offset_y"] = 0
    
    # --- Flow Analysis Functions ---
    def trace_water_paths(self):
        """Traces all water paths from pumps to nozzles."""
        # Find all pumps (sources)
        pumps = [item_id for item_id, data in self.placed_items.items()
                if data['type'] == ComponentType.PUMP]
        
        if not pumps:
            print("No pumps found in the system!")
            return []
        
        all_paths = []
        
        # For each pump, trace all possible paths
        for pump_id in pumps:
            paths = self._trace_from_source(pump_id, [], set())
            all_paths.extend(paths)
        
        # Update system state
        self.system_calculated = True
        
        return all_paths
    
    def _trace_from_source(self, current_id, current_path, visited):
        """
        Recursively trace paths from a source node
        Returns list of complete paths (arrays of component IDs)
        """
        # Add current node to path and visited set
        current_path = current_path + [current_id]
        visited = visited.union({current_id})
        
        # Get component type
        current_type = self.placed_items[current_id]['type']
        
        # If we've reached a nozzle (endpoint), return this path
        if current_type == ComponentType.NOZZLE:
            return [current_path]
        
        # Find all outgoing connections
        outgoing = [to_id for _, from_id, to_id in self.connectors 
                    if from_id == current_id and to_id not in visited]
        
        # No more connections - dead end (not ending at nozzle)
        if not outgoing:
            return []
        
        # Continue path for each outgoing connection
        paths = []
        for next_id in outgoing:
            next_paths = self._trace_from_source(next_id, current_path, visited)
            paths.extend(next_paths)
        
        return paths
    
    def calculate_flow_rates(self):
        """Calculate water flow rates through the system based on component properties."""
        # Get all water paths
        all_paths = self.trace_water_paths()
        
        if not all_paths:
            print("No complete water paths found")
            messagebox.showinfo("No Paths", "No complete water paths found in the system.\n"
                               "Make sure you have at least one pump connected to a nozzle.")
            return
        
        # Reset flow rates
        for item_id in self.placed_items:
            self.placed_items[item_id]['flow_rate'] = 0
        
        # For each path, calculate and update flow
        for path in all_paths:
            self._calculate_path_flow(path)
        
        # Update labels to show flow rates
        for item_id, data in self.placed_items.items():
            if 'flow_rate' in data:
                self._update_flow_label(item_id)
        
        print(f"Calculated flow rates for {len(all_paths)} complete paths")
    
    def _calculate_path_flow(self, path):
        """Calculate flow through a single path."""
        if not path:
            return
        
        # Start with pump flow rate
        pump_id = path[0]
        if self.placed_items[pump_id]['type'] != ComponentType.PUMP:
            print(f"Error: Path doesn't start with pump: {path}")
            return
        
        # Get base flow rate from pump
        base_flow = self.component_properties[ComponentType.PUMP]['flow_rate']
        
        # For each connector in the path, adjust flow based on its properties
        for i in range(len(path)-1):
            current_id = path[i]
            next_id = path[i+1]
            
            current_type = self.placed_items[current_id]['type']
            
            # If it's a connector that divides flow
            if current_type == ComponentType.PIPE_CONNECTOR:
                # Count outgoing connections
                outgoing = sum(1 for _, from_id, _ in self.connectors if from_id == current_id)
                if outgoing > 0:
                    # Divide flow among all outputs
                    base_flow = base_flow / outgoing
        
        # Update flow rate for each component in the path
        for item_id in path:
            self.placed_items[item_id]['flow_rate'] = \
                self.placed_items[item_id].get('flow_rate', 0) + base_flow
    
    def _update_flow_label(self, item_id):
        """Update the label to show flow rate."""
        if item_id not in self.placed_items:
            return
        
        item = self.placed_items[item_id]
        label_id = item.get('label_id')
        
        if not label_id or not self.canvas.winfo_exists():
            return
        
        try:
            flow_rate = item.get('flow_rate', 0)
            item_type = item['type']
            max_conn = item['max_connections']
            curr_conn = item['current_connections']
            
            label_text = f"{item_type}: {curr_conn}/{max_conn}\nFlow: {flow_rate:.1f}"
            self.canvas.itemconfig(label_id, text=label_text)
        except Exception as e:
            print(f"Error updating flow label: {e}")
    
    def _calculate_path_length(self, path):
        """Calculate the total length of a path in coordinate units"""
        if not path or len(path) < 2:
            return 0
        
        total_length = 0
        for i in range(len(path) - 1):
            current_id = path[i]
            next_id = path[i + 1]
            
            # Get coordinates
            current_x, current_y = self.placed_items[current_id]['coords']
            next_x, next_y = self.placed_items[next_id]['coords']
            
            # Calculate Euclidean distance
            segment_length = math.sqrt((next_x - current_x)**2 + (next_y - current_y)**2)
            total_length += segment_length
        
        return total_length
    
    def show_path_details(self):
        """Creates a new window showing detailed information about all water paths"""
        # Get all paths before creating the window
        all_paths = self.trace_water_paths()
        
        if not all_paths:
            messagebox.showinfo("No Paths", "No complete water paths found in the system.\n"
                               "Make sure you have at least one pump connected to a nozzle.")
            return
        
        # Create a new top-level window
        path_window = ctk.CTkToplevel()
        path_window.title("Water System Pathways")
        path_window.geometry("600x400")
        path_window.grab_set()  # Make it modal
        
        # Create a frame with scrollbars
        main_frame = ctk.CTkFrame(path_window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Add a scrollable text widget - using regular Tkinter text widget for full compatibility
        path_text = tk.Text(main_frame, wrap="word", padx=5, pady=5)
        scrollbar = tk.Scrollbar(main_frame, command=path_text.yview)
        path_text.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        path_text.pack(side="left", fill="both", expand=True)
        
        # Add a header
        path_text.insert("end", f"WATER SYSTEM ANALYSIS\n")
        path_text.insert("end", f"{'='*50}\n\n")
        path_text.insert("end", f"Found {len(all_paths)} complete flow path(s) from pump(s) to nozzle(s).\n\n")
        
        # Add controls to highlight paths
        control_frame = ctk.CTkFrame(path_window)
        control_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(control_frame, text="Highlight path: ").pack(side="left", padx=5)
        path_var = tk.StringVar(path_window)
        paths = [f"Path #{i+1}" for i in range(len(all_paths))]
        paths.insert(0, "None")
        path_var.set("None")
        
        def on_path_select(*args):
            selected = path_var.get()
            if selected == "None":
                self.highlight_path(None)
            else:
                # Extract path number and convert to 0-based index
                index = int(selected.split('#')[1]) - 1
                self.highlight_path(index)
        
        path_dropdown = ctk.CTkOptionMenu(control_frame, variable=path_var, values=paths,
                                         command=on_path_select)
        path_dropdown.pack(side="left", padx=5)
        
        # Add a separator
        separator = tk.Separator(path_window, orient="horizontal")
        separator.pack(fill="x", padx=10, pady=5)
        
        # Format and display each path
        for i, path in enumerate(all_paths):
            # Add path header
            path_text.insert("end", f"Path #{i+1}:\n")
            path_text.insert("end", f"{'-'*50}\n")
            
            # Display each component in the path with flow information
            for j, comp_id in enumerate(path):
                comp = self.placed_items[comp_id]
                comp_type = comp['type']
                flow_rate = comp.get('flow_rate', 0)
                coords = comp['coords']
                
                # Format based on component type
                if j == 0:
                    path_text.insert("end", f"START → {comp_type} (ID: {comp_id}) at ({int(coords[0])}, {int(coords[1])}) - Flow: {flow_rate:.1f}\n")
                elif j == len(path) - 1:
                    path_text.insert("end", f"    → {comp_type} (ID: {comp_id}) at ({int(coords[0])}, {int(coords[1])}) - Flow: {flow_rate:.1f} → END\n")
                else:
                    path_text.insert("end", f"    → {comp_type} (ID: {comp_id}) at ({int(coords[0])}, {int(coords[1])}) - Flow: {flow_rate:.1f}\n")
            
            # Calculate total path length
            path_length = self._calculate_path_length(path)
            path_text.insert("end", f"\nTotal path length: {path_length:.1f} units\n\n")
        
        # Make text widget read-only
        path_text.configure(state="disabled")
    
    def highlight_path(self, path_index=None):
        """Highlights a specific flow path or resets highlighting if None"""
        # Delete any previous path highlights
        for item in self.canvas.find_withtag("path_highlight"):
            self.canvas.delete(item)
        
        if path_index is None:
            return  # Just clear highlights
        
        # Get all paths
        all_paths = self.trace_water_paths()
        if not all_paths or path_index >= len(all_paths):
            return
        
        # Get selected path
        path = all_paths[path_index]
        
        # Create highlight lines (slightly offset from original connections)
        for i in range(len(path) - 1):
            current_id = path[i]
            next_id = path[i + 1]
            
            # Get component coordinates
            current_x, current_y = self.placed_items[current_id]['coords']
            next_x, next_y = self.placed_items[next_id]['coords']
            
            # Draw highlight line (with slight offset)
            highlight_id = self.canvas.create_line(
                current_x, current_y, next_x, next_y,
                fill="orange", width=4, dash=(5, 2),
                tags="path_highlight"
            )
            
            # Make sure it's below components but above regular connectors
            self.canvas.tag_lower(highlight_id, "item")
            
            # Add a sequential number at midpoint
            mid_x = (current_x + next_x) / 2
            mid_y = (current_y + next_y) / 2
            self.canvas.create_text(
                mid_x, mid_y, text=str(i+1),
                fill="black", font=("Arial", 10, "bold"),
                tags="path_highlight"
            )