import customtkinter as ctk
import tkinter
from components.custom_button import CustomButton
from utils.open_image import open_icon
from components.priority_selector import PrioritySelector

class Sequences(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        ctk.set_default_color_theme("theme.json")

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
            text="Task", 
            font=controller.fonts.get("default", None),
            text_color="#0D0D0D",
            anchor="n"
        )
        task_header.grid(row=0, column=0, pady=(10, 10), sticky="n")
        
        duration_header = ctk.CTkLabel(
            self.header_frame, 
            text="Duration", 
            font=controller.fonts.get("default", None),
            text_color="#0D0D0D",
            anchor="n"
        )
        duration_header.grid(row=0, column=1, pady=(10, 10), sticky="n")
        
        priority_header = ctk.CTkLabel(
            self.header_frame, 
            text="Priority", 
            font=controller.fonts.get("default", None), 
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
        
        # Initialize task rows list
        self.task_rows = []
        
        # Add task rows
        self.create_task_row("Rinse Component A", "P", 0)
        self.create_task_row("Clean Surface B", "S", 1)
        self.create_task_row("Final Wash Cycle", "P", 2)
        
        # Add more rows to demonstrate scrolling
        for i in range(3, 9):
            self.create_task_row(f"Task {i+1}", "P" if i % 2 == 0 else "S", i)

        # Update button - placed at bottom of form container, outside scrollable area
        self.update_button_frame = ctk.CTkFrame(
            self.form_container, 
            fg_color="transparent",
            height=60
        )
        self.update_button_frame.grid(row=2, column=0, sticky="ew", pady=(5, 10))
        
        self.update_button = CustomButton(
            self.update_button_frame,
            text="Update",
            font=controller.fonts.get("default", None),
            icon_path="assets/icons/refresh.png",
            icon_side="left",
            outlined=False,
            command=self.update_sequence,
        )
        self.update_button.pack(pady=10)

        # Graph frame for visualization
        self.graph_frame = ctk.CTkFrame(self.content_frame, fg_color="#F8F8F8")
        self.graph_frame.grid(row=0, column=1, sticky="nsew", padx=(20, 0), pady=(0, 20))

        # Total duration label
        self.duration_label = ctk.CTkLabel(
            self.content_frame, 
            text="Total washing duration: 45 sec", 
            font=controller.fonts.get("default", None),
            anchor="center"
        )
        self.duration_label.grid(row=1, column=1, padx=10, pady=10)

    def create_task_row(self, task_name, initial_priority, row_num):
        """Create a row with task name and priority selector"""
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
        
        unit_dropdown = ctk.CTkOptionMenu(
            entry_frame, 
            values=["s", "min", "h"], 
            font=self.controller.fonts.get("default", None),
            width=65,
            command=lambda x: None
        )
        unit_dropdown.pack(side="left", padx=(0, 10))
        unit_dropdown.set("s")
        
        # Priority selector
        priority_selector = PrioritySelector(
            self.form_frame,
            command=lambda p, t=task_name: self.on_priority_change(t, p),
            initial_value=initial_priority
        )
        priority_selector.grid(row=row_num, column=2, padx=(5, 20), pady=(10, 0), sticky="ew")
        
        # Store references to the widgets for later access
        self.task_rows.append({
            'task_name': task_name,
            'label': task_label,
            'entry_frame': entry_frame,
            'duration_entry': duration_entry,
            'unit_dropdown': unit_dropdown,
            'priority_selector': priority_selector
        })
        
        return priority_selector
    
    def on_priority_change(self, task, priority):
        """Handle priority change"""
        print(f"Task '{task}' priority changed to: {priority}")
        # You can add any additional logic here to handle priority changes
    
    def update_sequence(self):
        """Update the sequence based on current inputs"""
        total_duration = 0
        # Calculate total duration and update the washing sequence
        for row in self.task_rows:
            try:
                duration_text = row['duration_entry'].get()
                if not duration_text:  # Skip empty entries
                    continue
                    
                duration = float(duration_text)
                unit = row['unit_dropdown'].get()
                priority = row['priority_selector'].get()
                
                # Convert to seconds based on unit
                if unit == "min":
                    duration *= 60
                elif unit == "h":
                    duration *= 3600
                    
                total_duration += duration
                
                print(f"Task: {row['task_name']}, Duration: {duration}s, Priority: {priority}")
            except ValueError:
                print(f"Invalid duration for task: {row['task_name']}")
        
        # Update the total duration label
        self.duration_label.configure(text=f"Total washing duration: {total_duration:.1f} sec")
    
    def update_appearance(self):
        """Update any appearance-dependent elements"""
        # If you have any appearance-dependent elements, update them here
        pass

    def save_configuration(self):
        """Save the configuration via the controller"""
        print("Configuration saved!")