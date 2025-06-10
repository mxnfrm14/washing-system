import customtkinter as ctk
from utils.appearance_manager import AppearanceManager

class DetailList(ctk.CTkFrame):
    """Component list for circuit designer"""
    
    def __init__(self, master, controller, width=350, config=None, on_component_select=None):
        super().__init__(master)
        self.controller = controller
        self.config = config or self._get_default_config()
        self.on_component_select = on_component_select
        ctk.set_default_color_theme("theme.json")

        # Register with AppearanceManager
        AppearanceManager.register(self)

        # Store references to widgets that need appearance updates
        self.appearance_widgets = {
            'labels': [],
            'buttons': [],
            'frames': []
        }
        
        # Track selected component
        self.selected_component = None
        self.selected_button = None
        
        # Track placed components across all tabs
        self.placed_components = set()  # Set of component names that are placed
        self.component_buttons_map = {}  # Map component name to button

        # Get initial colors
        colors = self._get_appearance_colors()

        # Create main container
        self.main_container = ctk.CTkScrollableFrame(self, width=width)
        self.main_container.pack(fill="both", expand=True)
        
        # Force the frame to maintain its dimensions
        self.pack_propagate(False)
        
        # Title
        self.title_label = ctk.CTkLabel(
            self.main_container,
            text="Components",
            font=controller.fonts.get("title", None),
            anchor="n",
            text_color=colors['text_color']
        )
        self.title_label.pack(pady=10)
        self.appearance_widgets['labels'].append(self.title_label)
        
        # Create sections
        self._create_pump_section(colors)
        self._create_washing_components_section(colors)
    
    def _get_default_config(self):
        """Get default configuration if none provided"""
        return {
            "pump": {
                "name": "Main Pump",
                "outputs": 2,
                "flow_rate": 100,
                "washing_components_per_output": {
                    1: 2,
                    2: 1
                }
            },
            "washing_components": [
                {"name": "Component 1", "type": "component"},
                {"name": "Component 2", "type": "component"},
                {"name": "Component 3", "type": "component"}
            ]
        }
    
    def _create_pump_section(self, colors):
        """Create pump section"""
        # Pump header
        pump_header = ctk.CTkLabel(
            self.main_container,
            text="Pump",
            font=self.controller.fonts.get("subtitle", None),
            text_color=colors['text_color']
        )
        pump_header.pack(anchor="w", padx=10, pady=(20, 5))
        self.appearance_widgets['labels'].append(pump_header)
        
        # Check if pump data is available
        if not self.config.get('pump') or not self.config['pump'].get('name'):
            # Show message for no pumps
            no_pump_label = ctk.CTkLabel(
                self.main_container,
                text="No pump configured for this tab.",
                font=self.controller.fonts.get("default", None),
                text_color="#FF6B6B",  # Red color for warning
                justify="left"
            )
            no_pump_label.pack(anchor="w", padx=20, pady=10)
            self.appearance_widgets['labels'].append(no_pump_label)
            return
        
        # Pump info frame
        self.pump_info_frame = ctk.CTkFrame(
            self.main_container,
            fg_color='transparent',
            border_color=colors['border_color'],
            border_width=1,
            corner_radius=10
        )
        self.pump_info_frame.pack(padx=10, pady=5, fill="x")
        self.appearance_widgets['frames'].append(self.pump_info_frame)
        
        # Pump button
        pump_data = {
            "type": "pump", 
            "id": self.config['pump'].get('id', 'pump_0'),  # Use unique ID
            "name": self.config['pump']['name'], 
            "display_name": self.config['pump'].get('display_name', self.config['pump']['name']),  # Use display name
            "max_connections": self.config['pump']['outputs'],  # Use outputs as max connections
            "properties": self.config['pump']
        }
        self.pump_button = ctk.CTkButton(
            self.pump_info_frame,
            text=f"{pump_data['display_name']}\nOutputs: {self.config['pump']['outputs']}",
            anchor="w",
            command=lambda: self._on_component_click(pump_data, self.pump_button),
            fg_color="transparent",
            text_color=colors['text_color'],
            hover_color=colors['hover_color'],
            border_color=colors['border_color'],
            border_width=1,
            font=self.controller.fonts.get("default", None),
        )
        self.pump_button.pack(fill="x", padx=10, pady=5)
        self.appearance_widgets['buttons'].append(self.pump_button)
        
        # Store pump button in map using unique ID
        self.component_buttons_map[self.config['pump'].get('id', 'pump_0')] = self.pump_button

        # Output labels
        self.output_labels = []
        for output_num, num_components in self.config['pump'].get('washing_components_per_output', {}).items():
            output_label = ctk.CTkLabel(
                self.pump_info_frame,
                text=f"Output {output_num}: {num_components} components",
                anchor="w",
                text_color=colors['text_color'],
                font=self.controller.fonts.get("default", None)
            )
            output_label.pack(anchor="w", padx=20, pady=2)
            self.output_labels.append(output_label)
            self.appearance_widgets['labels'].append(output_label)
    
    def _create_washing_components_section(self, colors):
        """Create washing components section"""
        # Washing Components header
        washing_header = ctk.CTkLabel(
            self.main_container,
            text="Components",
            font=self.controller.fonts.get("subtitle", None),
            text_color=colors['text_color']
        )
        washing_header.pack(anchor="w", padx=10, pady=(20, 5))
        self.appearance_widgets['labels'].append(washing_header)
        
        # Check if washing components are available
        washing_components = self.config.get('washing_components', [])
        if not washing_components:
            # Show message for no components
            no_components_label = ctk.CTkLabel(
                self.main_container,
                text="No washing components configured.\nPlease configure components in the previous page.",
                font=self.controller.fonts.get("default", None),
                text_color="#FF6B6B",  # Red color for warning
                justify="left"
            )
            no_components_label.pack(anchor="w", padx=20, pady=10)
            self.appearance_widgets['labels'].append(no_components_label)
            return
        
        # Component buttons
        self.component_buttons = []
        for component in washing_components:
            # Ensure component is a dict
            if isinstance(component, str):
                component = {"name": component, "type": "component"}
            
            # Add unique ID and display name if not present
            if 'id' not in component:
                component['id'] = f"component_{len(self.component_buttons)}"
            if 'display_name' not in component:
                component['display_name'] = component.get('name', 'Unknown')
            
            comp_button = ctk.CTkButton(
                self.main_container,
                text=component.get('display_name', 'Unknown'),
                anchor="w",
                command=lambda c=component, b=None: self._on_component_click(c, b),
                fg_color="transparent",
                text_color=colors['text_color'],
                hover_color=colors['hover_color'],
                border_color=colors['border_color'],
                border_width=1,
                font=self.controller.fonts.get("default", None),
            )
            comp_button.pack(fill="x", padx=10, pady=2)
            # Update lambda to pass button reference
            comp_button.configure(command=lambda c=component, b=comp_button: self._on_component_click(c, b))
            self.component_buttons.append(comp_button)
            self.appearance_widgets['buttons'].append(comp_button)
            
            # Store in map using unique ID
            self.component_buttons_map[component.get('id', 'unknown')] = comp_button
    
    def _on_component_click(self, component, button):
        """Handle component selection"""
        # Check if component is already placed using unique ID
        component_id = component.get('id', '')
        if component_id in self.placed_components:
            print(f"Component {component.get('display_name', 'Unknown')} is already placed")
            return
        
        # Update visual selection
        self._update_selection(button)
        
        # Store selected component
        self.selected_component = component
        
        # Notify callback
        if self.on_component_select:
            self.on_component_select(component)
        
        print(f"Component selected: {component.get('display_name', 'Unknown')} - switching to place mode")
    
    def _update_selection(self, selected_button):
        """Update visual selection state"""
        # Don't allow selection of placed components
        if selected_button:
            # Find component ID
            component_id = None
            if selected_button == self.pump_button:
                component_id = self.config['pump'].get('id', 'pump_0')
            else:
                for comp_id, btn in self.component_buttons_map.items():
                    if btn == selected_button:
                        component_id = comp_id
                        break
            
            # Check if component is already placed
            if component_id and component_id in self.placed_components:
                return  # Don't select placed components
        
        colors = self._get_appearance_colors()
        
        # Reset previous selection
        if self.selected_button and self.selected_button != selected_button:
            # Only reset if not placed
            component_id = None
            if self.selected_button == self.pump_button:
                component_id = self.config['pump'].get('id', 'pump_0')
            else:
                for comp_id, btn in self.component_buttons_map.items():
                    if btn == self.selected_button:
                        component_id = comp_id
                        break
            
            if component_id not in self.placed_components:
                self.selected_button.configure(
                    fg_color="transparent",
                    border_color=colors['border_color']
                )
        
        # Highlight new selection
        if selected_button:
            self.selected_button = selected_button
            selected_button.configure(
                fg_color=colors['selected_bg'],
                border_color=colors['selected_border']
            )
    
    def _get_appearance_colors(self, mode=None):
        """Get colors based on appearance mode"""
        if mode is None:
            mode = ctk.get_appearance_mode()
        
        if mode == "Dark":
            return {
                'text_color': "#F8F8F8",
                'hover_color': "#12205C",
                'border_color': "#F8F8F8",
                'selected_bg': "#243783",
                'selected_border': "#4A90E2"
            }
        else:
            return {
                'text_color': "#0D0D0D",
                'hover_color': "#E8E8E8",
                'border_color': "#0D0D0D",
                'selected_bg': "#E3E7FF",
                'selected_border': "#243783"
            }

    def update_appearance(self, mode=None):
        """Update appearance-dependent elements"""
        colors = self._get_appearance_colors(mode)
        
        # Update all labels
        for label in self.appearance_widgets['labels']:
            if label.winfo_exists():
                label.configure(text_color=colors['text_color'])
        
        # Update all buttons
        for button in self.appearance_widgets['buttons']:
            if button.winfo_exists():
                # Get component name to check if it's placed
                component_name = None
                if button == self.pump_button:
                    component_name = self.config['pump']['name']
                else:
                    # Find component name from button
                    for name, btn in self.component_buttons_map.items():
                        if btn == button:
                            component_name = name
                            break
                
                # Check if component is placed
                if component_name and component_name in self.placed_components:
                    # Keep disabled state
                    button.configure(
                        state="disabled",
                        fg_color="gray70",
                        text_color="gray40",
                        hover_color="gray70"
                    )
                elif button == self.selected_button:
                    button.configure(
                        text_color=colors['text_color'],
                        hover_color=colors['hover_color'],
                        border_color=colors['selected_border'],
                        fg_color=colors['selected_bg']
                    )
                else:
                    button.configure(
                        text_color=colors['text_color'],
                        hover_color=colors['hover_color'],
                        border_color=colors['border_color'],
                        fg_color="transparent"
                    )
        
        # Update all frames with borders
        for frame in self.appearance_widgets['frames']:
            if frame.winfo_exists():
                frame.configure(border_color=colors['border_color'])
    
    def get_selected_component(self):
        """Get currently selected component"""
        return self.selected_component
    
    def clear_selection(self):
        """Clear current selection"""
        if self.selected_button:
            # Only clear if the component is not placed
            component_name = None
            if self.selected_button == self.pump_button:
                component_name = self.config['pump']['name']
            else:
                for name, btn in self.component_buttons_map.items():
                    if btn == self.selected_button:
                        component_name = name
                        break
            
            # Only reset appearance if not placed
            if component_name not in self.placed_components:
                colors = self._get_appearance_colors()
                self.selected_button.configure(
                    fg_color="transparent",
                    border_color=colors['border_color']
                )
            
            self.selected_button = None
            self.selected_component = None

    def destroy(self):
        """Override destroy to unregister from AppearanceManager"""
        AppearanceManager.unregister(self)
        super().destroy()
    
    def mark_component_placed(self, component_id):
        """Mark a component as placed and disable its button using unique ID"""
        if component_id in self.component_buttons_map:
            self.placed_components.add(component_id)
            button = self.component_buttons_map[component_id]
            # Disable the button
            button.configure(
                state="disabled",
                fg_color="gray70",
                text_color="gray40",
                hover_color="gray70"
            )
            print(f"Component {component_id} marked as placed")
    
    def mark_component_available(self, component_id):
        """Mark a component as available and enable its button using unique ID"""
        if component_id in self.placed_components:
            self.placed_components.remove(component_id)
        
        if component_id in self.component_buttons_map:
            button = self.component_buttons_map[component_id]
            colors = self._get_appearance_colors()
            # Re-enable the button
            button.configure(
                state="normal",
                fg_color="transparent",
                text_color=colors['text_color'],
                hover_color=colors['hover_color']
            )
            print(f"Component {component_id} marked as available")
    
    def reset_all_components(self):
        """Reset all components to available state"""
        for component_id in list(self.placed_components):
            self.mark_component_available(component_id)
        self.placed_components.clear()