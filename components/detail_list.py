import customtkinter as ctk
from utils.appearance_manager import AppearanceManager

config = {
    "pump": {
        "name": "Main Pump",
        "outputs": 2,
        "washing_components_per_output": {
            1: 2,
            2: 1
        }
    },
    "washing_components": [
        "Component 1",
        "Component 2",
        "Component 3"
    ]
}


class DetailList(ctk.CTkFrame):
    def __init__(self, master, controller, width=350, config=config):
        super().__init__(master)
        self.controller = controller
        self.config = config
        ctk.set_default_color_theme("theme.json")

        # Register with AppearanceManager
        AppearanceManager.register(self)

        # Store references to widgets that need appearance updates
        self.appearance_widgets = {
            'labels': [],
            'buttons': [],
            'frames': []
        }

        def on_pump_click():
            print(f"Pump selected: {self.config['pump']}")

        def on_component_click(component_name):
            print(f"Washing component selected: {component_name}")

        # Get initial colors
        colors = self._get_appearance_colors()

        # Create main container for better layout control
        self.main_container = ctk.CTkScrollableFrame(self, width=width)
        self.main_container.pack(fill="both", expand=True)
        
        # Force the frame to maintain its dimensions
        self.pack_propagate(False)
        
        # Add a title to make the frame visible
        self.title_label = ctk.CTkLabel(
            self.main_container,
            text="Component list",
            font=controller.fonts.get("title", None),
            anchor="n",
            text_color=colors['text_color']
        )
        self.title_label.pack(pady=10)
        self.appearance_widgets['labels'].append(self.title_label)
        
        # Create pump info frame
        self.pump_info_frame = ctk.CTkFrame(
            self.main_container, 
            fg_color='transparent',
            border_color=colors['border_color'],
            border_width=1, 
            corner_radius=10
        )
        self.pump_info_frame.pack(padx=10, pady=5, fill="x")
        self.appearance_widgets['frames'].append(self.pump_info_frame)
        
        # Make the whole pump block a button
        self.pump_button = ctk.CTkButton(
            self.pump_info_frame, 
            text=f"{config['pump']['name']}\nOutputs: {config['pump']['outputs']}", 
            anchor="w",
            command=on_pump_click,
            fg_color="transparent", 
            text_color=colors['text_color'],
            hover_color=colors['hover_color'],
            border_color=colors['border_color'],
            border_width=1
        )
        self.pump_button.pack(fill="x", padx=10, pady=5)
        self.appearance_widgets['buttons'].append(self.pump_button)

        # Store output labels
        self.output_labels = []
        for output_num, num_components in config['pump']['washing_components_per_output'].items():
            output_label = ctk.CTkLabel(
                self.pump_info_frame, 
                text=f"Output {output_num}: {num_components} washing component(s)", 
                anchor="w", 
                text_color=colors['text_color']
            )
            output_label.pack(anchor="w", padx=10, pady=2)
            self.output_labels.append(output_label)
            self.appearance_widgets['labels'].append(output_label)

        # Washing Components Category
        self.washing_title = ctk.CTkLabel(
            self.main_container, 
            text="Washing components", 
            font=("Arial", 16, "bold"), 
            text_color=colors['text_color']
        )
        self.washing_title.pack(anchor="w", padx=10, pady=(20, 5))
        self.appearance_widgets['labels'].append(self.washing_title)
        
        # Store component buttons
        self.component_buttons = []
        for component in config['washing_components']:
            component_button = ctk.CTkButton(
                self.main_container, 
                text=component,
                anchor="w",
                command=lambda c=component: on_component_click(c),
                fg_color="transparent",
                text_color=colors['text_color'],
                hover_color=colors['hover_color'],
                border_color=colors['border_color'],
                border_width=1
            )
            component_button.pack(fill="x", padx=10, pady=2)
            self.component_buttons.append(component_button)
            self.appearance_widgets['buttons'].append(component_button)

    def _get_appearance_colors(self, mode=None):
        """Get colors based on appearance mode"""
        if mode is None:
            mode = ctk.get_appearance_mode()
        
        if mode == "Dark":
            return {
                'text_color': "#F8F8F8",
                'hover_color': "#12205C",
                'border_color': "#F8F8F8"
            }
        else:
            return {
                'text_color': "#0D0D0D",
                'hover_color': "#E8E8E8",
                'border_color': "#0D0D0D"
            }

    def update_appearance(self, mode=None):
        """Update appearance-dependent elements - called by AppearanceManager"""
        colors = self._get_appearance_colors(mode)
        
        # Update all labels
        for label in self.appearance_widgets['labels']:
            if label.winfo_exists():  # Check if widget still exists
                label.configure(text_color=colors['text_color'])
        
        # Update all buttons
        for button in self.appearance_widgets['buttons']:
            if button.winfo_exists():  # Check if widget still exists
                button.configure(
                    text_color=colors['text_color'], 
                    hover_color=colors['hover_color'],
                    border_color=colors['border_color']
                )
        
        # Update all frames with borders
        for frame in self.appearance_widgets['frames']:
            if frame.winfo_exists():  # Check if widget still exists
                frame.configure(border_color=colors['border_color'])

    def destroy(self):
        """Override destroy to unregister from AppearanceManager"""
        AppearanceManager.unregister(self)
        super().destroy()