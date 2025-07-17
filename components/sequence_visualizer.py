import customtkinter as ctk
import tkinter as tk
from utils.appearance_manager import AppearanceManager

class SequenceVisualizer(ctk.CTkFrame):
    """
    Sequence visualizer component that creates a Gantt chart-style 
    visualization of washing sequences with parallel pump support
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
        self.name_column_width = 170  # Increased to accommodate output indicators
        self.bar_height = 25
        self.spacing = 10
        self.y_start = 10
        self.padding = 20
        
        # Pump colors for differentiation
        self.pump_colors = [
            "#6B8AC7",  # Secondary blue
            "#4CAF50",  # Green
            "#FF9800",  # Orange
            "#9C27B0",  # Purple
            "#F44336",  # Red
            "#00BCD4",  # Cyan
            "#795548",  # Brown
        ]
        
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
        self.title_label.pack(pady=(0, 1))
        
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
        
        # Pump legend
        self.legend_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.legend_frame.pack(pady=(1, 0))
        
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
        Update the visualization with new task data supporting parallel execution
        
        Args:
            tasks_data: List of dictionaries with keys:
                - 'name': Task name
                - 'duration': Duration value (float)
                - 'unit': Time unit ('s', 'min', 'h')
                - 'priority': Priority ('P' or 'S')
                - 'pump_index': Index of the pump (for parallel execution)
                - 'output_num': Output number of the pump
        """
        self.tasks = tasks_data
        self._draw_parallel_sequence()
    
    def _draw_parallel_sequence(self):
        """Draw the parallel sequence visualization in staggered layout"""
        self.canvas.delete("all")
        
        if not self.tasks:
            self._draw_empty_state()
            return
        
        # Process and group tasks by pump
        pump_tracks = self._group_tasks_by_pump()
        
        if not pump_tracks:
            self._draw_empty_state()
            return
        
        # Calculate parallel execution timeline
        timeline_data = self._calculate_parallel_timeline(pump_tracks)
        
        # Get canvas dimensions
        canvas_width = self.canvas.winfo_width()
        if canvas_width <= 1:
            canvas_width = self.width - 40
        
        # Calculate dimensions
        graph_width = canvas_width - self.name_column_width - (self.padding * 2)
        total_duration = timeline_data['total_duration']
        
        if total_duration <= 0:
            self._draw_empty_state()
            return
        
        # Calculate time scale
        time_scale = graph_width / total_duration if total_duration > 0 else 1
        
        # Create unified timeline for staggered display
        unified_timeline = self._create_unified_timeline(timeline_data['pump_timelines'])
        
        # Calculate canvas scroll region
        num_tasks = len(unified_timeline)
        content_height = num_tasks * (self.bar_height + self.spacing) + 120
        content_width = self.name_column_width + graph_width + self.padding * 2 + 50
        self.canvas.configure(scrollregion=(0, 0, content_width, content_height))
        
        # Draw tasks in staggered layout
        x_start = self.name_column_width + self.padding
        
        for i, task_info in enumerate(unified_timeline):
            y_position = self.y_start + i * (self.bar_height + self.spacing)
            self._draw_staggered_task(
                task_info,
                x_start,
                y_position,
                time_scale
            )
        
        # Draw time axis
        axis_y = self.y_start + num_tasks * (self.bar_height + self.spacing) + 20
        self._draw_time_axis(x_start, total_duration, time_scale, axis_y)
        
        # Update duration label and legend
        self._update_duration_label(total_duration)
        self._update_pump_legend(pump_tracks)
    
    def _group_tasks_by_pump(self):
        """Group tasks by pump and process them"""
        pump_tracks = {}
        
        for task in self.tasks:
            try:
                duration = float(task.get('duration', 0))
                if duration <= 0:
                    continue
                
                # Get pump information
                pump_index = task.get('pump_index', 0)
                output_num = task.get('output_num', '1')
                
                # Convert to seconds
                unit = task.get('unit', 's')
                duration_seconds = self._convert_to_seconds(duration, unit)
                
                processed_task = {
                    'name': task.get('name', 'Unknown Task'),
                    'duration': duration,
                    'unit': unit,
                    'duration_seconds': duration_seconds,
                    'priority': task.get('priority', 'S'),
                    'pump_index': pump_index,
                    'output_num': output_num,
                    'original_index': len(pump_tracks.get(pump_index, {}).get('tasks', []))
                }
                
                # Initialize pump track if not exists
                if pump_index not in pump_tracks:
                    pump_tracks[pump_index] = {
                        'pump_index': pump_index,
                        'pump_name': f'Pump {pump_index + 1}',
                        'tasks': [],
                        'total_duration': 0
                    }
                
                pump_tracks[pump_index]['tasks'].append(processed_task)
                
            except (ValueError, TypeError):
                continue
        
        # Sort tasks within each pump by priority first, then output, then original index
        for track_data in pump_tracks.values():
            track_data['tasks'].sort(key=lambda x: (
                0 if x['priority'] == 'P' else 1,  # Priority first (P before S)
                str(x['output_num']),  # Then by output
                x['original_index']  # Then by original order
            ))
        
        return pump_tracks
    
    def _calculate_parallel_timeline(self, pump_tracks):
        """Calculate timeline for parallel execution with priority-based output ordering"""
        pump_timelines = {}
        max_duration = 0
        
        for pump_index, track_data in pump_tracks.items():
            # Group tasks by output within this pump
            output_groups = {}
            for task in track_data['tasks']:
                output_num = task['output_num']
                if output_num not in output_groups:
                    output_groups[output_num] = []
                output_groups[output_num].append(task)
            
            # Determine priority for each output (highest priority task in that output)
            output_priorities = {}
            for output_num, tasks in output_groups.items():
                # Find the highest priority in this output (P is higher than S)
                has_priority_p = any(task['priority'] == 'P' for task in tasks)
                output_priorities[output_num] = 0 if has_priority_p else 1
            
            # Sort outputs by their priority, then by output number
            sorted_outputs = sorted(output_groups.keys(), key=lambda x: (output_priorities[x], str(x)))
            
            # Calculate timeline for this pump with priority-based output ordering
            current_time = 0
            pump_timeline = []
            
            # Process outputs in priority order
            for output_num in sorted_outputs:
                output_tasks = output_groups[output_num]
                
                # All tasks in the same output start at the same time
                output_start_time = current_time
                output_max_duration = 0
                
                for task in output_tasks:
                    pump_timeline.append({
                        'task': task,
                        'start_time': output_start_time,
                        'end_time': output_start_time + task['duration_seconds'],
                        'output_num': output_num
                    })
                    # Track the longest task in this output
                    output_max_duration = max(output_max_duration, task['duration_seconds'])
                
                # Next output starts after the longest task in current output finishes
                current_time = output_start_time + output_max_duration
            
            pump_timelines[pump_index] = pump_timeline
            max_duration = max(max_duration, current_time)
        
        return {
            'pump_timelines': pump_timelines,
            'total_duration': max_duration
        }
    
    def _create_unified_timeline(self, pump_timelines):
        """Create a unified timeline for staggered display with output grouping"""
        # Group tasks by start time and pump/output combination
        time_groups = {}
        
        for pump_index, timeline in pump_timelines.items():
            for task_info in timeline:
                start_time = task_info['start_time']
                output_num = task_info['output_num']
                
                # Create a unique key for each pump-output-time combination
                group_key = (start_time, pump_index, output_num)
                
                if group_key not in time_groups:
                    time_groups[group_key] = []
                
                task_data = task_info['task'].copy()
                task_data.update({
                    'start_time': task_info['start_time'],
                    'end_time': task_info['end_time'],
                    'pump_index': pump_index,
                    'output_num': output_num
                })
                time_groups[group_key].append(task_data)
        
        # Sort groups by start time, then by pump index, then by output
        sorted_groups = sorted(time_groups.items(), key=lambda x: (x[0][0], x[0][1], x[0][2]))
        
        # Flatten the groups to create the final timeline
        unified_timeline = []
        for (start_time, pump_index, output_num), tasks in sorted_groups:
            # Sort tasks within the same group by priority (P first)
            tasks.sort(key=lambda x: (0 if x['priority'] == 'P' else 1, x['name']))
            unified_timeline.extend(tasks)
        
        return unified_timeline
    
    def _draw_staggered_task(self, task_info, x_start, y, time_scale):
        """Draw a single task in staggered layout"""
        start_time = task_info['start_time']
        duration_seconds = task_info['duration_seconds']
        pump_index = task_info['pump_index']
        output_num = task_info['output_num']
        
        # Calculate position and size
        x = x_start + start_time * time_scale
        bar_length = duration_seconds * time_scale
        
        # Get pump color
        pump_color = self.pump_colors[pump_index % len(self.pump_colors)]
        text_color = "#F8F8F8"  # White text for all pumps
        
        # Clean component name (remove pump info from display)
        task_name = task_info['name']
        # Remove pump info like "(P1-O1)" from the end if present
        if '(' in task_name and task_name.endswith(')'):
            clean_name = task_name.split('(')[0].strip()
        else:
            clean_name = task_name
        
        # Draw component name on the left
        self.canvas.create_text(
            self.name_column_width - 10, y + self.bar_height / 2,
            text=clean_name,
            anchor="e",
            font=("Arial", 10, "bold"),
            fill="black"
        )
        
        # Draw task bar with slight transparency effect for stacked appearance
        self.canvas.create_rectangle(
            x, y, x + bar_length, y + self.bar_height,
            fill=pump_color,
            outline="#0D0D0D",
            width=1
        )
        
        # Draw duration text inside bar if there's enough space
        if bar_length > 60:
            duration_text = f"{task_info['duration']:.1f}{task_info['unit']}"
            self.canvas.create_text(
                x + bar_length / 2, y + self.bar_height / 2,
                text=duration_text,
                fill=text_color,
                font=("Arial", 9, "bold"),
                anchor="center"
            )
        
        # Draw output indicator on the left edge of the bar
        output_indicator_x = x - 15
        self.canvas.create_text(
            output_indicator_x, y + self.bar_height / 2,
            text=f"O{output_num}",
            fill=pump_color,
            font=("Arial", 8, "bold"),
            anchor="center"
        )
        
        # Draw priority indicator
        priority_x = x + bar_length + 5
        self.canvas.create_text(
            priority_x, y + self.bar_height / 2,
            text=f"({task_info['priority']})",
            fill="gray",
            font=("Arial", 8),
            anchor="w"
        )
    
    def _convert_to_seconds(self, duration, unit):
        """Convert duration to seconds"""
        if unit == 'ms':
            return duration / 1000  # Convert milliseconds to seconds
        else:  # 's' or default
            return duration
    
    def _draw_time_axis(self, x_start, total_duration, time_scale, axis_y):
        """Draw the time axis"""
        if total_duration <= 0:
            return
            
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
            tick_interval = 0.2  # 200ms ticks
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
    
    def _update_duration_label(self, total_duration):
        """Update duration label"""
        # Format duration appropriately
        if total_duration < 1:
            duration_text = f"Total washing duration: {total_duration * 1000:.1f} ms"
        else:
            duration_text = f"Total washing duration: {total_duration:.1f} sec"
        
        self.duration_label.configure(text=duration_text)
    
    def _update_pump_legend(self, pump_tracks):
        """Update pump legend with colors"""
        # Clear existing legend
        for widget in self.legend_frame.winfo_children():
            widget.destroy()
        
        if len(pump_tracks) <= 1:
            return  # No need for legend with single pump
        
        # Center the legend content
        legend_container = ctk.CTkFrame(self.legend_frame, fg_color="transparent")
        legend_container.pack()
        
        legend_title = ctk.CTkLabel(
            legend_container,
            text="Pumps:",
            font=("Arial", 10, "bold")
        )
        legend_title.pack(side="left", padx=(0, 10))
        
        for pump_index, track_data in pump_tracks.items():
            pump_color = self.pump_colors[pump_index % len(self.pump_colors)]
            
            # Create pump indicator frame
            pump_frame = ctk.CTkFrame(legend_container, fg_color="transparent")
            pump_frame.pack(side="left", padx=5)
            
            # Create color indicator
            color_frame = ctk.CTkFrame(
                pump_frame,
                width=15,
                height=15,
                fg_color=pump_color,
                corner_radius=3
            )
            color_frame.pack(side="left", padx=(0, 5))
            color_frame.pack_propagate(False)
            
            # Create label
            pump_label = ctk.CTkLabel(
                pump_frame,
                text=f"Pump {pump_index + 1}",
                font=("Arial", 9)
            )
            pump_label.pack(side="left")
    
    def clear_visualization(self):
        """Clear the visualization"""
        self.tasks = []
        self._draw_empty_state()
        self.duration_label.configure(text="Total washing duration: 0.0 ms")
        
        # Clear legend
        for widget in self.legend_frame.winfo_children():
            widget.destroy()
    
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
            self._draw_parallel_sequence()
    
    def destroy(self):
        """Clean up when destroying"""
        AppearanceManager.unregister(self)
        super().destroy()