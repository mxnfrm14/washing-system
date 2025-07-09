import customtkinter as ctk
import tkinter
from tkinter import messagebox
from components.custom_button import CustomButton
from utils.open_image import open_icon
from components.priority_selector import PrioritySelector
from components.sequence_visualizer import SequenceVisualizer

class Sequences(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        ctk.set_default_color_theme("theme.json")

        # Track configuration hash to detect changes
        self.last_config_hash = None
        
        # Initialize task rows list and pump-output mapping first
        self.task_rows = []
        self.pump_output_mapping = {}
        self.component_to_pump_output = {}
        
        # Flag to track if UI is fully initialized
        self.ui_initialized = False

        # Add flag to prevent recursive priority changes
        self.is_applying_constraints = False

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
            text="Configuration of sequences", 
            font=self.controller.fonts.get("title", None), 
            anchor="w"
        )
        self.title_label.pack(side="left")

        # Save configuration button
        self.save_button = CustomButton(
            self.top_frame,
            text="Save configuration",
            font=self.controller.fonts.get("default", None),
            icon_path="assets/icons/save.png",
            icon_side="left",
            outlined=False,
            command=self.save_to_disk
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
            font=self.controller.fonts.get("default", None),
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
            font=self.controller.fonts.get("default", None),
            icon_path="assets/icons/back.png",
            icon_side="left",
            outlined=True,
            command=lambda: self.save_and_back()
        )
        self.back_button.pack(side="left")

        # Create UI components but don't load configuration yet
        self.create_ui_components()
    
    def create_ui_components(self):
        """Create all UI components - can be called to refresh the UI"""
        try:
            # Clear any existing UI components if they exist
            if hasattr(self, 'content_frame') and self.content_frame:
                for widget in self.content_frame.winfo_children():
                    widget.destroy()
                self.content_frame.destroy()
            
            # Reset UI initialization flag
            self.ui_initialized = False
            
            # ========================== Content Area ==========================
            # Content frame for the main content
            self.content_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
            self.content_frame.pack(fill="both", expand=True, padx=70, pady=30)
    
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
            self.header_frame.grid_columnconfigure(0, weight=0, minsize=150)  # Task column
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
            self.form_frame.grid_columnconfigure(1, weight=1)               # Left input column start
            self.form_frame.grid_columnconfigure(2, weight=0)               # Priority column
            
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
                custom_fg_color="#243783",
                custom_text_color="#F8F8F8",
                custom_hover_color="#8995C6",
                custom_border_color="#243783",
                command=self.update_sequence,
            )
            self.update_button.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="ew")
            
            self.clear_button = CustomButton(
                self.button_container_frame,
                text="Clear All",
                font=self.controller.fonts.get("default", None),
                icon_path="assets/icons/trash.png",
                icon_side="left",
                outlined=True,
                custom_fg_color="#F8F8F8",
                custom_text_color="#243783",
                custom_hover_color="#C8C8C8",
                custom_border_color="#243783",
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
            self.sequence_visualizer.grid(row=0, column=1, sticky="nsew", padx=(20, 0))
            
            # Mark UI as initialized only after all components are created
            self.ui_initialized = True
            print("UI components successfully created and initialized")
            
        except Exception as e:
            print(f"Error creating UI components: {e}")
            import traceback
            traceback.print_exc()
            self.ui_initialized = False  # Make sure flag is reset on error

    def _get_config_from_controller(self):
        """Get configuration from controller (from previous pages)"""
        # Try to get actual config from controller
        if hasattr(self.controller, 'get_config_data'):
            try:
                # Get the configuration data
                washing_components = self.controller.get_config_data('washing_components')
                pumps_data = self.controller.get_config_data('pumps')
                circuits_data = self.controller.get_config_data('circuits')
                sequences_data = self.controller.get_config_data('sequences')  # Add sequences data
                
                # Convert to expected format
                config = {
                    "washing_components": washing_components or [],
                    "pumps": pumps_data or [],
                    "circuits": circuits_data or [],
                    "sequences": sequences_data or {}  # Include sequences in config
                }
                
                print(f"Loaded config from controller: circuits={len(config.get('circuits', []))}, sequences={bool(sequences_data)}")
                return config
                
            except Exception as e:
                print(f"Error getting config from controller: {e}")
        
        # Return empty config if no data available
        return {
            "washing_components": [],
            "pumps": [],
            "circuits": [],
            "sequences": {}
        }

    def _get_config_hash(self, config):
        """Generate a hash of the configuration to detect changes"""
        import hashlib
        import json
        
        # Create a simplified version for hashing
        config_for_hash = {
            'washing_components': len(config.get('washing_components', [])),
            'pumps': len(config.get('pumps', [])),
            'circuits': len(config.get('circuits', []))
        }
        
        # Include circuit data in more detail
        circuits_data = config.get("circuits", [])
        if isinstance(circuits_data, list):
            config_for_hash['circuits_count'] = len(circuits_data)
        elif isinstance(circuits_data, dict) and 'connection_summary' in circuits_data:
            config_for_hash['connection_summary'] = len(circuits_data.get('connection_summary', []))
        
        config_str = json.dumps(config_for_hash, sort_keys=True)
        return hashlib.md5(config_str.encode()).hexdigest()

    def refresh_configuration(self):
        """Refresh the page with updated configuration from controller"""
        print("Refreshing sequences page configuration...")
        
        # Get updated configuration
        new_config = self._get_config_from_controller()
        
        # Check if configuration actually changed
        new_hash = self._get_config_hash(new_config)
        if self.last_config_hash == new_hash:
            print("Configuration unchanged, skipping refresh")
            return
        
        # Update configuration
        self.config = new_config
        
        # Update hash
        self.last_config_hash = new_hash
        
        # Recreate the content
        self._create_sequence_content()
        
        print(f"Sequences page refreshed")

    def _create_sequence_content(self):
        """Create or recreate the sequence content based on current configuration"""
        try:
            # If UI isn't initialized, rebuild it
            if not self.ui_initialized:
                self.create_ui_components()
            
            # Clear any existing rows
            self.clear_existing_rows()
            
            # Load configuration data
            self.load_configuration_from_config()
            
        except Exception as e:
            print(f"Error creating sequence content: {e}")
            import traceback
            traceback.print_exc()

    def load_configuration_from_config(self):
        """Load configuration data from self.config and create task rows"""
        try:
            # Make sure UI is initialized before loading configuration
            if not self.ui_initialized:
                print("UI not initialized, creating components first")
                self.create_ui_components()
                
                # Add a delay to ensure UI components are fully created
                self.after(100, lambda: self.load_configuration_from_config())
                return
            
            # Safety check - make sure config is available
            if not hasattr(self, 'config') or not isinstance(self.config, dict):
                print(f"Warning: config is not available or not a dictionary")
                self.show_warning_message()
                return
            
            # Get circuits data
            circuits_data = self.config.get("circuits", [])
            
            # Handle different formats of circuit data
            connection_summary = []
            
            if isinstance(circuits_data, list):
                # Direct list format is already the connection summary
                connection_summary = circuits_data
                print(f"Using circuits_data directly as connection_summary (list format)")
            elif isinstance(circuits_data, dict) and "connection_summary" in circuits_data:
                # Dictionary with connection_summary key
                connection_summary = circuits_data.get("connection_summary", [])
                print(f"Using connection_summary from circuits_data dictionary")
            else:
                print(f"Warning: Unexpected circuits_data format: {type(circuits_data)}")
                self.show_warning_message()
                return
            
            # If no circuit configuration, show warning and skip further loading
            if not connection_summary:
                self.clear_existing_rows()
                self.show_warning_message()
                return
            
            # Get saved sequences data
            sequences_data = self.config.get("sequences", {})
            saved_tasks = {}
            
            # Extract saved task data if available
            if isinstance(sequences_data, dict) and "sequence_configuration" in sequences_data:
                sequence_config = sequences_data["sequence_configuration"]
                if isinstance(sequence_config, dict) and "tasks" in sequence_config:
                    saved_tasks_list = sequence_config["tasks"]
                    if isinstance(saved_tasks_list, list):
                        # Create a mapping by component_id for quick lookup
                        for task in saved_tasks_list:
                            if isinstance(task, dict) and "component_id" in task:
                                saved_tasks[task["component_id"]] = task
                            elif isinstance(task, dict) and "name" in task:
                                # Fallback: use task name for mapping
                                saved_tasks[task["name"]] = task
            
            print(f"Found {len(saved_tasks)} saved tasks to restore")
            
            # Clear existing task rows
            self.clear_existing_rows()
            
            # Build pump-output mapping
            self.build_pump_output_mapping(connection_summary)
            
            # Create task rows from components - with retry mechanism
            row_num = 0
            retry_needed = False
            
            for pump_info in connection_summary:
                # Check if pump_info is a dictionary, skip if not
                if not isinstance(pump_info, dict):
                    print(f"Warning: Expected pump_info to be a dictionary, got {type(pump_info)}")
                    continue
                    
                pump_name = pump_info.get("pump_name", "Unknown Pump")
                outputs = pump_info.get("outputs", {})
                pump_index = pump_info.get("pump_index", 0)  # Get pump index
                
                # Check if outputs is a dictionary
                if not isinstance(outputs, dict):
                    print(f"Warning: Expected outputs to be a dictionary, got {type(outputs)}")
                    continue
                
                for output_num, components in outputs.items():
                    # Skip if components is not a list
                    if not isinstance(components, list):
                        print(f"Warning: Expected components to be a list, got {type(components)}")
                        continue
                        
                    for component in components:
                        # Skip if component is not a dictionary
                        if not isinstance(component, dict):
                            print(f"Warning: Expected component to be a dictionary, got {type(component)}")
                            continue
                            
                        component_name = component.get("name", "Unknown Component")
                        component_id = component.get("actual_id", "")
                        
                        # Create unique task name with pump and output info
                        task_name = f"{component_name} (P{pump_index+1}-O{output_num})"
                        
                        # Get saved values for this component
                        saved_task = saved_tasks.get(component_id) or saved_tasks.get(task_name)
                        initial_priority = "S"  # default
                        saved_duration = ""
                        saved_unit = "s"
                        
                        if saved_task:
                            initial_priority = saved_task.get("priority", "S")
                            saved_duration = str(saved_task.get("duration", ""))
                            saved_unit = saved_task.get("unit", "s")
                            print(f"Restoring task {task_name}: duration={saved_duration}{saved_unit}, priority={initial_priority}")
                        
                        # Create task row with saved or default values
                        result = self.create_task_row(
                            task_name, 
                            initial_priority, 
                            row_num, 
                            component_id, 
                            pump_index,  # Pass pump index
                            output_num,   # Pass output number
                            saved_duration,  # Pass saved duration
                            saved_unit      # Pass saved unit
                        )
                        if result is None:
                            # Task row creation failed, likely due to UI issues
                            retry_needed = True
                            break
                        row_num += 1
                    
                    if retry_needed:
                        break
                
                if retry_needed:
                    break
            
            # If any row creation failed, we'll retry after a short delay
            if retry_needed:
                print("Some task rows failed to create, retrying in 200ms...")
                self.after(200, lambda: self.load_configuration_from_config())
                return
                
            # If no components found, show warning
            if not self.task_rows:
                self.show_warning_message()
                
        except Exception as e:
            print(f"Error loading configuration data: {e}")
            import traceback
            traceback.print_exc()  # Print full traceback for debugging
            self.show_warning_message()

    def load_configuration(self, config_data=None):
        """Load configuration data and refresh the page"""
        print("Loading configuration for sequences page...")
        self.refresh_configuration()

    def build_pump_output_mapping(self, connection_summary):
        """Build mapping of pump outputs to components"""
        self.pump_output_mapping = {}
        self.component_to_pump_output = {}
        
        # Safety check for connection_summary
        if not isinstance(connection_summary, list):
            print(f"Warning: Expected connection_summary to be a list, got {type(connection_summary)}")
            return
            
        for pump_info in connection_summary:
            # Check if pump_info is a dictionary, skip if not
            if not isinstance(pump_info, dict):
                print(f"Warning: Expected pump_info to be a dictionary, got {type(pump_info)}")
                continue
                
            pump_index = pump_info.get("pump_index", 0)
            outputs = pump_info.get("outputs", {})
            
            # Check if outputs is a dictionary
            if not isinstance(outputs, dict):
                print(f"Warning: Expected outputs to be a dictionary, got {type(outputs)}")
                continue
            
            if pump_index not in self.pump_output_mapping:
                self.pump_output_mapping[pump_index] = {}
            
            for output_num, components in outputs.items():
                # Skip if components is not a list
                if not isinstance(components, list):
                    print(f"Warning: Expected components to be a list, got {type(components)}")
                    continue
                
                self.pump_output_mapping[pump_index][output_num] = []
                
                for component in components:
                    # Skip if component is not a dictionary
                    if not isinstance(component, dict):
                        print(f"Warning: Expected component to be a dictionary, got {type(component)}")
                        continue
                        
                    component_id = component.get("actual_id", "")
                    component_name = component.get("name", "")
                    
                    self.pump_output_mapping[pump_index][output_num].append(component_id)
                    self.component_to_pump_output[component_id] = {
                        "pump_index": pump_index,
                        "output": output_num
                    }

    def clear_existing_rows(self):
        """Clear existing task rows"""
        try:
            for row in self.task_rows:
                try:
                    if 'label' in row and row['label'].winfo_exists():
                        row['label'].destroy()
                    if 'entry_frame' in row and row['entry_frame'].winfo_exists():
                        row['entry_frame'].destroy()
                    if 'priority_selector' in row and row['priority_selector'].winfo_exists():
                        row['priority_selector'].destroy()
                except Exception as e:
                    print(f"Error destroying row widget: {e}")
            self.task_rows = []
        except Exception as e:
            print(f"Error clearing existing rows: {e}")
            self.task_rows = []

    def show_warning_message(self):
        """Display warning when no configuration data is available"""
        try:
            # First clear any existing content
            for widget in self.content_frame.winfo_children():
                widget.destroy()
                
            # Reset content frame to use pack layout
            self.content_frame.pack_forget()
            self.content_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
            self.content_frame.pack(fill="both", expand=True, padx=70, pady=30)
            
            # Create a centered message frame
            message_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
            message_frame.pack(expand=True, fill="both", padx=50)
            
            # Warning symbol
            warning_label = ctk.CTkLabel(
                message_frame,
                text="       ⚠️",
                font=("Arial", 48),
            )
            warning_label.pack(pady=(40, 10))
            
            # Main message
            main_message = ctk.CTkLabel(
                message_frame,
                text="No Circuit Configuration Found",
                font=self.controller.fonts.get("title", ("Arial", 24, "bold")),
            )
            main_message.pack(pady=(10, 5))
            
            # Detailed message
            detail_message = ctk.CTkLabel(
                message_frame,
                text="Please configure circuits in the previous page\nbefore setting up sequences.",
                font=self.controller.fonts.get("default", ("Arial", 14)),
                justify="center"
            )
            detail_message.pack(pady=(5, 20))
            
            # Button to go back to circuits page
            back_to_circuits_button = CustomButton(
                message_frame,
                text="Configure Circuits",
                font=self.controller.fonts.get("default", None),
                icon_path="assets/icons/back.png",
                icon_side="left",
                outlined=False,
                command=lambda: self.controller.show_page("circuits")
            )
            back_to_circuits_button.pack(pady=(10, 40))
            
        except Exception as e:
            print(f"Error displaying warning message: {e}")
            try:
                # Super simple fallback warning with minimal dependencies
                fallback_label = ctk.CTkLabel(
                    self,  # Use self instead of self.main_container
                    text="Please configure circuits first",
                    font=("Arial", 16, "bold")
                )
                fallback_label.pack(expand=True, pady=50)
            except Exception as e2:
                print(f"Fatal error displaying fallback warning: {e2}")

    def create_task_row(self, task_name, initial_priority, row_num, component_id=None, pump_index=None, output_num=None, saved_duration="", saved_unit="s"):
        """Create a row with task name and priority selector"""
        try:
            # Ensure form_frame exists and UI is properly initialized
            if not self.ui_initialized:
                print("UI not initialized, initializing UI components first...")
                self.create_ui_components()
                # We need to return here because the form_frame might not be immediately available
                # This will cause the load_configuration method to retry creating rows after UI is ready
                return None
                
            # More robust form_frame check with tkinter winfo_exists
            if not hasattr(self, 'form_frame'):
                print("Error: form_frame doesn't exist at all, recreating UI components")
                self.create_ui_components()
                return None
                
            # Ensure the widget still exists in Tkinter
            try:
                exists = self.form_frame.winfo_exists()
            except Exception:
                exists = False
                
            if not exists:
                print("Error: form_frame was destroyed or never properly created")
                self.create_ui_components()
                return None
                
            # At this point we're sure the form_frame exists, so create the task row
            # Task label
            task_label = ctk.CTkLabel(
                self.form_frame,
                text=task_name,
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
            
            # Set saved duration value if available
            if saved_duration:
                duration_entry.insert(0, saved_duration)
            
            unit_dropdown = ctk.CTkOptionMenu(
                entry_frame, 
                values=["s", "ms"], 
                font=self.controller.fonts.get("default", None),
                width=65,
                command=lambda x: None
            )
            unit_dropdown.pack(side="left", padx=(0, 10))
            unit_dropdown.set(saved_unit)  # Set saved unit value
            
            # Priority selector
            priority_selector = PrioritySelector(
                self.form_frame,
                command=lambda p, t=task_name: self.on_priority_change(t, p),
                initial_value=initial_priority
            )
            priority_selector.grid(row=row_num, column=2, padx=(5, 20), pady=(10, 0), sticky="ew")
            
            # Store references to the widgets for later access
            row_data = {
                'task_name': task_name,
                'label': task_label,
                'entry_frame': entry_frame,
                'duration_entry': duration_entry,
                'unit_dropdown': unit_dropdown,
                'priority_selector': priority_selector,
                'component_id': component_id,
                'pump_index': pump_index,
                'output_num': output_num
            }
            self.task_rows.append(row_data)
            
            return priority_selector
            
        except Exception as e:
            print(f"Error creating task row: {e}")
            import traceback
            traceback.print_exc()
            return None

    def clear_all_tasks(self):
        """Clear all task rows except the first few default ones"""
        
        # Clear values in remaining tasks
        for row in self.task_rows:
            row['duration_entry'].delete(0, 'end')
            row['priority_selector'].select('P')
            row['unit_dropdown'].set("s")
    
        
        # Clear the visualization
        self.sequence_visualizer.clear_visualization()
    
    def on_priority_change(self, task_name, new_priority):
        """Handle priority change with pump output constraints"""
        # Skip if already applying constraints
        if self.is_applying_constraints:
            return
            
        # Find the row with the matching task name
        component_id = None
        pump_index = None
        output_num = None
        
        for row in self.task_rows:
            if row['task_name'] == task_name:
                component_id = row.get('component_id')
                pump_index = row.get('pump_index')
                output_num = row.get('output_num')
                break
                
        if component_id is None or pump_index is None or output_num is None:
            # Silent return for default components
            return
        
        # Print a single message about the change
        print(f"Applying priority constraints for component on Pump {pump_index+1} Output {output_num}")
        
        # Apply priority constraints based on pump outputs
        self.apply_priority_constraints(pump_index, output_num, new_priority)

    def apply_priority_constraints(self, changed_pump_index, changed_output, new_priority):
        """Apply priority constraints based on pump output rules"""
        try:
            # Set flag to prevent recursive calls
            self.is_applying_constraints = True
            
            # Get all outputs for this pump
            pump_outputs = self.pump_output_mapping.get(changed_pump_index, {})
            
            # Find the opposite priority
            opposite_priority = "S" if new_priority == "P" else "P"
            
            # Create lists for more efficient updates
            same_output_rows = []
            other_outputs_rows = {}
            
            # Group rows by output for efficiency
            for row in self.task_rows:
                if row['pump_index'] == changed_pump_index and row['component_id'] is not None:
                    if row['output_num'] == changed_output:
                        same_output_rows.append(row)
                    elif row['output_num'] in pump_outputs:
                        if row['output_num'] not in other_outputs_rows:
                            other_outputs_rows[row['output_num']] = []
                        other_outputs_rows[row['output_num']].append(row)
            
            # Update all components in the same output to have the same priority
            for row in same_output_rows:
                row['priority_selector'].select(new_priority)
            
            # Update all components in other outputs to have the opposite priority
            for output_rows in other_outputs_rows.values():
                for row in output_rows:
                    row['priority_selector'].select(opposite_priority)
            
        except Exception as e:
            print(f"Error applying priority constraints: {e}")
        finally:
            # Clear flag when done
            self.is_applying_constraints = False

    def update_sequence(self):
        """Update the sequence based on current inputs"""
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
                task_name = row['task_name']
                pump_index = row.get('pump_index', 0)
                output_num = row.get('output_num', '1')
                
                # Convert to seconds for total calculation
                if unit == "ms":
                    duration_seconds = duration / 1000.0
                else:  # "s"
                    duration_seconds = duration
                    
                total_duration += duration_seconds
                
                # Add to tasks data for visualization with pump information
                tasks_data.append({
                    'name': task_name,
                    'duration': duration,
                    'unit': unit,
                    'priority': priority,
                    'pump_index': pump_index,
                    'output_num': output_num
                })
                
                print(f"Task: {task_name}, Duration: {duration}{unit}, Priority: {priority}, Pump: {pump_index + 1}, Output: {output_num}")
            except ValueError:
                print(f"Invalid duration for task: {row['task_name']}")
        
        # Update the sequence visualizer
        self.sequence_visualizer.update_visualization(tasks_data)
        if self.is_completed():
            self.controller.mark_page_completed("sequence")
        else:
            self.controller.mark_page_incomplete("sequence")
            self.controller.show_page("sequence")
    
    def update_appearance(self):
        """Update any appearance-dependent elements"""
        # Update the sequence visualizer appearance
        if hasattr(self, 'sequence_visualizer'):
            try:
                self.sequence_visualizer.update_appearance()
            except Exception as e:
                print(f"Error updating sequence visualizer appearance: {e}")
    
    def get_configuration(self):
        """Get the current sequence configuration"""
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
                task_name = row['task_name']
                component_id = row.get('component_id')
                pump_index = row.get('pump_index')
                output_num = row.get('output_num')
                
                # Convert to seconds for duration_seconds field
                if unit == "ms":
                    duration_seconds = duration / 1000.0
                else:  # "s"
                    duration_seconds = duration
                    
                total_duration_seconds += duration_seconds
                
                # Add task to the list
                task_data = {
                    "name": task_name,
                    "duration": duration,
                    "unit": unit,
                    "priority": priority,
                    "duration_seconds": duration_seconds,
                    "pump_index": pump_index,
                    "output_num": output_num
                }

                 # Add component mapping info if available
                if component_id:
                    task_data["component_id"] = component_id
                
                tasks_data.append(task_data)
                
            except ValueError:
                print(f"Invalid duration for task: {row['task_name']} - skipping")
        
        # Create the sequence configuration dictionary
        sequence_configuration = {
            "sequence_configuration": {
                "tasks": tasks_data,
                "total_duration_seconds": total_duration_seconds,
                "total_tasks": len(tasks_data),
            }
        }
        
        return sequence_configuration

    def save_current_configuration(self):
        """Save the configuration via the controller"""
        sequences_data = self.get_configuration()  # Ensure we have the latest configuration
        
        self.controller.update_config_data("sequences", sequences_data)

        
    def save_to_disk(self):
        """Save the current configuration to disk"""
        self.save_current_configuration()
        # Save to disk
        if self.controller.save_whole_configuration():
            messagebox.showinfo("Success", "Configuration saved successfully!")
        else:
            messagebox.showerror("Error", "Failed to save configuration!")
    
    def save_and_next(self):
        """Save configuration and navigate to the next page"""
        self.on_leave_page()  # Ensure current state is saved
        
        self.controller.show_page("results")
    
    def save_and_back(self):
        """Save configuration and navigate to the previous page"""
        self.on_leave_page()  # Ensure current state is saved
        self.controller.show_page("circuits")

    def on_leave_page(self):
        """Called when navigating away from this page"""
        # Save the current configuration
        self.save_current_configuration()
        
        # Check if the form is still complete enough to be marked as completed
        if self.is_completed():
            self.controller.mark_page_completed("sequence")
        else:
            # If it's no longer complete, mark as incomplete
            self.controller.mark_page_incomplete("sequence")
    
    def on_show_page(self):
        """Called when the page is shown"""
        # Check if the form is still complete
        if self.is_completed():
            self.controller.mark_page_completed("sequence")
        else:
            self.controller.mark_page_incomplete("sequence")

    def is_completed(self):
        """Check if the component configuration is completed"""
        # Check if there are any task rows created
        if not self.task_rows:
            return False
        
        # Check if all task rows have valid durations and priorities
        for row in self.task_rows:
            try:
                duration_text = row['duration_entry'].get()
                if not duration_text:  # Empty duration is not valid
                    return False
                    
                duration = float(duration_text)
                if duration <= 0:  # Duration must be positive
                    return False
                    
                priority = row['priority_selector'].get()
                if priority not in ["P", "S"]:  # Only allow valid priorities
                    return False
                    
            except ValueError:
                return False
        
        # If all checks passed, the configuration is complete
        return True
    
    def reset_app(self):
        """Reset the app to its initial state"""
        self.clear_all_tasks()
        self.clear_existing_rows()
        
        # Clear configuration
        self.config = {
            "washing_components": [],
            "pumps": [],
            "circuits": []
        }
        
        # Reset hash to force refresh next time
        self.last_config_hash = None
        
        # Recreate content
        self._create_sequence_content()