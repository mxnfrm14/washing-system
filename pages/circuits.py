import customtkinter as ctk
from components.custom_button import CustomButton
from components.tabview import ThemedTabview
import tkinter as tk
import tkinter.messagebox as messagebox
from components.circuit_designer import CircuitDesigner
from components.detail_list import DetailList
from components.mode_selector import ModeSelector
import uuid
from components.synthesis import Synthesis

class Circuits(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        ctk.set_default_color_theme("theme.json")
        
        # Track configuration hash to detect changes
        self.last_config_hash = None
        self.saved_circuit_states = {}  # Store circuit data for each pump
        
        # Synthesis tab references
        self.synthesis_tab = None
        self.synthesis_content = None
        self.synthesis_placeholder = None
        
        # Polling state
        self._polling_active = False
        self._last_circuit_state = None
        
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
            command=self.save_to_disk
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
            command=lambda: self.save_and_next()
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
            command=lambda: self.save_and_back()
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
    
    # def _restore_circuit_to_designer(self, designer, circuit_data):
    #     """Restore a specific circuit to a designer"""
    #     if not circuit_data or not designer:
    #         return
        
    #     # Restore components
    #     components = circuit_data.get('components', [])
    #     for comp_data in components:
    #         try:
    #             # Recreate the component data structure
    #             component = {
    #                 'name': comp_data['name'],
    #                 'type': comp_data['type'],
    #                 'max_connections': comp_data.get('connections', 0)
    #             }
                
    #             # If it's a connector, add subtype
    #             if comp_data['type'] in ['t_connector', 'y_connector', 'straight_connector']:
    #                 component['subtype'] = comp_data['type']
    #                 component['type'] = 'connector'
                
    #             # Place the component
    #             x, y = comp_data['position']
    #             designer.place_component(x, y, component)
                
    #         except Exception as e:
    #             print(f"Error restoring component {comp_data.get('name', 'Unknown')}: {e}")
        
    #     # Restore connections after all components are placed
    #     connections = circuit_data.get('connections', [])
    #     for conn_data in connections:
    #         try:
    #             # Find the placed items by matching names and positions
    #             from_item_id = None
    #             to_item_id = None
                
    #             for item_id, item_data in designer.placed_items.items():
    #                 if item_data['name'] == conn_data['from_name']:
    #                     from_item_id = item_id
    #                 elif item_data['name'] == conn_data['to_name']:
    #                     to_item_id = item_id
                
    #             if from_item_id and to_item_id:
    #                 designer.create_connection(from_item_id, to_item_id, conn_data.get('parameters', {}))
                
    #         except Exception as e:
    #             print(f"Error restoring connection: {e}")
    
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

    def _create_synthesis_placeholder(self):
        """Create placeholder content for synthesis tab when circuit is not completed"""
        placeholder_frame = ctk.CTkFrame(self.synthesis_tab)
        placeholder_frame.pack(fill="both", expand=True, padx=50, pady=50)
        
        # Center the content
        placeholder_frame.grid_rowconfigure(0, weight=1)
        placeholder_frame.grid_rowconfigure(2, weight=1)
        placeholder_frame.grid_columnconfigure(0, weight=1)
        
        # Icon
        icon_label = ctk.CTkLabel(
            placeholder_frame,
            text="🔧",
            font=("Arial", 48)
        )
        icon_label.grid(row=0, column=0, pady=(0, 10))
        
        # Main message
        main_message = ctk.CTkLabel(
            placeholder_frame,
            text="Circuit Synthesis Not Available",
            font=self.controller.fonts.get("title", ("Arial", 24, "bold"))
        )
        main_message.grid(row=1, column=0, pady=(0, 10))
        
        # Detailed message
        detail_message = ctk.CTkLabel(
            placeholder_frame,
            text="Please complete all circuit configurations\nto view the synthesis diagram.",
            font=self.controller.fonts.get("default", ("Arial", 14)),
            justify="center"
        )
        detail_message.grid(row=2, column=0, pady=(0, 10))
        
        # Requirements list
        requirements_frame = ctk.CTkFrame(placeholder_frame, fg_color="transparent")
        requirements_frame.grid(row=3, column=0, pady=10)
        
        requirements_title = ctk.CTkLabel(
            requirements_frame,
            text="Requirements:",
            font=self.controller.fonts.get("subtitle", ("Arial", 16, "bold"))
        )
        requirements_title.pack(pady=(0, 10))
        
        requirements = [
            "✓ Place all pumps in circuits",
            "✓ Connect pumps to components or connectors",
            "✓ Ensure all washing components are connected",
            "✓ Complete pipe configurations for all connections"
        ]
        
        for req in requirements:
            req_label = ctk.CTkLabel(
                requirements_frame,
                text=req,
                font=self.controller.fonts.get("default", ("Arial", 12)),
                anchor="w"
            )
            req_label.pack(anchor="w", pady=2)
        
        # Add refresh button
        refresh_button = CustomButton(
            placeholder_frame,
            text="Check Again",
            font=self.controller.fonts.get("default", None),
            icon_path="assets/icons/refresh.png",
            icon_side="left",
            outlined=False,
            command=self._manual_refresh_synthesis
        )
        refresh_button.grid(row=4, column=0, pady=10)
        
        return placeholder_frame
    
    def _start_synthesis_polling(self):
        """Start polling for circuit changes to update synthesis tab"""
        self._last_circuit_state = None
        self._polling_active = True
        self._check_circuit_changes()
    
    def _stop_synthesis_polling(self):
        """Stop polling for circuit changes"""
        self._polling_active = False
        if hasattr(self, '_polling_after_id'):
            try:
                self.after_cancel(self._polling_after_id)
            except:
                pass
    
    def _check_circuit_changes(self):
        """Check if circuits have changed and update synthesis if needed"""
        if not self._polling_active:
            return
        
        try:
            # Get current circuit state
            current_state = self._get_circuit_state_hash()
            
            # Compare with last known state
            if hasattr(self, '_last_circuit_state') and current_state != self._last_circuit_state:
                print("Circuit state changed, updating synthesis...")
                self._update_synthesis_tab()
            
            # Update last known state
            self._last_circuit_state = current_state
            
            # Schedule next check
            self._polling_after_id = self.after(2000, self._check_circuit_changes)  # Check every 2 seconds
            
        except Exception as e:
            print(f"Error in circuit change polling: {e}")
            # Continue polling even if there's an error
            self._polling_after_id = self.after(2000, self._check_circuit_changes)
    
    def _get_circuit_state_hash(self):
        """Get a hash representing the current state of all circuits"""
        import hashlib
        import json
        
        try:
            state_data = []
            for i, designer in enumerate(self.circuit_designers):
                if designer and hasattr(designer, 'get_circuit_data'):
                    circuit_data = designer.get_circuit_data()
                    # Simplify data for hashing
                    simplified = {
                        'components': len(circuit_data.get('components', [])),
                        'connections': len(circuit_data.get('connections', [])),
                        'component_types': sorted([comp.get('type', '') for comp in circuit_data.get('components', [])]),
                        'has_pump': any(comp.get('type') == 'pump' for comp in circuit_data.get('components', []))
                    }
                    state_data.append(simplified)
            
            state_str = json.dumps(state_data, sort_keys=True)
            return hashlib.md5(state_str.encode()).hexdigest()
        except Exception as e:
            print(f"Error generating circuit state hash: {e}")
            return str(hash(str(len(self.circuit_designers))))
    
    def _manual_refresh_synthesis(self):
        """Manually refresh synthesis tab when user clicks the button"""
        print("Manual synthesis refresh triggered...")
        self._update_synthesis_tab()
    
    def destroy(self):
        """Clean up when destroying the widget"""
        self._stop_synthesis_polling()
        super().destroy()

    def _create_circuit_content(self):
        """Create or recreate the circuit content based on current configuration"""
        # Stop any existing polling
        if hasattr(self, '_polling_active'):
            self._stop_synthesis_polling()
        
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
        self.synthesis_tab = None
        self.synthesis_content = None
        self.synthesis_placeholder = None
        
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
            self.synthesis_tab = self.tab_view.add("Synthesis")
            self._update_synthesis_tab()
            
            # Start polling for circuit changes
            self._start_synthesis_polling()
    
    def _update_synthesis_tab(self):
        """Update synthesis tab based on circuit completion status"""
        if not self.synthesis_tab:
            print("No synthesis tab found")
            return
        
        print("Updating synthesis tab...")
        
        # Clear existing content
        for widget in self.synthesis_tab.winfo_children():
            widget.destroy()
        
        # Check completion status
        is_complete = self.is_completed()
        print(f"Circuit completion status: {is_complete}")
        
        if is_complete:
            # Circuit is completed, show synthesis
            print("Creating synthesis content...")
            self.synthesis_content = Synthesis(
                parent=self.synthesis_tab, 
                controller=self.controller, 
                circuits=self.get_configuration()
            )
            self.synthesis_content.pack(fill="both", expand=True, padx=10, pady=10)
            self.synthesis_placeholder = None
            print("Synthesis tab enabled - circuit is completed")
        else:
            # Circuit is not completed, show placeholder
            print("Creating synthesis placeholder...")
            self.synthesis_placeholder = self._create_synthesis_placeholder()
            self.synthesis_content = None
            print("Synthesis tab disabled - circuit is not completed")
    
    def _on_component_placement(self, component_id, placed=True):
        """Handle component placement/removal across all tabs and update synthesis"""
        # Update all detail lists
        for detail_list in self.detail_lists:
            if placed:
                detail_list.mark_component_placed(component_id)
            else:
                detail_list.mark_component_available(component_id)
        
        # Update synthesis tab based on new completion status
        self._update_synthesis_tab()
    
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
    
    def _get_config_from_controller(self):
        """Get configuration from controller - Fixed to separate original vs display names"""
        if hasattr(self.controller, 'get_config_data'):
            try:
                washing_components = self.controller.get_config_data('washing_components')
                pumps_data = self.controller.get_config_data('pumps')
                
                config = {
                    "pumps": [],
                    "washing_components": []
                }
                
                # Process pumps - separate original name from display name
                if pumps_data and isinstance(pumps_data, list):
                    for pump_index, pump in enumerate(pumps_data):
                        if isinstance(pump, dict):
                            original_pump_name = pump.get('Pump Name', 'Unknown Pump')
                            pump_id = pump.get('id', f"pump_{uuid.uuid4().hex[:8]}")
                            
                            pump_config = {
                                "id": pump_id,
                                "name": original_pump_name,  # Original name for saving
                                "display_name": f"{original_pump_name} ({pump_index + 1})",  # Display name for UI
                                "outputs": int(pump.get('Number of output', 1)),
                                "max_connections": int(pump.get('Number of output', 1)),
                                "washing_components_per_output": {}
                            }
                            
                            outputs = int(pump.get('Number of output', 1))
                            for i in range(1, outputs + 1):
                                wc_key = f"Number of WC (O{i})"
                                pump_config["washing_components_per_output"][i] = int(pump.get(wc_key, 0))
                            
                            config["pumps"].append(pump_config)
                
                # Process washing components - separate original name from display name
                if washing_components and isinstance(washing_components, list):
                    for comp_index, component in enumerate(washing_components):
                        if isinstance(component, dict):
                            original_comp_name = component.get('Component', 'Unknown Component')
                            comp_id = component.get('id', f"component_{uuid.uuid4().hex[:8]}")
                            
                            comp_config = {
                                "id": comp_id,
                                "name": original_comp_name,  # Original name for saving
                                "display_name": f"{original_comp_name} ({comp_index + 1})",  # Display name for UI
                                "type": "component"
                            }
                            config["washing_components"].append(comp_config)
                        elif isinstance(component, str):
                            comp_config = {
                                "id": f"component_{uuid.uuid4().hex[:8]}",
                                "name": component,  # Original name
                                "display_name": f"{component} ({comp_index + 1})",  # Display name
                                "type": "component"
                            }
                            config["washing_components"].append(comp_config)
                
                print(f"Loaded config from controller: {len(config['pumps'])} pumps, {len(config['washing_components'])} components")
                return config
                
            except Exception as e:
                print(f"Error getting config from controller: {e}")
        
        return {"pumps": [], "washing_components": []}

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

    def save_current_configuration(self):
        """Save the configuration via the controller"""
        circuits_data = self.get_configuration()  # Ensure we have the latest configuration
        self.controller.update_config_data('circuits', circuits_data)

    def save_to_disk(self):
        """Save the current circuit configuration to disk"""
        self.save_current_configuration()
        # Save to disk
        if self.controller.save_whole_configuration():
            messagebox.showinfo("Success", "Configuration saved successfully!")
        else:
            messagebox.showerror("Error", "Failed to save configuration!")

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
        """Load configuration data and restore all circuit designs"""
        print("🔄 Loading configuration for circuits page...")
        
        # Extract circuit data from config
        loaded_circuits_data = None
        if 'circuits' in config_data:
            circuits_section = config_data['circuits']
            if isinstance(circuits_section, dict) and 'circuits' in circuits_section:
                loaded_circuits_data = circuits_section['circuits']
            elif isinstance(circuits_section, list):
                loaded_circuits_data = circuits_section
        
        print(f"📊 Found {len(loaded_circuits_data) if loaded_circuits_data else 0} circuits to restore")
        
        # Refresh the configuration (rebuilds UI with new pump/component data)
        self.refresh_configuration()
        
        # Restore circuits after UI is built
        if loaded_circuits_data:
            self.after_idle(lambda: self._restore_circuits_from_config(loaded_circuits_data))


    def _restore_circuits_from_config(self, circuits_data):
        """Restore circuit designs from loaded configuration data"""
        print(f"🔧 Restoring {len(circuits_data)} circuits...")
        
        if not hasattr(self, 'circuit_designers') or not self.circuit_designers:
            print("❌ No circuit designers available")
            return
        
        restored_count = 0
        
        for circuit_config in circuits_data:
            pump_index = circuit_config.get("pump_index", 0)
            circuit_data = circuit_config.get("circuit", {})
            
            if 0 <= pump_index < len(self.circuit_designers):
                designer = self.circuit_designers[pump_index]
                components = circuit_data.get('components', [])
                connections = circuit_data.get('connections', [])
                
                if designer and (components or connections):
                    print(f"  📦 Restoring circuit {pump_index}: {len(components)} components, {len(connections)} connections")
                    try:
                        self._restore_single_circuit(designer, circuit_data)
                        restored_count += 1
                        print(f"  ✅ Circuit {pump_index} restored successfully")
                    except Exception as e:
                        print(f"  ❌ Error restoring circuit {pump_index}: {e}")
            else:
                print(f"  ⚠️ Invalid pump index: {pump_index}")
        
        print(f"🎉 Restoration complete: {restored_count}/{len(circuits_data)} circuits restored")
        
        # Update synthesis tab
        self._update_synthesis_tab()
        
        # Mark as completed if any circuits were restored
        if restored_count > 0:
            self.controller.mark_page_completed("circuits")

    def _restore_single_circuit(self, designer, circuit_data):
        """Restore a single circuit to its designer - with better position handling"""
        # Clear existing circuit
        designer.reset_canvas()
        
        components = circuit_data.get('components', [])
        connections = circuit_data.get('connections', [])
        
        if not components:
            return
        
        # Give the canvas a moment to properly size itself
        designer.canvas.update_idletasks()
        
        # Phase 1: Place all components
        id_mapping = {}  # Map saved canvas IDs to new canvas IDs
        placed_component_ids = []  # Track component IDs that were placed
        
        for comp_data in components:
            comp_name = comp_data.get('name', 'Unknown')
            comp_type = comp_data.get('type', 'unknown')
            position = comp_data.get('position', [100, 100])
            saved_canvas_id = comp_data.get('id')
            
            print(f"    🔧 Restoring: {comp_name} ({comp_type}) at {position}")
            
            # Find the corresponding component in our configuration
            component_info = self._find_component_config(comp_name, comp_type)
            
            if component_info:
                # Place the component at the saved position
                x, y = position
                designer.place_component(x, y, component_info)
                
                # Find the newly created canvas item (with flexible position matching)
                new_canvas_id = self._find_placed_component(designer, comp_name, comp_type, x, y)
                if new_canvas_id:
                    id_mapping[saved_canvas_id] = new_canvas_id
                    print(f"      ✅ Placed {comp_name} -> canvas ID {new_canvas_id}")
                    
                    # Track placed components for detail list updates (only pumps and components)
                    if comp_type in ['pump', 'component']:
                        actual_component_id = component_info.get('id')
                        if actual_component_id:
                            placed_component_ids.append(actual_component_id)
                else:
                    print(f"      ❌ Could not find placed component: {comp_name}")
                    # Debug: show all placed items
                    print(f"      🔍 Available items:")
                    for item_id, item_data in designer.placed_items.items():
                        print(f"        - {item_id}: {item_data.get('name')} ({item_data.get('type')}) at {item_data.get('coords')}")
            else:
                print(f"      ❌ Could not find config for: {comp_name} ({comp_type})")
        
        # Phase 2: Restore connections
        print(f"    🔗 Restoring {len(connections)} connections...")
        for conn_data in connections:
            saved_from_id = conn_data.get('from')
            saved_to_id = conn_data.get('to')
            parameters = conn_data.get('parameters', {})
            
            # Map to new canvas IDs
            new_from_id = id_mapping.get(saved_from_id)
            new_to_id = id_mapping.get(saved_to_id)
            
            if new_from_id and new_to_id:
                designer.create_connection(new_from_id, new_to_id, parameters)
                print(f"      🔗 Connected {conn_data.get('from_name', '')} -> {conn_data.get('to_name', '')}")
            else:
                print(f"      ❌ Could not restore connection: {saved_from_id} -> {saved_to_id}")
                print(f"          From ID {saved_from_id} mapped to {new_from_id}")
                print(f"          To ID {saved_to_id} mapped to {new_to_id}")
                print(f"          Available mappings: {id_mapping}")
        
        # Phase 3: Update detail lists to reflect placed components
        print(f"    📋 Updating detail lists for {len(placed_component_ids)} placed components...")
        for component_id in placed_component_ids:
            # Notify all detail lists that this component has been placed
            self._on_component_placement(component_id, placed=True)
            print(f"      ✅ Marked component {component_id} as placed in detail lists")

    def _find_component_config(self, comp_name, comp_type):
        """Find component configuration data using original names"""
        print(f"      🔍 Looking for {comp_type}: '{comp_name}'")
        
        if comp_type == 'pump':
            # Find pump by original name (no suffixes)
            for pump in self.config.get('pumps', []):
                pump_name = pump.get('name', '')  # Original name without suffix
                
                if comp_name == pump_name:
                    print(f"        ✅ Found pump: {pump_name}")
                    return {
                        'name': comp_name,
                        'type': 'pump',
                        'id': pump.get('id', 'pump_unknown'),
                        'max_connections': pump.get('outputs', 2)
                    }
        
        elif comp_type == 'component':
            # Find washing component by original name (no suffixes)
            for component in self.config.get('washing_components', []):
                comp_config_name = component.get('name', '')  # Original name without suffix
                
                if comp_name == comp_config_name:
                    print(f"        ✅ Found component: {comp_config_name}")
                    return {
                        'name': comp_name,
                        'type': 'component',
                        'id': component.get('id', 'component_unknown'),
                        'max_connections': 1
                    }
        
        elif comp_type in ['t_connector', 'y_connector', 'straight_connector']:
            # Connectors don't need config lookup
            return {
                'name': comp_name,
                'type': 'connector',
                'subtype': comp_type,
                'max_connections': 3 if comp_type in ['t_connector', 'y_connector'] else 2
            }
        
        print(f"        ❌ No match found for {comp_type}: '{comp_name}'")
        return None

    def _find_placed_component(self, designer, comp_name, comp_type, x, y):
        """Find a placed component - flexible position matching for restoration"""
        print(f"        🔍 Looking for placed component: {comp_name} at ({x}, {y})")
        
        # First try: exact name and type match (ignore position for now)
        candidates = []
        for item_id, item_data in designer.placed_items.items():
            item_name = item_data.get('name', '')
            item_type = item_data.get('type', '')
            item_coords = item_data.get('coords', [0, 0])
            
            print(f"          Checking: {item_name} ({item_type}) at {item_coords}")
            
            # Check name and type match
            if comp_name == item_name and comp_type == item_type:
                candidates.append((item_id, item_coords))
                print(f"          ✅ Name/type match found: {item_id}")
        
        if not candidates:
            print(f"        ❌ No name/type matches found for {comp_name}")
            return None
        
        if len(candidates) == 1:
            # Only one match - return it regardless of position
            item_id = candidates[0][0]
            actual_coords = candidates[0][1]
            print(f"        ✅ Single match found: {item_id} at {actual_coords}")
            return item_id
        
        # Multiple matches - find closest by position
        print(f"        📍 Multiple matches found, finding closest to ({x}, {y})")
        best_match = None
        best_distance = float('inf')
        
        for item_id, item_coords in candidates:
            item_x, item_y = item_coords
            distance = ((item_x - x) ** 2 + (item_y - y) ** 2) ** 0.5
            print(f"          Distance to {item_id}: {distance:.1f}")
            
            if distance < best_distance:
                best_distance = distance
                best_match = item_id
        
        if best_match:
            print(f"        ✅ Best match: {best_match} (distance: {best_distance:.1f})")
            return best_match
        
        print(f"        ❌ No suitable match found")
        return None


    def _restore_circuit_to_designer(self, designer, circuit_data):
        """Restore a specific circuit to a designer (enhanced version)"""
        if not circuit_data or not designer:
            return
        
        try:
            # Clear existing circuit first
            designer.reset_canvas()
            
            # Get components and connections from circuit data
            components = circuit_data.get('components', [])
            connections = circuit_data.get('connections', [])
            
            print(f"Restoring {len(components)} components and {len(connections)} connections...")
            
            # First pass: Place all components
            placed_items_map = {}  # Map from saved component data to new item IDs
            
            for comp_data in components:
                try:
                    # Extract component information
                    comp_name = comp_data.get('name', 'Unknown')
                    comp_type = comp_data.get('type', 'unknown')
                    position = comp_data.get('position', [100, 100])
                    comp_id = comp_data.get('id', '')
                    
                    print(f"Restoring component: {comp_name} ({comp_type}) at {position}")
                    
                    # Create component data structure for placement
                    component_info = {
                        'name': comp_name,
                        'type': comp_type,
                        'id': comp_id
                    }
                    
                    # Handle different component types
                    if comp_type == 'pump':
                        # For pumps, get max connections from the component data
                        component_info['max_connections'] = comp_data.get('connections', 2)
                    elif comp_type in ['t_connector', 'y_connector', 'straight_connector']:
                        # For connectors, set type and subtype correctly
                        component_info['subtype'] = comp_type
                        component_info['type'] = 'connector'
                    elif comp_type == 'component':
                        # For washing components
                        component_info['max_connections'] = 1
                    
                    # Place the component at its saved position
                    x, y = position if isinstance(position, (list, tuple)) and len(position) >= 2 else [100, 100]
                    designer.place_component(x, y, component_info)
                    
                    # Store mapping for connection restoration
                    # We need to find the newly created item ID
                    for item_id, item_data in designer.placed_items.items():
                        if (item_data.get('name') == comp_name and 
                            item_data.get('type') == comp_type and
                            item_data.get('coords') == (x, y)):
                            placed_items_map[comp_id] = item_id
                            break
                    
                except Exception as e:
                    print(f"Error restoring component {comp_data.get('name', 'Unknown')}: {e}")
                    continue
            
            # Second pass: Restore connections after all components are placed
            print(f"Restoring {len(connections)} connections...")
            
            for conn_data in connections:
                try:
                    from_id = conn_data.get('from')
                    to_id = conn_data.get('to')
                    parameters = conn_data.get('parameters', {})
                    
                    # Map old IDs to new item IDs
                    new_from_id = placed_items_map.get(from_id)
                    new_to_id = placed_items_map.get(to_id)
                    
                    if new_from_id and new_to_id:
                        print(f"Restoring connection: {conn_data.get('from_name', '')} -> {conn_data.get('to_name', '')}")
                        designer.create_connection(new_from_id, new_to_id, parameters)
                    else:
                        print(f"Warning: Could not restore connection from {from_id} to {to_id} (items not found)")
                        
                except Exception as e:
                    print(f"Error restoring connection: {e}")
                    continue
            
            print(f"Successfully restored circuit to designer")
            
        except Exception as e:
            print(f"Error in _restore_circuit_to_designer: {e}")
            import traceback
            traceback.print_exc()
    
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
                "outputs":outputs
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
    
    def save_and_next(self):
        """Save configuration and navigate to the next page"""
        self.save_current_configuration()
        
        if self.is_completed():
            self.controller.mark_page_completed("circuits")
        else:
            self.controller.mark_page_incomplete("circuits")
            
        self.controller.show_page("sequence")
    
    def save_and_back(self):
        """Save configuration and navigate to the previous page"""
        self.save_current_configuration()
        if self.is_completed():
            self.controller.mark_page_completed("circuits")
        else:
            self.controller.mark_page_incomplete("circuits")
        self.controller.show_page("pumps")

    def on_leave_page(self):
        """Called when navigating away from this page"""
        # Save the current configuration
        self.save_current_configuration()
        
        # Check if the form is still complete enough to be marked as completed
        if self.is_completed():
            self.controller.mark_page_completed("circuits")
        else:
            # If it's no longer complete, mark as incomplete
            self.controller.mark_page_incomplete("circuits")
    
    def on_show_page(self):
        """Called when the page is shown"""
        # Check if the form is still complete
        if self.is_completed():
            self.controller.mark_page_completed("circuits")
        else:
            self.controller.mark_page_incomplete("circuits")

    def is_completed(self):
        """Check if the circuits page is completed"""
        print("Checking circuit completion status...")
        
        # Check if we have at least one pump configured
        if not self.config['pumps']:
            print("❌ No pumps configured")
            return False
        
        print(f"✓ Found {len(self.config['pumps'])} pumps configured")
        
        # Check if all circuit designers have valid circuits
        if not hasattr(self, 'circuit_designers') or not self.circuit_designers:
            print("❌ No circuit designers found")
            return False
        
        for i, designer in enumerate(self.circuit_designers):
            print(f"Checking circuit designer {i+1}...")
            
            if not designer or not hasattr(designer, 'get_circuit_data'):
                print(f"❌ Circuit designer {i+1} is invalid")
                return False
            
            circuit_data = designer.get_circuit_data()
            if not circuit_data or not circuit_data.get('components'):
                print(f"❌ Circuit designer {i+1} has no components")
                return False
            
            components = circuit_data.get('components', [])
            connections = circuit_data.get('connections', [])
            
            print(f"  - Components: {len(components)}")
            print(f"  - Connections: {len(connections)}")
            
            # Check if there's at least one pump component
            pump_components = [comp for comp in components if comp.get('type') == 'pump']
            if not pump_components:
                print(f"❌ Circuit {i+1} has no pump component")
                return False
            
            # Check if pump has at least one output connected
            pump_connected = False
            for pump_comp in pump_components:
                pump_id = pump_comp.get('id')
                pump_connections = [conn for conn in connections if conn.get('from') == pump_id]
                if pump_connections:
                    pump_connected = True
                    print(f"  ✓ Pump {pump_comp.get('name', 'Unknown')} has {len(pump_connections)} connections")
                    break
            
            if not pump_connected:
                print(f"❌ Circuit {i+1} pump has no output connections")
                return False
            
            # Check if there are washing components
            washing_components = [comp for comp in components if comp.get('type') == 'component']
            if washing_components:
                print(f"  ✓ Circuit {i+1} has {len(washing_components)} washing components")
            else:
                print(f"⚠️ Circuit {i+1} has no washing components (this might be okay if using connectors)")
        
        # If we reach here, all circuits are valid
        print("✅ All circuits are completed!")
        return True
    
    def reset_app(self):
        """Reset the application to initial state"""
        # Stop polling
        self._stop_synthesis_polling()
        
        # Clear all configurations
        self.config = {
            "pumps": [],
            "washing_components": []
        }
        
        # Reset instance variables
        self.last_config_hash = None
        self.saved_circuit_states = {}
        
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Recreate the content
        self._create_circuit_content()
        
        print("Application reset to initial state")