import customtkinter as ctk
from components.custom_button import CustomButton
from components.tabview import ThemedTabview
import tkinter as tk
import tkinter.messagebox as messagebox
from components.circuit_designer import CircuitDesigner
from components.detail_list import DetailList
from components.mode_selector import ModeSelector

class Circuits(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        ctk.set_default_color_theme("theme.json")
        
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

        # Create tabview for multiple pumps
        self.tab_view = ThemedTabview(self.content_frame)
        self.tab_view.pack(fill="both", expand=True)
        
        # Store current tab index
        self.current_tab_index = 0
        
        # Create tabs based on pump configuration
        self.tabs = []
        self.circuit_designers = []
        self.detail_lists = []
        
        # Create a shared detail list for the first pump (all tabs share component availability)
        self.shared_detail_list = None
        
        # Track all placed components globally
        self.global_placed_components = set()
        
        # Create tabs for each pump
        for i, pump_config in enumerate(self.config['pumps']):
            tab = self.tab_view.add(f"Pump {i+1}")
            self.tabs.append(tab)
            
            # Configure grid for tab
            tab.grid_rowconfigure(0, weight=1)
            tab.grid_columnconfigure(0, weight=0, minsize=350)    # Detail list column
            tab.grid_columnconfigure(1, weight=1)                 # Circuit designer column
            
            # Create detail list for this pump
            pump_specific_config = {
                "pump": pump_config,
                "washing_components": self.config['washing_components']
            }
            detail_list = DetailList(
                tab, 
                controller, 
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
            circuit_designer = CircuitDesigner(designer_frame, controller)
            circuit_designer.grid(row=0, column=0, sticky="nsew")
            self.circuit_designers.append(circuit_designer)
            
            # Connect detail list to circuit designer
            circuit_designer.set_detail_list(detail_list)
            circuit_designer.set_circuits_controller(self)
            
            # Create mode selector
            mode_selector = ModeSelector(
                designer_frame, 
                controller,
                on_mode_change=circuit_designer.set_mode
            )
            mode_selector.grid(row=1, column=0, sticky="ew")
            
            # Connect mode selector to circuit designer
            circuit_designer.mode_selector = mode_selector
        
        # Sync all detail lists to share component availability
        self._sync_detail_lists_initial()
        
        # Add synthesis tab
        synthesis_tab = self.tab_view.add("Synthesis")
        synthesis_label = ctk.CTkLabel(
            synthesis_tab, 
            text="Synthesis view will show combined circuit designs"
        )
        synthesis_label.pack(pady=20)
    
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
        

        # Default example config
        return {
            "pumps": [
                {
                    "name": "Main Pump",
                    "outputs": 2,
                    "flow_rate": 100,
                    "washing_components_per_output": {
                        1: 2,
                        2: 1
                    }
                },
                {
                    "name": "Secondary Pump",
                    "outputs": 1,
                    "flow_rate": 75,
                    "washing_components_per_output": {
                        1: 2
                    }
                }
            ],
            "washing_components": [
                {"name": "Component 1", "type": "component"},
                {"name": "Component 2", "type": "component"},
                {"name": "Component 3", "type": "component"},
                {"name": "Component 4", "type": "component"},
                {"name": "Component 5", "type": "component"},
                {"name": "Component 6", "type": "component"}
            ]
        }
    
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
    
    def update_appearance(self):
        """Update any appearance-dependent elements"""
        # Update detail lists
        for detail_list in self.detail_lists:
            if hasattr(detail_list, 'update_appearance'):
                try:
                    detail_list.update_appearance()
                except Exception as e:
                    print(f"Error updating detail list appearance: {e}")
        
        # Update circuit designers
        for designer in self.circuit_designers:
            if hasattr(designer, 'update_appearance'):
                try:
                    designer.update_appearance()
                except Exception as e:
                    print(f"Error updating circuit designer appearance: {e}")

    def save_configuration(self):
        """Save the configuration via the controller"""
        # Collect circuit data from all designers
        circuits_data = []
        for i, designer in enumerate(self.circuit_designers):
            circuit_data = designer.get_circuit_data()
            circuits_data.append({
                "pump_index": i,
                "circuit": circuit_data
            })
        print(f"Saving circuit configurations: {circuits_data}")
        # Save to controller
        if hasattr(self.controller, 'save_circuit_config'):
            self.controller.save_circuit_config(circuits_data)
        
        print("Circuit configurations saved!")
        messagebox.showinfo("Configuration Saved", "Circuit configurations have been saved successfully.")