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
            font=self.controller.fonts.get("default", None),
            icon_path="assets/icons/next.png",
            icon_side="right",
            outlined=False,
            command=lambda: self.controller.show_page("results")
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
            command=lambda: self.controller.show_page("circuits")
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
        
        # Initialize task rows list
        self.task_rows = []
        
        # Add initial task rows
        self.create_task_row("Rinse Component A", "P", 0)
        self.create_task_row("Clean Surface B", "S", 1)
        self.create_task_row("Final Wash Cycle", "P", 2)
        
        # Add more rows to demonstrate scrolling and add button for dynamic rows
        for i in range(3, 6):
            self.create_task_row(f"Task {i+1}", "P" if i % 2 == 0 else "S", i)
        


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
            outlined=False  ,
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
    
    def add_new_task(self):
        """Add a new task row dynamically"""
        new_index = len(self.task_rows)
        task_name = f"New Task {new_index + 1}"
        
        # Create new task row
        self.create_task_row(task_name, "P", new_index)
        
    
    def clear_all_tasks(self):
        """Clear all task rows except the first few default ones"""
        
        # Clear values in remaining tasks
        for row in self.task_rows:
            row['duration_entry'].delete(0, 'end')
            row['priority_selector'].select('P')
            row['unit_dropdown'].set("s")
    
        
        # Clear the visualization
        self.sequence_visualizer.clear_visualization()
    
    def on_priority_change(self, task, priority):
        """Handle priority change"""
        print(f"Task '{task}' priority changed to: {priority}")
        # You can add any additional logic here to handle priority changes
    
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
                print(f"Invalid duration for task: {row['task_name']}")
        
        # Update the sequence visualizer
        self.sequence_visualizer.update_visualization(tasks_data)
    
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
                task_name = row['task_name']
                
                # Convert to seconds for duration_seconds field
                if unit == "ms":
                    duration_seconds = duration / 1000.0
                else:  # "s"
                    duration_seconds = duration
                    
                total_duration_seconds += duration_seconds
                
                # Add task to the list
                tasks_data.append({
                    "name": task_name,
                    "duration": duration,
                    "unit": unit,
                    "priority": priority,
                    "duration_seconds": duration_seconds
                })
                
            except ValueError:
                print(f"Invalid duration for task: {row['task_name']} - skipping")
        
        # Create the sequence configuration dictionary
        sequence_configuration = {
            "sequence_configuration": {
                "tasks": tasks_data,
                "total_duration_seconds": total_duration_seconds,
                "total_tasks": len(tasks_data)
            }
        }
        
        # Print the configuration
        print(sequence_configuration)
        
        # Also return the data in case you want to use it elsewhere
        return sequence_configuration