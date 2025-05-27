import customtkinter as ctk
from utils.appearance_manager import AppearanceManager
from utils.open_image import open_icon

class ModeSelector(ctk.CTkFrame):
    """Mode selector with connector placement buttons and action modes"""
    
    def __init__(self, parent, controller, on_mode_change=None, **kwargs):
        # Remove height from kwargs if present to prevent it from being passed downstream
        if 'height' in kwargs:
            self._height = kwargs.pop('height')
        else:
            self._height = 50  # Default height
            
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.controller = controller
        self.on_mode_change = on_mode_change
        self.current_mode = "move"  # Default mode
        self.selected_connector = None
        
        # Register with appearance manager
        AppearanceManager.register(self)
        
        # Define modes (no place mode - it's automatic)
        self.modes = {
            "move": {
                "name": "Move",
                "icon": "assets/icons/move.png",
                "tooltip": "Move components"
            },
            "connect": {
                "name": "Connect",
                "icon": "assets/icons/link.png",
                "tooltip": "Connect components"
            },
            "delete": {
                "name": "Delete",
                "icon": "assets/icons/trash.png",
                "tooltip": "Delete components"
            }
        }
        
        # Connector types
        self.connector_types = {
            "t_connector": {
                "name": "T",
                "full_name": "T-Connector",
                "icon": "assets/icons/connector_t.png",
                "type": "connector",
                "subtype": "t_connector"
            },
            "y_connector": {
                "name": "Y", 
                "full_name": "Y-Connector",
                "icon": "assets/icons/connector_y.png",
                "type": "connector",
                "subtype": "y_connector"
            },
            "straight_connector": {
                "name": "S",
                "full_name": "Straight Connector",
                "icon": "assets/icons/connector_s.png",
                "type": "connector",
                "subtype": "straight_connector"
            }
        }
        
        self.mode_buttons = {}
        self.connector_buttons = {}
        
        self._create_ui()
        self.update_appearance()
    
    def _create_ui(self):
        """Create the mode selector UI"""
        # Main container
        self.main_frame = ctk.CTkFrame(self, height=self._height)
        self.main_frame.pack(fill="x", padx=5, pady=5)
        self.main_frame.pack_propagate(False)
        
        # Configure grid
        self.main_frame.grid_columnconfigure(0, weight=1)  # Left side - connectors
        self.main_frame.grid_columnconfigure(1, weight=0)  # Separator
        self.main_frame.grid_columnconfigure(2, weight=1)  # Right side - modes
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        # Left section - Connector buttons
        self.connectors_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.connectors_frame.grid(row=0, column=0, sticky="w", padx=10)
        
        connector_label = ctk.CTkLabel(
            self.connectors_frame,
            text="Connectors:",
            font=self.controller.fonts.get("default", None),
            text_color="#F8F8F8"
        )
        connector_label.pack(side="left", padx=(0, 10))
        
        # Create connector buttons
        for conn_key, conn_info in self.connector_types.items():
            btn_frame = ctk.CTkFrame(self.connectors_frame, fg_color="transparent")
            btn_frame.pack(side="left", padx=5)
            
            # Load icon
            icon = open_icon(conn_info["icon"], size=(30, 30), tint_color="#FFFFFF")
            
            # Create button - fixed height
            btn = ctk.CTkButton(
                btn_frame,
                text="",
                image=icon,
                width=45,
                height=45,  # Keep explicit height for buttons
                corner_radius=6,
                border_width=0,
                command=lambda c=conn_key: self.select_connector(c)
            )
            btn.pack()
            
            # Store button reference
            self.connector_buttons[conn_key] = btn
            
            # Add tooltip with full name
            label = ctk.CTkLabel(
                btn_frame,
                text=conn_info["full_name"],
                font=("Encode Sans Expanded", 9),
                text_color="#F8F8F8"
            )
            label.pack()
        
        # Separator
        separator = ctk.CTkFrame(self.main_frame, width=2, height=15, fg_color="#F8F8F8")
        separator.grid(row=0, column=1, sticky="ns", padx=10)
        
        # Right section - Mode buttons
        self.modes_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.modes_frame.grid(row=0, column=2, sticky="e", padx=10)
        
        mode_label = ctk.CTkLabel(
            self.modes_frame,
            text="Mode:",
            font=self.controller.fonts.get("default", None),
            text_color="#F8F8F8"
        )
        mode_label.pack(side="left", padx=(0, 10))
        
        # Create mode buttons
        for mode_key, mode_info in self.modes.items():
            btn_frame = ctk.CTkFrame(self.modes_frame, fg_color="transparent")
            btn_frame.pack(side="left", padx=5)
            
            # Load icon
            icon = open_icon(mode_info["icon"], size=(24, 24), tint_color="#FFFFFF")
            
            # Create button
            btn = ctk.CTkButton(
                btn_frame,
                text="",
                image=icon,
                width=45,
                height=45,
                corner_radius=6,
                border_width=0,
                command=lambda m=mode_key: self.set_mode(m)
            )
            btn.pack()
            
            # Store button reference
            self.mode_buttons[mode_key] = btn
            
            # Add tooltip (as label below for now)
            tooltip = ctk.CTkLabel(
                btn_frame,
                text=mode_info["name"],
                font=("Encode Sans Expanded", 10),
                text_color="#F8F8F8"
            )
            tooltip.pack()
        
        # Set initial mode
        self.set_mode(self.current_mode)
    
    def select_connector(self, connector_key):
        """Select a connector and switch to place mode"""
        if connector_key not in self.connector_types:
            return
        
        self.selected_connector = connector_key
        
        # Update visual states
        self._update_button_states()
        
        # Automatically switch to place mode and notify
        if self.on_mode_change:
            connector_data = self.connector_types[connector_key].copy()
            connector_data["name"] = connector_data.get("full_name", connector_data["name"])
            mode_data = {
                "mode": "place",
                "component": connector_data
            }
            self.on_mode_change(mode_data)
    
    def set_mode(self, mode):
        """Set the current mode and update UI"""
        if mode not in self.modes and mode != "place":
            return
        
        # Only update if it's a valid mode button
        if mode in self.modes:
            self.current_mode = mode
            self._update_button_states()
        
        # Notify callback
        if self.on_mode_change:
            mode_data = {
                "mode": mode,
                "component": None
            }
            self.on_mode_change(mode_data)
    
    def _update_button_states(self):
        """Update visual states of buttons"""
        colors = self._get_colors()
        
        # Update mode buttons
        for mode_key, btn in self.mode_buttons.items():
            if mode_key == self.current_mode:
                btn.configure(
                    fg_color=colors["selected_bg"],
                    hover_color=colors["selected_hover"]
                )
            else:
                btn.configure(
                    fg_color=colors["unselected_bg"],
                    hover_color=colors["unselected_hover"]
                )
        
        # Update connector buttons (visual feedback when selected)
        for conn_key, btn in self.connector_buttons.items():
            if self.selected_connector == conn_key:
                btn.configure(
                    fg_color=colors["connector_selected"],
                    hover_color=colors["connector_hover"]
                )
            else:
                btn.configure(
                    fg_color=colors["unselected_bg"],
                    hover_color=colors["unselected_hover"]
                )
    
    def _get_colors(self):
        """Get theme colors based on appearance mode"""
        mode = ctk.get_appearance_mode()
        
        if mode == "Dark":
            return {
                "selected_bg": "#1A296C",
                "selected_hover": "#2F4590",
                "unselected_bg": "#243783",
                "unselected_hover": "#2F4590",
                "connector_selected": "#1A296C",
                "connector_hover": "#2F4590"
            }
        else:
            return {
                "selected_bg": "#1A296C",
                "selected_hover": "#2F4590",
                "unselected_bg": "#243783",
                "unselected_hover": "#2F4590",
                "connector_selected": "#1A296C",
                "connector_hover": "#2F4590"
            }
    
    def update_appearance(self, mode=None):
        """Update appearance based on theme"""
        self._update_button_states()
        
        # Update frame colors
        colors = self._get_colors()
        if hasattr(self, 'main_frame'):
            bg_color = "#243783" if ctk.get_appearance_mode() == "Dark" else "#243783"
            self.main_frame.configure(fg_color=bg_color)
    
    def get_current_mode(self):
        """Get current mode and settings"""
        return {
            "mode": self.current_mode,
            "component": None
        }
    
    def clear_connector_selection(self):
        """Clear connector selection"""
        self.selected_connector = None
        self._update_button_states()
    
    def destroy(self):
        """Clean up when destroying"""
        AppearanceManager.unregister(self)
        super().destroy()