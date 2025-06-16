import customtkinter as ctk
from components.custom_button import CustomButton
from components.tabview import ThemedTabview
import tkinter as tk
import tkinter.messagebox as messagebox
from components.circuit_designer import CircuitDesigner
from components.detail_list import DetailList
from components.mode_selector import ModeSelector
import uuid

class Circuits(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        ctk.set_default_color_theme("theme.json")
        
        # Track configuration hash to detect changes
        self.last_config_hash = None
        self.saved_circuit_states = {}  # Store circuit data for each pump
        
        # Get configuration from controller (from previous pages)
        self.config = self._get_config_from_controller()

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
            text="Configuration of circuits diagrams", 
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

        # Divider
        self.divider = ctk.CTkFrame(self.main_container, height=2, corner_radius=0, fg_color="#F8F8F8")
        self.divider.pack(pady=(0, 10), fill="x")

        # =========================== Navigation Buttons ==========================
        # Bottom frame for navigation buttons
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
            command=lambda: controller.show_page("sequence")
        )
        self.next_button.pack(side="right")

        # Back button
        self.back_button = CustomButton(
            self.bottom_frame,
            text="Back",
            font=controller.fonts.get("default", None),
            icon_path="assets/icons/back.png",
            icon_side="left",
            outlined=True,
            command=lambda: controller.show_page("pumps")
        )
        self.back_button.pack(side="left")

        # ========================== Content Area ==========================
        # Content frame for the main content
        self.content_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=50, pady=0)

        # Initialize UI components
        self._create_circuit_content()
    
    def _get_config_hash(self, config):
        """Generate a hash of the configuration to detect changes"""
        import hashlib
        import json
        
        # Create a simplified version for hashing
        config_for_hash = {
            'pumps': [
                {
                    'name': pump.get('name', ''),
                    'outputs': pump.get('outputs', 0)
                } for pump in config.get('pumps', [])
            ],
            'washing_components': [
                comp.get('name', '') if isinstance(comp, dict) else str(comp)
                for comp in config.get('washing_components', [])
            ]
        }
        
        config_str = json.dumps(config_for_hash, sort_keys=True)
        return hashlib.md5(config_str.encode()).hexdigest()
    
    def _save_circuit_states(self):
        """Save current circuit states before refreshing"""
        if hasattr(self, 'circuit_designers') and self.circuit_designers:
            for i, designer in enumerate(self.circuit_designers):
                if designer and hasattr(designer, 'get_circuit_data'):
                    self.saved_circuit_states[i] = designer.get_circuit_data()
    
    def _restore_circuit_states(self):
        """Restore circuit states after refreshing"""
        if hasattr(self, 'circuit_designers') and self.circuit_designers:
            for i, designer in enumerate(self.circuit_designers):
                if i in self.saved_circuit_states and designer:
                    try:
                        self._restore_circuit_to_designer(designer, self.saved_circuit_states[i])
                    except Exception as e:
                        print(f"Error restoring circuit state for pump {i}: {e}")
    
    def _restore_circuit_to_designer(self, designer, circuit_data):
        """Restore a specific circuit to a designer"""
        if not circuit_data or not designer:
            return
        
        # Restore components
        components = circuit_data.get('components', [])
        for comp_data in components:
            try:
                # Recreate the component data structure
                component = {
                    'name': comp_data['name'],
                    'type': comp_data['type'],
                    'max_connections': comp_data.get('connections', 0)
                }
                
                # If it's a connector, add subtype
                if comp_data['type'] in ['t_connector', 'y_connector', 'straight_connector']:
                    component['subtype'] = comp_data['type']
                    component['type'] = 'connector'
                
                # Place the component
                x, y = comp_data['position']
                designer.place_component(x, y, component)
                
            except Exception as e:
                print(f"Error restoring component {comp_data.get('name', 'Unknown')}: {e}")
        
        # Restore connections after all components are placed
        connections = circuit_data.get('connections', [])
        for conn_data in connections:
            try:
                # Find the placed items by matching names and positions
                from_item_id = None
                to_item_id = None
                
                for item_id, item_data in designer.placed_items.items():
                    if item_data['name'] == conn_data['from_name']:
                        from_item_id = item_id
                    elif item_data['name'] == conn_data['to_name']:
                        to_item_id = item_id
                
                if from_item_id and to_item_id:
                    designer.create_connection(from_item_id, to_item_id, conn_data.get('parameters', {}))
                
            except Exception as e:
                print(f"Error restoring connection: {e}")
    
    def _analyze_circuit_connections(self, circuit_data):
        """Analyze circuit connections to determine component hierarchy"""
        if not circuit_data or 'components' not in circuit_data or 'connections' not in circuit_data:
            return {}
        
        components = {comp['name']: comp for comp in circuit_data['components']}
        connections = circuit_data['connections']
        
        # Build connection graph
        connection_graph = {}
        for conn in connections:
            from_name = conn['from_name']
            to_name = conn['to_name']
            
            if from_name not in connection_graph:
                connection_graph[from_name] = []
            connection_graph[from_name].append(to_name)
        
        return connection_graph
    
    def _find_pump_outputs(self, components):
        """Find pump components and their outputs"""
        pump_outputs = {}
        for comp_name, comp_data in components.items():
            if comp_data.get('type') == 'pump':
                outputs = comp_data.get('max_connections', 1)
                pump_outputs[comp_name] = list(range(1, outputs + 1))
        return pump_outputs
    
    def _trace_path_from_output(self, start_component, connection_graph, components, visited=None):
        """Trace the path from a pump output to find all connected components"""
        if visited is None:
            visited = set()
        
        if start_component in visited:
            return []
        
        visited.add(start_component)
        path = []
        
        # Add current component if it's not a pump
        if start_component in components:
            comp_type = components[start_component].get('type', '')
            if comp_type != 'pump':
                path.append({
                    'name': start_component,
                    'type': comp_type,
                    'distance': len(visited) - 1
                })
        
        # Follow connections
        if start_component in connection_graph:
            for connected_component in connection_graph[start_component]:
                child_path = self._trace_path_from_output(connected_component, connection_graph, components, visited.copy())
                for item in child_path:
                    item['distance'] += 1
                path.extend(child_path)
        
        return path
    
    def _get_pump_outputs_ids(self, pump_comp, circuit_data, pump_config):
        """
        Return a list of (output_index, to_id) for each output connection from the pump,
        ordered left-to-right by the x position of the 'to' component.
        """
        pump_id = pump_comp.get('id')
        # Get all direct connections from the pump
        direct_conns = [conn for conn in circuit_data.get('connections', []) if conn['from'] == pump_id]
        # Sort connections left-to-right by the x position of the 'to' component if possible
        components_by_id = {comp['id']: comp for comp in circuit_data['components']}
        def get_x(conn):
            comp = components_by_id.get(conn['to'])
            if comp and isinstance(comp.get('position'), (list, tuple)) and len(comp['position']) > 0:
                return comp['position'][0]
            return 0
        direct_conns_sorted = sorted(direct_conns, key=get_x)
        # Each connection is a separate output, index starting from 1
        output_map = []
        for idx, conn in enumerate(direct_conns_sorted, 1):
            output_map.append((idx, [conn['to']]))
        return output_map

    def _follow_output_path(self, start_id, circuit_data, components_by_id, visited=None):
        """
        Recursively follow the path from a given id, collecting all reachable 'component' type names.
        Always explore further through connectors.
        """
        if visited is None:
            visited = set()
        result = []
        if start_id in visited:
            return result
        visited.add(start_id)
        comp = components_by_id.get(start_id)
        if comp:
            if comp.get('type') == 'component':
                result.append(comp['name'])
            # Always continue through connectors and any other node
            for conn in circuit_data.get('connections', []):
                if conn['from'] == start_id:
                    result += self._follow_output_path(conn['to'], circuit_data, components_by_id, visited)
        return result

    def _generate_circuit_summary(self, circuit_data, pump_config):
        """Generate a summary of components connected to each pump output using IDs for tracking."""
        if not circuit_data or 'components' not in circuit_data:
            return {}
        
        components_by_id = {comp['id']: comp for comp in circuit_data['components']}
        
        # Find the pump component
        pump_comp = None
        for comp in circuit_data['components']:
            if comp.get('type') == 'pump':
                pump_comp = comp
                break
        if not pump_comp:
            return {}
        
        # Create a mapping of used component IDs to avoid duplicates
        used_component_ids = set()
        
        # For each output, follow its path and collect component IDs and names
        output_map = {}
        outputs = self._get_pump_outputs_ids(pump_comp, circuit_data, pump_config)
        for idx, to_ids in outputs:
            comp_list = []
            comp_ids_seen = set()  # Track circuit IDs to avoid duplicates
            for to_id in to_ids:
                path_components = self._follow_output_path_with_ids(to_id, circuit_data, components_by_id, visited=set())
                for comp_info in path_components:
                    comp_id = comp_info['id']
                    # Only add if we haven't seen this specific circuit component ID
                    if comp_id not in comp_ids_seen:
                        comp_ids_seen.add(comp_id)
                        # Find the actual component ID from the washing components configuration
                        actual_component_id = self._get_actual_component_id(comp_info['name'], used_component_ids)
                        comp_info['actual_id'] = actual_component_id
                        if actual_component_id:
                            used_component_ids.add(actual_component_id)
                        comp_list.append(comp_info)
            
            output_map[str(idx)] = comp_list
        return output_map

    def _get_actual_component_id(self, component_name, used_ids):
        """Get the actual component ID from the washing components configuration, avoiding already used IDs"""
        washing_components = self.config.get('washing_components', [])
        
        # First, try to find an unused component with the matching name
        for component in washing_components:
            if (component.get('name') == component_name and 
                component.get('id') not in used_ids):
                return component.get('id')
        
        # If all components with this name are used, return the first match with a warning
        for component in washing_components:
            if component.get('name') == component_name:
                print(f"Warning: Component '{component_name}' (ID: {component.get('id')}) is being reused in circuit")
                return component.get('id')
        
        print(f"Warning: No configuration found for component '{component_name}'")
        return None


    def _create_circuit_content(self):
        """Create or recreate the circuit content based on current configuration"""
        # Check if we need to refresh based on configuration changes
        current_hash = self._get_config_hash(self.config)
        should_clear_circuits = (self.last_config_hash is None or 
                               self.last_config_hash != current_hash)
        
        # Save current circuit states if we're not clearing them
        if not should_clear_circuits:
            self._save_circuit_states()
        else:
            # Clear saved states if configuration changed
            self.saved_circuit_states = {}
        
        # Update the hash
        self.last_config_hash = current_hash
        
        # Clear existing content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Reset instance variables
        self.tabs = []
        self.circuit_designers = []
        self.detail_lists = []
        self.current_tab_index = 0
        self.shared_detail_list = None
        self.global_placed_components = set()
        
        # Check if we have pumps configured
        if not self.config['pumps']:
            # Show message when no pumps are configured
            self._create_no_pumps_message()
            return
        
        # Create tabview for multiple pumps
        self.tab_view = ThemedTabview(self.content_frame)
        self.tab_view.pack(fill="both", expand=True)
        
        # Create tabs for each pump
        for i, pump_config in enumerate(self.config['pumps']):
            # Use unique display name for tab
            pump_display_name = pump_config.get('display_name', f'Pump {i+1}')
            tab = self.tab_view.add(pump_display_name)
            self.tabs.append(tab)
            
            # Configure grid for tab
            tab.grid_rowconfigure(0, weight=1)
            tab.grid_columnconfigure(0, weight=0, minsize=350)    # Detail list column
            tab.grid_columnconfigure(1, weight=1)                 # Circuit designer column
            
            # Create detail list for this specific pump only
            pump_specific_config = {
                "pump": pump_config,  # Only this pump's config
                "washing_components": self.config['washing_components']
            }
            detail_list = DetailList(
                tab, 
                self.controller, 
                config=pump_specific_config,
                on_component_select=lambda comp, idx=i: self._on_component_selected(comp, idx)
            )
            detail_list.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
            self.detail_lists.append(detail_list)
            
            # Create circuit designer container
            designer_frame = ctk.CTkFrame(tab, fg_color="transparent")
            designer_frame.grid(row=0, column=1, sticky="nsew", padx=(0,10), pady=10)
            
            # Configure grid for designer frame
            designer_frame.grid_rowconfigure(0, weight=1)  # Canvas
            designer_frame.grid_rowconfigure(1, weight=0)  # Mode selector
            designer_frame.grid_columnconfigure(0, weight=1)
            
            # Create circuit designer
            circuit_designer = CircuitDesigner(designer_frame, self.controller)
            circuit_designer.grid(row=0, column=0, sticky="nsew")
            self.circuit_designers.append(circuit_designer)
            
            # Connect detail list to circuit designer
            circuit_designer.set_detail_list(detail_list)
            circuit_designer.set_circuits_controller(self)
            
            # Create mode selector
            mode_selector = ModeSelector(
                designer_frame, 
                self.controller,
                on_mode_change=circuit_designer.set_mode
            )
            mode_selector.grid(row=1, column=0, sticky="ew")
            
            # Connect mode selector to circuit designer
            circuit_designer.mode_selector = mode_selector
        
        # Restore circuit states if we didn't clear them
        if not should_clear_circuits and self.saved_circuit_states:
            # Use after_idle to ensure all widgets are created before restoring
            self.after_idle(self._restore_circuit_states)
        
        # Sync all detail lists to share component availability
        self._sync_detail_lists_initial()
        
        # Add synthesis tab if we have pumps
        if self.config['pumps']:
            synthesis_tab = self.tab_view.add("Synthesis")
            synthesis_label = ctk.CTkLabel(
                synthesis_tab, 
                text="Synthesis view will show combined circuit designs"
            )
            synthesis_label.pack(pady=20)
    
    def _create_no_pumps_message(self):
        """Create content when no pumps are configured"""
        # Create a centered message frame
        message_frame = ctk.CTkFrame(self.content_frame)
        message_frame.pack(expand=True, fill="both", padx=50, pady=50)
        
        # Center the message
        message_frame.grid_rowconfigure(0, weight=1)
        message_frame.grid_rowconfigure(2, weight=1)
        message_frame.grid_columnconfigure(0, weight=1)
        
        # Icon or warning symbol
        warning_label = ctk.CTkLabel(
            message_frame,
            text="⚠️",
            font=("Arial", 48),
        )
        warning_label.grid(row=0, column=0, pady=(0, 20), padx=(70,0))
        
        # Main message
        main_message = ctk.CTkLabel(
            message_frame,
            text="No Pumps Configured",
            font=self.controller.fonts.get("title", ("Arial", 24, "bold")),
        )
        main_message.grid(row=1, column=0, pady=(0, 10))
        
        # Detailed message
        detail_message = ctk.CTkLabel(
            message_frame,
            text="Please configure pumps in the previous page\nbefore designing circuits.",
            font=self.controller.fonts.get("default", ("Arial", 14)),
            justify="center"
        )
        detail_message.grid(row=2, column=0, pady=(0, 20))
        
        # Button to go back to pumps page
        back_to_pumps_button = CustomButton(
            message_frame,
            text="Configure Pumps",
            font=self.controller.fonts.get("default", None),
            icon_path="assets/icons/back.png",
            icon_side="left",
            outlined=False,
            command=lambda: self.controller.show_page("pumps")
        )
        back_to_pumps_button.grid(row=3, column=0, pady=20)
    
    def _sync_detail_lists_initial(self):
        """Sync all detail lists to check for already placed components"""
        # Collect all placed components from all circuit designers
        all_placed = set()
        for designer in self.circuit_designers:
            placed = designer.get_placed_components()
            all_placed.update(placed)
        
        # Update all detail lists with placed components
        for detail_list in self.detail_lists:
            for component_name in all_placed:
                detail_list.mark_component_placed(component_name)
    
    def _on_component_placement(self, component_name, placed=True):
        """Handle component placement/removal across all tabs"""
        # Update all detail lists
        for detail_list in self.detail_lists:
            if placed:
                detail_list.mark_component_placed(component_name)
            else:
                detail_list.mark_component_available(component_name)
    
    def _get_config_from_controller(self):
        """Get configuration from controller (from previous pages)"""
        # Try to get actual config from controller
        if hasattr(self.controller, 'get_config_data'):
            try:
                # Get the configuration data
                washing_components = self.controller.get_config_data('washing_components')
                pumps_data = self.controller.get_config_data('pumps')
                
                # Convert to expected format
                config = {
                    "pumps": [],
                    "washing_components": []
                }
                
                # Process pumps data
                if pumps_data and isinstance(pumps_data, list):
                    for pump_index, pump in enumerate(pumps_data):
                        if isinstance(pump, dict):
                            # Convert pump data to expected format
                            pump_name = pump.get('Pump Name', 'Unknown Pump')
                            # Use existing ID or generate new one
                            pump_id = pump.get('id', f"pump_{uuid.uuid4().hex[:8]}")
                            pump_config = {
                                "id": pump_id,
                                "name": pump_name,
                                "display_name": f"{pump_name} ({pump_index + 1})" if pump_name else f"Pump {pump_index + 1}",
                                "outputs": int(pump.get('Number of output', 1)),
                                "max_connections": int(pump.get('Number of output', 1)),
                                "washing_components_per_output": {}
                            }
                            
                            # Parse washing components per output from the saved format
                            outputs = int(pump.get('Number of output', 1))
                            for i in range(1, outputs + 1):
                                # Look for keys like "Number of WC (O1)", "Number of WC (O2)", etc.
                                wc_key = f"Number of WC (O{i})"
                                if wc_key in pump:
                                    pump_config["washing_components_per_output"][i] = int(pump.get(wc_key, 0))
                                else:
                                    pump_config["washing_components_per_output"][i] = 0
                            
                            config["pumps"].append(pump_config)
                
                # Process washing components data
                if washing_components and isinstance(washing_components, list):
                    for comp_index, component in enumerate(washing_components):
                        if isinstance(component, dict):
                            comp_name = component.get('Component', 'Unknown Component')
                            # Use existing ID or generate new one
                            comp_id = component.get('id', f"component_{uuid.uuid4().hex[:8]}")
                            comp_config = {
                                "id": comp_id,
                                "name": comp_name,
                                "display_name": f"{comp_name} ({comp_index + 1})" if comp_name else f"Component {comp_index + 1}",
                                "type": "component"
                            }
                            config["washing_components"].append(comp_config)
                        elif isinstance(component, str):
                            # Handle string format
                            comp_config = {
                                "id": f"component_{uuid.uuid4().hex[:8]}",
                                "name": component,
                                "display_name": f"{component} ({comp_index + 1})" if component else f"Component {comp_index + 1}",
                                "type": "component"
                            }
                            config["washing_components"].append(comp_config)
                
                print(f"Loaded config from controller: {len(config['pumps'])} pumps, {len(config['washing_components'])} components")
                # Debug: Print pump configurations
                for pump in config['pumps']:
                    print(f"Pump: {pump['display_name']} (ID: {pump['id']}), Outputs: {pump['outputs']}, WC per output: {pump['washing_components_per_output']}")
                
                return config
                
            except Exception as e:
                print(f"Error getting config from controller: {e}")
        
        # Return empty config if no data available
        return {
            "pumps": [],
            "washing_components": []
        }

    def _follow_output_path_with_ids(self, start_id, circuit_data, components_by_id, visited=None):
        """Recursively follow the path from a given id, collecting component info with IDs."""
        if visited is None:
            visited = set()
        result = []
        if start_id in visited:
            return result
        visited.add(start_id)
        
        comp = components_by_id.get(start_id)
        if comp and comp.get('type') == 'component':
            result.append({
                'id': comp['id'],
                'name': comp['name'],
                'type': comp['type']
            })
        
        # Follow all outgoing connections
        for conn in circuit_data.get('connections', []):
            if conn['from'] == start_id:
                result += self._follow_output_path_with_ids(conn['to'], circuit_data, components_by_id, visited)
        return result

    def save_configuration(self):
        """Save the configuration via the controller"""
        circuits_data = []
        for i, designer in enumerate(self.circuit_designers):
            circuit_data = designer.get_circuit_data()
            circuits_data.append({
                "pump_index": i,
                "circuit": circuit_data
            })
        connection_summary = self._generate_overall_summary()
        enhanced_circuits_data = {
            'circuits': circuits_data,
            'connection_summary': connection_summary
        }
        print(f"Saving circuit configurations: {len(circuits_data)} circuits")
        if hasattr(self.controller, 'save_circuit_config'):
            self.controller.save_circuit_config(enhanced_circuits_data)
        if hasattr(self.controller, 'update_config_data'):
            self.controller.update_config_data('circuits', enhanced_circuits_data)
        print("Circuit configurations saved!")
        messagebox.showinfo("Configuration Saved", "Circuit configurations have been saved successfully.")

    def get_configuration(self):
        """Get current circuit configuration for controller saving"""
        if not hasattr(self, 'circuit_designers') or not self.circuit_designers:
            return []
        circuits_data = []
        for i, designer in enumerate(self.circuit_designers):
            if designer and hasattr(designer, 'get_circuit_data'):
                circuit_data = designer.get_circuit_data()
                circuits_data.append({
                    "pump_index": i,
                    "circuit": circuit_data
                })
        connection_summary = self._generate_overall_summary()
        enhanced_config = {
            'circuits': circuits_data,
            'connection_summary': connection_summary
        }
        print(f"Returning circuit configuration: {len(circuits_data)} circuits with connection summary")
        return enhanced_config
    
    def refresh_configuration(self):
        """Refresh the page with updated configuration from controller"""
        print("Refreshing circuits page configuration...")
        
        # Get updated configuration
        new_config = self._get_config_from_controller()
        
        # Check if configuration actually changed
        new_hash = self._get_config_hash(new_config)
        if self.last_config_hash == new_hash:
            print("Configuration unchanged, skipping refresh")
            return
        
        # Update configuration
        self.config = new_config
        
        # Recreate the content
        self._create_circuit_content()
        
        print(f"Circuits page refreshed: {len(self.config['pumps'])} pumps, {len(self.config['washing_components'])} components")
    
    def load_configuration(self, config_data):
        """Load configuration data and refresh the page"""
        print("Loading configuration for circuits page...")
        self.refresh_configuration()
    
    def _generate_overall_summary(self):
        """Generate overall summary with per-output component mapping using IDs."""
        connection_summary = []
        for i, (pump_config, designer) in enumerate(zip(self.config['pumps'], self.circuit_designers)):
            if not designer or not hasattr(designer, 'get_circuit_data'):
                pump_summary = {
                    "pump_index": i,
                    "pump_id": pump_config.get('id', f'pump_{i}'),
                    "pump_name": pump_config.get('display_name', f'Pump {i+1}'),
                    "outputs": {}
                }
                connection_summary.append(pump_summary)
                continue
            
            circuit_data = designer.get_circuit_data()
            outputs = self._generate_circuit_summary(circuit_data, pump_config)
            pump_summary = {
                "pump_index": i,
                "pump_id": pump_config.get('id', f'pump_{i}'),
                "pump_name": pump_config.get('display_name', f'Pump {i+1}'),
                "outputs": outputs
            }
            connection_summary.append(pump_summary)
        return connection_summary
    
    def _on_component_selected(self, component, tab_index):
        """Handle component selection from detail list"""
        if 0 <= tab_index < len(self.circuit_designers):
            designer = self.circuit_designers[tab_index]
            designer.set_selected_component(component)
            # Automatically switch to place mode
            if hasattr(designer, 'mode_selector'):
                mode_data = {
                    "mode": "place",
                    "component": component
                }
                designer.set_mode(mode_data)