import customtkinter as ctk
import tkinter
from components.custom_button import CustomButton
from utils.open_image import open_icon
from components.priority_selector import PrioritySelector
from components.sequence_visualizer import SequenceVisualizer

class Sequences(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        ctk.set_default_color_theme("theme.json")

        # Initialize configuration data
        self.config_data = {}
        self.connected_components = []  # List of components connected in circuits
        self.is_config_valid = False

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
            text="Configuration of sequences", 
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
        self.divider.pack(pady=(0, 20), fill="x")

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
            command=lambda: controller.show_page("results")
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
            command=lambda: controller.show_page("circuits")
        )
        self.back_button.pack(side="left")

        # ========================== Content Area ==========================
        # Content frame for the main content
        self.content_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=70, pady=30)

        # Load initial configuration and create content
        self.refresh_configuration()

    def refresh_configuration(self):
        """Refresh configuration from controller and recreate content"""
        print("Refreshing sequences page configuration...")
        
        # Get configuration from controller
        self.config_data = self._get_config_from_controller()
        
        # Transform circuit data to get connected components
        self.connected_components = self._transform_circuit_data()
        
        # Validate configuration
        self.is_config_valid = self._validate_configuration()
        
        # Clear existing content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        if self.is_config_valid:
            self._create_sequence_content()
        else:
            self._create_warning_content()
        
        print(f"Sequences page refreshed. Valid config: {self.is_config_valid}, Components: {len(self.connected_components)}")

    def _get_config_from_controller(self):
        """Get configuration data from controller"""
        if hasattr(self.controller, 'get_config_data'):
            return {
                'general_settings': self.controller.get_config_data('general_settings'),
                'washing_components': self.controller.get_config_data('washing_components'),
                'pumps': self.controller.get_config_data('pumps'),
                'circuits': self.controller.get_config_data('circuits')
            }
        return {}


    # ========================== Transform data ==========================
    def _transform_circuit_data(self):
        """Transform circuit data to extract connected components per pump output"""
        connected_components = []
        
        circuits_data = self.config_data.get('circuits', [])
        pumps_data = self.config_data.get('pumps', [])
        
        print(f"Transforming circuit data:")
        print(f"  - Circuits data: {len(circuits_data)} items")
        print(f"  - Pumps data: {len(pumps_data)} items")
        
        # Debug: Print actual circuit data
        for i, circuit in enumerate(circuits_data):
            print(f"  - Circuit {i}: {circuit}")
        
        if not circuits_data or not pumps_data:
            print("  - No circuits or pumps data available")
            return connected_components
        
        try:
            for circuit_config in circuits_data:
                pump_index = circuit_config.get('pump_index', 0)
                circuit = circuit_config.get('circuit', {})
                
                print(f"  - Processing circuit for pump {pump_index}")
                print(f"    - Circuit has {len(circuit.get('components', []))} components")
                print(f"    - Circuit has {len(circuit.get('connections', []))} connections")
                
                # Debug: Print all connections
                connections = circuit.get('connections', [])
                for j, conn in enumerate(connections):
                    print(f"      - Connection {j}: {conn.get('from_name')} -> {conn.get('to_name')}")
                
                # Get pump information
                if pump_index < len(pumps_data):
                    pump_data = pumps_data[pump_index]
                    pump_name = pump_data.get('Pump Name', f'Pump {pump_index + 1}')
                    num_outputs = int(pump_data.get('Number of output', 1))
                    
                    print(f"    - Pump name: '{pump_name}', Outputs: {num_outputs}")
                    
                    # Initialize pump structure
                    pump_structure = {
                        'pump_index': pump_index,
                        'pump_name': pump_name,
                        'outputs': {}
                    }
                    
                    # Initialize outputs
                    for output_num in range(1, num_outputs + 1):
                        pump_structure['outputs'][output_num] = []
                    
                    # Process connections to find components connected to each output
                    components = circuit.get('components', [])
                    
                    print(f"    - Processing {len(connections)} connections")
                    
                    # Create component lookup by name for easier matching
                    component_lookup = {}
                    for comp in components:
                        if comp.get('type') == 'component':  # Only washing components
                            component_lookup[comp['name']] = comp
                            print(f"      - Found component: {comp['name']} at {comp['position']}")
                    
                    # For each output, trace all possible connections to find all components
                    for output_num in range(1, num_outputs + 1):
                        output_components = self._find_all_components_for_output(
                            pump_name, output_num, connections, component_lookup
                        )
                        pump_structure['outputs'][output_num] = output_components
                        print(f"    - Output {output_num}: {len(output_components)} components - {output_components}")
                    
                    # Only add pump if it has any connected components
                    has_connections = any(components for components in pump_structure['outputs'].values())
                    if has_connections:
                        connected_components.append(pump_structure)
                        print(f"    - Added pump structure")
                    else:
                        print(f"    - No connected components found for pump {pump_name}")
                        
        except Exception as e:
            print(f"Error transforming circuit data: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"Final connected components: {len(connected_components)}")
        for comp in connected_components:
            print(f"  - {comp['pump_name']}: {comp['outputs']}")
        return connected_components

    def _find_all_components_for_output(self, pump_name, output_num, connections, component_lookup):
        """Find all washing components connected to a specific pump output"""
        found_components = []
        
        print(f"      - Finding components for output {output_num}")
        print(f"      - Looking for pump name: '{pump_name}'")
        
        # Get pump data to check if it's single or multi-output
        pump_data = next((p for p in self.config_data.get('pumps', []) if p.get('Pump Name') == pump_name), None)
        is_single_output = pump_data and int(pump_data.get('Number of output', 1)) == 1
        
        print(f"      - Is single output pump: {is_single_output}")
        
        # First, look for explicit output connections (for both single and multi-output pumps)
        explicit_output_names = [
            f"{pump_name} Output {output_num}",
            f"{pump_name} Output({output_num})",
            f"{pump_name} - Output {output_num}",
            f"{pump_name}_Output_{output_num}",
            f"{pump_name} Out {output_num}",
        ]
        
        print(f"        - Checking explicit output names: {explicit_output_names}")
        
        # Check for connections from explicit output names
        for output_name in explicit_output_names:
            components = self._trace_all_paths_from_node(output_name, connections, component_lookup, set())
            for comp in components:
                if comp not in found_components:
                    found_components.append(comp)
                    print(f"        - Found component via explicit output {output_name}: {comp}")
        
        # If no explicit output connections found, handle direct pump connections
        if not found_components:
            print(f"        - No explicit output connections found, checking direct pump connections")
            
            # Get all direct connections from the pump
            direct_connections = []
            for conn in connections:
                if conn.get('from_name') == pump_name:
                    direct_connections.append(conn)
            
            print(f"        - Found {len(direct_connections)} direct connections from pump")
            
            if is_single_output and output_num == 1:
                # For single output pumps, all connections go to output 1
                print(f"        - Single output pump, assigning all connections to output 1")
                for conn in direct_connections:
                    to_name = conn.get('to_name')
                    print(f"        - Processing connection: {pump_name} -> {to_name}")
                    
                    if to_name in component_lookup and to_name not in found_components:
                        found_components.append(to_name)
                        print(f"        - Added direct component: {to_name}")
                    elif to_name:
                        # Trace from this intermediate node
                        components = self._trace_all_paths_from_node(to_name, connections, component_lookup, set())
                        for comp in components:
                            if comp not in found_components:
                                found_components.append(comp)
                                print(f"        - Added traced component: {comp}")
            
            elif not is_single_output:
                # For multi-output pumps with direct connections, distribute based on pump WC configuration
                print(f"        - Multi-output pump, distributing connections based on WC configuration")
                
                if direct_connections and pump_data:
                    # Get the expected number of components for this output from pump configuration
                    expected_components = int(pump_data.get(f'Number of WC (O{output_num})', 0))
                    print(f"        - Expected components for output {output_num}: {expected_components}")
                    
                    if expected_components > 0:
                        # Collect all components that can be reached from the pump
                        all_reachable_components = []
                        for conn in direct_connections:
                            to_name = conn.get('to_name')
                            if to_name in component_lookup:
                                all_reachable_components.append(to_name)
                            elif to_name:
                                # Trace from this intermediate node to find components
                                components = self._trace_all_paths_from_node(to_name, connections, component_lookup, set())
                                all_reachable_components.extend(components)
                        
                        # Remove duplicates while preserving order
                        unique_components = []
                        for comp in all_reachable_components:
                            if comp not in unique_components:
                                unique_components.append(comp)
                        
                        print(f"        - Found {len(unique_components)} total reachable components: {unique_components}")
                        
                        # Distribute components to outputs based on WC configuration
                        # Calculate the starting index for this output
                        start_idx = 0
                        num_outputs = int(pump_data.get('Number of output', 1))
                        for i in range(1, output_num):
                            prev_output_components = int(pump_data.get(f'Number of WC (O{i})', 0))
                            start_idx += prev_output_components
                        
                        end_idx = start_idx + expected_components
                        
                        print(f"        - Output {output_num} gets components from index {start_idx} to {end_idx-1}")
                        
                        # Assign the appropriate components to this output
                        for i in range(start_idx, min(end_idx, len(unique_components))):
                            component = unique_components[i]
                            if component not in found_components:
                                found_components.append(component)
                                print(f"        - Assigned component {i}: {component}")
        
        # Also check pattern matching in connections for explicit output references
        for conn in connections:
            from_name = conn.get('from_name', '')
            to_name = conn.get('to_name', '')
            
            # Check if the from_name contains the pump name and THIS specific output number
            if (pump_name in from_name and 
                str(output_num) in from_name and 
                self._is_output_specific_connection(from_name, pump_name, output_num)):
                
                print(f"        - Found output-specific connection: {from_name} -> {to_name}")
                
                # Check if target is directly a washing component
                if to_name in component_lookup and to_name not in found_components:
                    found_components.append(to_name)
                    print(f"        - Found direct component: {to_name}")
                else:
                    # Trace from this intermediate node
                    components = self._trace_all_paths_from_node(to_name, connections, component_lookup, set())
                    for comp in components:
                        if comp not in found_components:
                            found_components.append(comp)
                            print(f"        - Found traced component: {comp}")
        
        print(f"      - Output {output_num} final components: {found_components}")
        return found_components

    def _trace_all_paths_from_node(self, start_node, connections, component_lookup, visited):
        """Trace all possible paths from a node to find all connected washing components"""
        if not start_node or start_node in visited:
            return []
        
        visited = visited.copy()
        visited.add(start_node)
        
        found_components = []
        
        # If current node is a washing component, add it
        if start_node in component_lookup:
            found_components.append(start_node)
            print(f"          - Found washing component: {start_node}")
            return found_components
        
        # Find ALL outgoing connections from this node (not just the first one)
        outgoing_connections = []
        for conn in connections:
            if conn.get('from_name') == start_node:
                next_node = conn.get('to_name')
                if next_node and next_node not in visited:
                    outgoing_connections.append(next_node)
        
        print(f"          - Node {start_node} has {len(outgoing_connections)} outgoing connections: {outgoing_connections}")
        
        # Recursively trace from all next nodes
        for next_node in outgoing_connections:
            components = self._trace_all_paths_from_node(next_node, connections, component_lookup, visited)
            for comp in components:
                if comp not in found_components:
                    found_components.append(comp)
                    print(f"          - Added component from path via {next_node}: {comp}")
        
        return found_components

    def _is_output_specific_connection(self, from_name, pump_name, output_num):
        """Check if a connection name specifically refers to this output number"""
        # Convert output_num to string for comparison
        output_str = str(output_num)
        
        # Remove pump name to focus on the output part
        output_part = from_name.replace(pump_name, '').strip()
        
        # Check various patterns that indicate this specific output
        output_indicators = [
            f"Output {output_str}",
            f"Output({output_str})",
            f"- Output {output_str}",
            f"_Output_{output_str}",
            f"Out {output_str}",
            f"O{output_str}",
        ]
        
        for indicator in output_indicators:
            if indicator in output_part:
                # Make sure it's not part of a larger number (e.g., "10" when looking for "1")
                # Check that the output number is followed by a non-digit or end of string
                import re
                pattern = indicator.replace(output_str, f"\\b{output_str}\\b")
                if re.search(pattern, output_part):
                    print(f"          - Matched output pattern '{indicator}' in '{output_part}'")
                    return True
        
        return False

    def _validate_configuration(self):
        """Validate that configuration is complete for sequence design"""
        print(f"Validating configuration:")
        print(f"  - Pumps: {len(self.config_data.get('pumps', []))}")
        print(f"  - Circuits: {len(self.config_data.get('circuits', []))}")
        print(f"  - Connected components: {len(self.connected_components)}")
        
        # Check if we have pumps
        if not self.config_data.get('pumps'):
            print("  - Validation failed: No pumps")
            return False
        
        # Check if we have circuits configured
        if not self.config_data.get('circuits'):
            print("  - Validation failed: No circuits")
            return False
        
        # Check if we have connected components
        if not self.connected_components:
            print("  - Validation failed: No connected components")
            return False
        
        # Check if at least one pump has connected components
        has_connections = False
        for pump_data in self.connected_components:
            print(f"  - Pump {pump_data['pump_name']}: {pump_data['outputs']}")
            for output_components in pump_data['outputs'].values():
                if output_components:
                    print(f"    - Found connections: {output_components}")
                    has_connections = True
                    break
            if has_connections:
                break
        
        if not has_connections:
            print("  - Validation failed: No pump has connected components")
            return False
        
        print("  - Validation passed!")
        return has_connections

    # ========================== Warning Message (config not ok) ==========================
    def _create_warning_content(self):
        """Create warning content when configuration is incomplete"""
        # Configure grid for content frame
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        # Create warning frame
        warning_frame = ctk.CTkFrame(self.content_frame)
        warning_frame.grid(row=0, column=0, sticky="nsew", padx=50)
        
        # Configure warning frame grid
        warning_frame.grid_rowconfigure(0, weight=1)
        warning_frame.grid_rowconfigure(1, weight=0)
        warning_frame.grid_rowconfigure(2, weight=0) 
        warning_frame.grid_rowconfigure(3, weight=0)
        warning_frame.grid_rowconfigure(4, weight=1)
        warning_frame.grid_columnconfigure(0, weight=1)
        
        # Warning icon
        warning_icon = ctk.CTkLabel(
            warning_frame,
            text="⚠️",
            font=("Arial", 64),
        )
        warning_icon.grid(row=1, column=0, pady=(0, 15))
        
        # Warning title
        warning_title = ctk.CTkLabel(
            warning_frame,
            text="Incomplete Circuit Configuration",
            font=self.controller.fonts.get("title", ("Arial", 24, "bold")),
        )
        warning_title.grid(row=2, column=0, pady=(0, 15))
        
        # Warning message
        warning_message = ctk.CTkLabel(
            warning_frame,
            text="Please complete the circuit configuration before setting up sequences.\n\n" +
                 "Make sure you have:\n" +
                 "• Configured pumps\n" +
                 "• Designed circuits with connected washing components",
            font=self.controller.fonts.get("default", ("Arial", 14)),
            justify="center"
        )
        warning_message.grid(row=3, column=0, pady=(0, 20))
        
        # Button to go back to circuits
        back_to_circuits_button = CustomButton(
            warning_frame,
            text="Go to Circuits",
            font=self.controller.fonts.get("default", None),
            icon_path="assets/icons/back.png",
            icon_side="left",
            outlined=False,
            command=lambda: self.controller.show_page("circuits")
        )
        back_to_circuits_button.grid(row=4, column=0, pady=(0, 50))

    def _create_sequence_content(self):
        """Create the main sequence configuration content"""
        # Configure grid for content frame
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(1, weight=0)
        self.content_frame.grid_columnconfigure(0, weight=0)
        self.content_frame.grid_columnconfigure(1, weight=1)

        # ========================== SETUP SEQUENCE ==========================
        # Outer container frame for form and update button
        self.form_container = ctk.CTkFrame(self.content_frame, fg_color="#F8F8F8")
        self.form_container.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 20))
        
        # Configure the form container grid - adding header row
        self.form_container.grid_rowconfigure(0, weight=0)  # Header row - fixed height
        self.form_container.grid_rowconfigure(1, weight=1)  # Scrollable area expands
        self.form_container.grid_rowconfigure(2, weight=0)  # Button row fixed height
        self.form_container.grid_columnconfigure(0, weight=1)
        
        # Header frame for fixed column headers
        self.header_frame = ctk.CTkFrame(self.form_container, fg_color="transparent", height=50)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        # Configure grid for header frame to match scrollable content
        self.header_frame.grid_columnconfigure(0, weight=0, minsize=200)  # Task column
        self.header_frame.grid_columnconfigure(1, weight=1)               # Duration column
        self.header_frame.grid_columnconfigure(2, weight=1)               # Priority column
        
        # Header labels
        task_header = ctk.CTkLabel(
            self.header_frame, 
            text="Component", 
            font=self.controller.fonts.get("default", None),
            text_color="#0D0D0D",
            anchor="n"
        )
        task_header.grid(row=0, column=0, pady=(10, 10), sticky="n")
        
        duration_header = ctk.CTkLabel(
            self.header_frame, 
            text="Duration", 
            font=self.controller.fonts.get("default", None),
            text_color="#0D0D0D",
            anchor="n"
        )
        duration_header.grid(row=0, column=1, pady=(10, 10), sticky="n")
        
        priority_header = ctk.CTkLabel(
            self.header_frame, 
            text="Priority", 
            font=self.controller.fonts.get("default", None), 
            text_color="#0D0D0D",
            anchor="n"
        )
        priority_header.grid(row=0, column=2, pady=(10, 10), sticky="n")
        
        # Create scrollable frame for the form content
        self.form_frame = ctk.CTkScrollableFrame(
            self.form_container, 
            fg_color="transparent",
            width=450,
            corner_radius=0
        )
        self.form_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # Configure grid for scrollable form frame
        self.form_frame.grid_columnconfigure(0, weight=0, minsize=150)  # Left label column
        self.form_frame.grid_columnconfigure(1, weight=1)               # Duration column
        self.form_frame.grid_columnconfigure(2, weight=0)               # Priority column
        
        # Initialize task rows list
        self.task_rows = []
        
        # Create task rows based on connected components
        self._create_component_task_rows()

        # Update and Clear buttons - placed at bottom of form container, outside scrollable area
        self.button_container_frame = ctk.CTkFrame(
            self.form_container, 
            fg_color="transparent",
            height=80
        )
        self.button_container_frame.grid(row=2, column=0, sticky="ew", pady=(5, 10))
        
        # Configure grid for button container
        self.button_container_frame.grid_columnconfigure(0, weight=1)
        self.button_container_frame.grid_columnconfigure(1, weight=1)
        
        self.update_button = CustomButton(
            self.button_container_frame,
            text="Update",
            font=self.controller.fonts.get("default", None),
            icon_path="assets/icons/refresh.png",
            icon_side="left",
            outlined=False,
            command=self.update_sequence,
        )
        self.update_button.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="ew")
        
        self.clear_button = CustomButton(
            self.button_container_frame,
            text="Clear All",
            font=self.controller.fonts.get("default", None),
            icon_path="assets/icons/trash.png",
            icon_side="left",
            outlined=False,
            command=self.clear_all_tasks,
        )
        self.clear_button.grid(row=0, column=1, padx=(5, 10), pady=10, sticky="ew")

        # Create sequence visualizer
        self.sequence_visualizer = SequenceVisualizer(
            self.content_frame,
            self.controller,
            width=600,
            height=300
        )
        self.sequence_visualizer.grid(row=0, column=1, sticky="nsew", padx=(20, 0), pady=(0, 20))

    def _create_component_task_rows(self):
        """Create task rows based on connected components from circuit configuration"""
        row_num = 0
        
        for pump_data in self.connected_components:
            pump_name = pump_data['pump_name']
            
            # Create a section header for each pump
            pump_header = ctk.CTkLabel(
                self.form_frame,
                text=f"=== {pump_name} ===",
                font=self.controller.fonts.get("subtitle", None),
                text_color="#243783",
                anchor="w"
            )
            pump_header.grid(row=row_num, column=0, columnspan=3, padx=(20, 20), pady=(15, 5), sticky="ew")
            row_num += 1
            
            # Add components for each output
            for output_num, components in pump_data['outputs'].items():
                if components:  # Only show outputs that have connected components
                    # Output header
                    output_header = ctk.CTkLabel(
                        self.form_frame,
                        text=f"Output {output_num}:",
                        font=self.controller.fonts.get("default", None),
                        text_color="#666666",
                        anchor="w"
                    )
                    output_header.grid(row=row_num, column=0, columnspan=3, padx=(30, 20), pady=(5, 2), sticky="w")
                    row_num += 1
                    
                    # Create task row for each component
                    for component_name in components:
                        task_display_name = f"{component_name}"
                        task_full_name = f"{pump_name} - Output {output_num} - {component_name}"
                        self.create_task_row(task_display_name, task_full_name, "P", row_num)
                        row_num += 1
            
            # Add spacing between pumps
            if pump_data != self.connected_components[-1]:  # Not the last pump
                spacer = ctk.CTkLabel(self.form_frame, text="", height=10)
                spacer.grid(row=row_num, column=0, columnspan=3)
                row_num += 1

    def create_task_row(self, display_name, full_name, initial_priority, row_num):
        """Create a row with task name and priority selector"""
        # Task label with indentation for components
        task_label = ctk.CTkLabel(
            self.form_frame,
            text=display_name,
            font=self.controller.fonts.get("default", None), 
            text_color="#0D0D0D",
            anchor="w",
        )
        task_label.grid(row=row_num, column=0, padx=(20, 0), pady=(10, 0), sticky="w")

        # Frame for the entry and dropdown
        entry_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        entry_frame.grid(row=row_num, column=1, padx=(20, 0), pady=(10, 0), sticky="ew")
        
        duration_entry = ctk.CTkEntry(
            entry_frame, 
            font=self.controller.fonts.get("default", None), 
            placeholder_text="Duration",
            width=70,
            fg_color="#F8F8F8",
            border_color="#243783",
            text_color="#243783",
            placeholder_text_color="#243783",
        )
        duration_entry.pack(side="left", padx=(0, 10))
        
        unit_dropdown = ctk.CTkOptionMenu(
            entry_frame, 
            values=["s", "ms"], 
            font=self.controller.fonts.get("default", None),
            width=65,
            command=lambda x: None
        )
        unit_dropdown.pack(side="left", padx=(0, 10))
        unit_dropdown.set("s")
        
        # Priority selector
        priority_selector = PrioritySelector(
            self.form_frame,
            command=lambda p, t=full_name: self.on_priority_change(t, p),
            initial_value=initial_priority
        )
        priority_selector.grid(row=row_num, column=2, padx=(5, 20), pady=(5, 0), sticky="ew")
        
        # Store references to the widgets for later access
        self.task_rows.append({
            'task_name': full_name,
            'display_name': display_name,
            'label': task_label,
            'entry_frame': entry_frame,
            'duration_entry': duration_entry,
            'unit_dropdown': unit_dropdown,
            'priority_selector': priority_selector
        })
        
        return priority_selector

    def load_configuration(self, config_data):
        """Load configuration data and refresh the page"""
        print("Loading configuration for sequences page...")
        self.refresh_configuration()

    def clear_all_tasks(self):
        """Clear all task rows except the first few default ones"""
        
        # Clear values in remaining tasks
        for row in self.task_rows:
            row['duration_entry'].delete(0, 'end')
            row['priority_selector'].select('P')
            row['unit_dropdown'].set("s")
    
        # Clear the visualization
        if hasattr(self, 'sequence_visualizer'):
            self.sequence_visualizer.clear_visualization()
    
    def on_priority_change(self, task, priority):
        """Handle priority change"""
        print(f"Task '{task}' priority changed to: {priority}")
        # You can add any additional logic here to handle priority changes
    
    def update_sequence(self):
        """Update the sequence based on current inputs"""
        # First save the current configuration to controller
        self.save_configuration()
        
        total_duration = 0
        tasks_data = []
        
        # Calculate total duration and collect task data
        for row in self.task_rows:
            try:
                duration_text = row['duration_entry'].get()
                if not duration_text:  # Skip empty entries
                    continue
                    
                duration = float(duration_text)
                unit = row['unit_dropdown'].get()
                priority = row['priority_selector'].get()
                task_name = row['display_name']
                
                # Convert to seconds for total calculation
                if unit == "ms":
                    duration_seconds = duration / 1000.0
                else:  # "s"
                    duration_seconds = duration
                    
                total_duration += duration_seconds
                
                # Add to tasks data for visualization
                tasks_data.append({
                    'name': task_name,
                    'duration': duration,
                    'unit': unit,
                    'priority': priority
                })
                
                print(f"Task: {task_name}, Duration: {duration}{unit}, Priority: {priority}")
            except ValueError:
                print(f"Invalid duration for task: {row['display_name']}")
        
        # Update the sequence visualizer
        if hasattr(self, 'sequence_visualizer'):
            self.sequence_visualizer.update_visualization(tasks_data)
        
        print("Sequence updated and configuration saved!")

    def update_appearance(self):
        """Update any appearance-dependent elements"""
        # Update the sequence visualizer appearance
        if hasattr(self, 'sequence_visualizer'):
            try:
                self.sequence_visualizer.update_appearance()
            except Exception as e:
                print(f"Error updating sequence visualizer appearance: {e}")

    def save_configuration(self):
        """Save the configuration via the controller"""
        # Collect all task data
        tasks_data = []
        total_duration_seconds = 0
        
        for row in self.task_rows:
            try:
                duration_text = row['duration_entry'].get()
                if not duration_text:  # Skip empty entries
                    continue
                    
                duration = float(duration_text)
                unit = row['unit_dropdown'].get()
                priority = row['priority_selector'].get()
                task_name = row['task_name']  # Use full name for saving
                display_name = row['display_name']
                
                # Convert to seconds for duration_seconds field
                if unit == "ms":
                    duration_seconds = duration / 1000.0
                else:  # "s"
                    duration_seconds = duration
                    
                total_duration_seconds += duration_seconds
                
                # Add task to the list
                tasks_data.append({
                    "name": task_name,
                    "display_name": display_name,
                    "duration": duration,
                    "unit": unit,
                    "priority": priority,
                    "duration_seconds": duration_seconds
                })
                
            except ValueError:
                print(f"Invalid duration for task: {row['display_name']} - skipping")
        
        # Create the sequence configuration dictionary
        sequence_configuration = {
            "sequence_configuration": {
                "tasks": tasks_data,
                "total_duration_seconds": total_duration_seconds,
                "total_tasks": len(tasks_data),
                "connected_components": self.connected_components  # Include component structure
            }
        }
        
        # Save to controller
        if hasattr(self.controller, 'save_sequence_config'):
            self.controller.save_sequence_config(sequence_configuration)
        
        # Also update config data directly
        if hasattr(self.controller, 'update_config_data'):
            self.controller.update_config_data('sequences', sequence_configuration)
        
        print("Sequence configuration saved!")
        
        # Return the data in case you want to use it elsewhere
        return sequence_configuration

    def get_configuration(self):
        """Get current sequence configuration for controller saving"""
        if not hasattr(self, 'task_rows') or not self.task_rows:
            return {}
        
        # Use the same logic as save_configuration but return the data
        tasks_data = []
        total_duration_seconds = 0
        
        for row in self.task_rows:
            try:
                duration_text = row['duration_entry'].get()
                if not duration_text:
                    continue
                    
                duration = float(duration_text)
                unit = row['unit_dropdown'].get()
                priority = row['priority_selector'].get()
                task_name = row['task_name']
                display_name = row['display_name']
                
                if unit == "ms":
                    duration_seconds = duration / 1000.0
                else:
                    duration_seconds = duration
                    
                total_duration_seconds += duration_seconds
                
                tasks_data.append({
                    "name": task_name,
                    "display_name": display_name,
                    "duration": duration,
                    "unit": unit,
                    "priority": priority,
                    "duration_seconds": duration_seconds
                })
                
            except ValueError:
                continue
        
        return {
            "sequence_configuration": {
                "tasks": tasks_data,
                "total_duration_seconds": total_duration_seconds,
                "total_tasks": len(tasks_data),
                "connected_components": getattr(self, 'connected_components', [])
            }
        }
