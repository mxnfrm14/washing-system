import customtkinter as ctk
import tkinter as tk
from utils.appearance_manager import AppearanceManager

class SequenceVisualizer(ctk.CTkFrame):
    """
    Sequence visualizer component that creates a Gantt chart-style 
    visualization of washing sequences
    """
    
    def __init__(self, parent, controller, width=600, height=400, **kwargs):
        super().__init__(parent, **kwargs)
        self.controller = controller
        self.width = width
        self.height = height
        
        # Register with appearance manager
        AppearanceManager.register(self)
        
        # Task data
        self.tasks = []
        
        # Visual settings
        self.name_column_width = 150
        self.bar_height = 25
        self.spacing = 10
        self.y_start = 10
        self.padding = 20
        
        self._create_ui()
        self.update_appearance()
    
    def _create_ui(self):
        """Create the visualizer UI"""
        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text="Sequence Timeline",
            font=self.controller.fonts.get("subtitle", None) if hasattr(self.controller, 'fonts') else None,
            anchor="center"
        )
        self.title_label.pack(pady=(0, 5))
        
        # Canvas frame with border and scrollbars
        self.canvas_frame = ctk.CTkFrame(self, corner_radius=8)
        self.canvas_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Create canvas with scrollbars
        self.canvas = tk.Canvas(
            self.canvas_frame,
            bg="white",
            highlightthickness=0,
            width=self.width - 40,
            height=self.height - 40
        )
        
        # Add scrollbars
        self.v_scrollbar = tk.Scrollbar(self.canvas_frame, orient="vertical", command=self.canvas.yview)
        self.h_scrollbar = tk.Scrollbar(self.canvas_frame, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)
        
        # Pack scrollbars and canvas
        self.v_scrollbar.pack(side="right", fill="y")
        self.h_scrollbar.pack(side="bottom", fill="x")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # Total duration label
        self.duration_label = ctk.CTkLabel(
            self,
            text="Total washing duration: 0.0 ms",
            font=self.controller.fonts.get("default", None) if hasattr(self.controller, 'fonts') else None,
            anchor="center"
        )
        self.duration_label.pack(pady=(5, 0))
        
        # Initial empty state
        self._draw_empty_state()
    
    def _draw_empty_state(self):
        """Draw empty state message"""
        self.canvas.delete("all")
        canvas_width = self.canvas.winfo_reqwidth()
        canvas_height = self.canvas.winfo_reqheight()
        
        # Use default dimensions if canvas isn't mapped yet
        if canvas_width <= 1:
            canvas_width = self.width - 40
        if canvas_height <= 1:
            canvas_height = self.height - 40
        
        self.canvas.create_text(
            canvas_width // 2, canvas_height // 2,
            text="Add tasks and click 'Update' to see the sequence timeline",
            font=("Arial", 12),
            fill="gray",
            anchor="center"
        )
    
    def update_visualization(self, tasks_data):
        """
        Update the visualization with new task data
        
        Args:
            tasks_data: List of dictionaries with keys:
                - 'name': Task name
                - 'duration': Duration value (float)
                - 'unit': Time unit ('s', 'min', 'h')
                - 'priority': Priority ('P' or 'S')
        """
        self.tasks = tasks_data
        self._draw_sequence()
    
    def _draw_sequence(self):
        """Draw the sequence visualization"""
        self.canvas.delete("all")
        
        if not self.tasks:
            self._draw_empty_state()
            return
        
        # Process and sort tasks
        processed_tasks = self._process_tasks()
        
        if not processed_tasks:
            self._draw_empty_state()
            return
        
        # Get canvas dimensions
        canvas_width = self.canvas.winfo_width()
        if canvas_width <= 1:
            canvas_width = self.width - 40
        
        # Calculate dimensions
        graph_width = canvas_width - self.name_column_width - (self.padding * 2)
        total_duration = sum(task['duration_seconds'] for task in processed_tasks)
        
        if total_duration <= 0:
            self._draw_empty_state()
            return
        
        # Calculate time scale
        time_scale = graph_width / total_duration if total_duration > 0 else 1
        
        # Calculate canvas scroll region for all tasks
        content_height = len(processed_tasks) * (self.bar_height + self.spacing) + 80
        content_width = self.name_column_width + graph_width + self.padding * 2 + 50
        self.canvas.configure(scrollregion=(0, 0, content_width, content_height))
        
        # Calculate starting positions
        x_start = self.name_column_width + self.padding
        current_time = 0
        
        # Draw all tasks
        for i, task in enumerate(processed_tasks):
            y = self.y_start + i * (self.bar_height + self.spacing)
            self._draw_task(task, x_start, y, current_time, time_scale)
            current_time += task['duration_seconds']
        
        # Draw time axis
        axis_y = self.y_start + len(processed_tasks) * (self.bar_height + self.spacing) + 20
        self._draw_time_axis(x_start, processed_tasks, time_scale, axis_y)
        
        # Update duration label
        self._update_duration_label(processed_tasks)
    
    def _process_tasks(self):
        """Process and sort tasks by priority and convert units to seconds"""
        processed = []
        
        for i, task in enumerate(self.tasks):
            try:
                duration = float(task.get('duration', 0))
                if duration <= 0:
                    continue
                    
                # Convert to seconds
                unit = task.get('unit', 's')
                duration_seconds = self._convert_to_seconds(duration, unit)
                
                processed.append({
                    'name': task.get('name', f'Task {i+1}'),
                    'duration': duration,
                    'unit': unit,
                    'duration_seconds': duration_seconds,
                    'priority': task.get('priority', 'S'),
                    'original_index': i
                })
            except (ValueError, TypeError):
                continue
        
        # Sort by priority (P first) then by original index
        processed.sort(key=lambda x: (0 if x['priority'] == 'P' else 1, x['original_index']))
        
        return processed
    
    def _convert_to_seconds(self, duration, unit):
        """Convert duration to seconds"""
        if unit == 'ms':
            return duration / 1000  # Convert milliseconds to seconds
        else:  # 's' or default
            return duration
    
    def _draw_task(self, task, x_start, y, current_time, time_scale):
        """Draw a single task bar"""
        duration_seconds = task['duration_seconds']
        bar_length = duration_seconds * time_scale
        x = x_start + current_time * time_scale
        
        # Choose color based on priority
        if task['priority'] == 'P':
            bar_color = "#243783"  # Primary blue
            text_color = "#F8F8F8"  # White text
        else:
            bar_color = "#6B8AC7"  # Secondary blue
            text_color = "#F8F8F8"  # White text
        
        # Draw task name on the left
        self.canvas.create_text(
            self.name_column_width - 10, y + self.bar_height / 2,
            text=task['name'],
            anchor="e",
            font=("Arial", 10, "bold"),
            fill="black"
        )
        
        # Draw task bar
        self.canvas.create_rectangle(
            x, y, x + bar_length, y + self.bar_height,
            fill=bar_color,
            outline="#0D0D0D",
            width=1
        )
        
        # Draw duration text inside bar if there's enough space
        if bar_length > 60:
            duration_text = f"{task['duration']:.1f}{task['unit']}"
            self.canvas.create_text(
                x + bar_length / 2, y + self.bar_height / 2,
                text=duration_text,
                fill=text_color,
                font=("Arial", 9, "bold"),
                anchor="center"
            )
        
        # Draw priority indicator
        priority_x = x + bar_length + 5
        self.canvas.create_text(
            priority_x, y + self.bar_height / 2,
            text=f"({task['priority']})",
            fill="gray",
            font=("Arial", 8),
            anchor="w"
        )
    
    def _update_duration_label(self, tasks):
        """Update duration label"""
        total_duration = sum(task['duration_seconds'] for task in tasks)
        
        # Format duration appropriately
        if total_duration < 1:
            duration_text = f"Total washing duration: {total_duration * 1000:.1f} ms"
        else:
            duration_text = f"Total washing duration: {total_duration:.1f} sec"
        
        self.duration_label.configure(text=duration_text)
    
    def _draw_time_axis(self, x_start, tasks, time_scale, axis_y):
        """Draw the time axis"""
        if not tasks:
            return
            
        total_duration = sum(task['duration_seconds'] for task in tasks)
        
        # Draw main axis line
        self.canvas.create_line(
            x_start, axis_y,
            x_start + total_duration * time_scale, axis_y,
            width=2,
            fill="black"
        )
        
        # Calculate tick interval based on total duration in seconds
        if total_duration <= 0.01:  # 10ms or less
            tick_interval = 0.001  # 1ms ticks
            label_format = "{:.0f}ms"
            label_multiplier = 1000
        elif total_duration <= 0.1:  # 100ms or less
            tick_interval = 0.01  # 10ms ticks
            label_format = "{:.0f}ms"
            label_multiplier = 1000
        elif total_duration <= 1:  # 1s or less
            tick_interval = 0.1  # 100ms ticks
            label_format = "{:.0f}ms"
            label_multiplier = 1000
        elif total_duration <= 10:
            tick_interval = 1  # 1s ticks
            label_format = "{:.0f}s"
            label_multiplier = 1
        elif total_duration <= 60:
            tick_interval = 5  # 5s ticks
            label_format = "{:.0f}s"
            label_multiplier = 1
        elif total_duration <= 300:
            tick_interval = 30  # 30s ticks
            label_format = "{:.0f}s"
            label_multiplier = 1
        else:
            tick_interval = 60  # 60s ticks
            label_format = "{:.0f}s"
            label_multiplier = 1
        
        # Draw ticks and labels
        current_tick = 0
        while current_tick <= total_duration:
            x = x_start + current_tick * time_scale
            
            # Draw tick mark
            self.canvas.create_line(
                x, axis_y - 5, x, axis_y + 5,
                width=1,
                fill="black"
            )
            
            # Draw label with appropriate format
            label_value = current_tick * label_multiplier
            self.canvas.create_text(
                x, axis_y + 15,
                text=label_format.format(label_value),
                font=("Arial", 9),
                fill="black",
                anchor="center"
            )
            
            current_tick += tick_interval
    
    def clear_visualization(self):
        """Clear the visualization"""
        self.tasks = []
        self._draw_empty_state()
        self.duration_label.configure(text="Total washing duration: 0.0 ms")
    
    def update_appearance(self, mode=None):
        """Update appearance based on theme"""
        # Update canvas background
        bg_color = "#F8F8F8" if ctk.get_appearance_mode() == "Dark" else "white"
        if hasattr(self, 'canvas'):
            self.canvas.configure(bg=bg_color)
        
        # Update title color
        text_color = "#F8F8F8" if ctk.get_appearance_mode() == "Dark" else "#0D0D0D"
        if hasattr(self, 'title_label'):
            self.title_label.configure(text_color=text_color)
        if hasattr(self, 'duration_label'):
            self.duration_label.configure(text_color=text_color)
        
        # Redraw with new colors
        if self.tasks:
            self._draw_sequence()
    
    def destroy(self):
        """Clean up when destroying"""
        AppearanceManager.unregister(self)
        super().destroy()