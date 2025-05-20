import customtkinter as ctk
from PIL import Image
import os
from typing import List, Dict, Any, Callable, Optional, Tuple, Union
from utils.appearance_manager import AppearanceManager

class CustomTable(ctk.CTkFrame):
    """
    Custom table implementation with edit and delete actions
    """
    def __init__(
        self, 
        master, 
        headers: List[str], 
        data: List[Dict[str, Any]] = None,
        width: int = 800,
        row_height: int = 40,
        corner_radius: int = 6,
        edit_command: Callable = None,
        delete_command: Callable = None,
        column_widths: List[int] = None,  # Allow custom column widths
        appearance_mode: str = "Dark",
        **kwargs
    ):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        # Store parameters
        self.headers = headers
        self.data = data or []
        self.width = width
        self.row_height = row_height
        self.corner_radius = corner_radius
        self.edit_command = edit_command
        self.delete_command = delete_command
        
        # Initialize appearance mode at the beginning
        self.appearance_mode = appearance_mode
        print(appearance_mode)
        # Removed the premature call to update_appearance()

        
        # Store references to rows, cells and icons
        self.header_cells = []
        self.rows = []
        self.row_frames = []
        self.action_buttons = []
        self.icons = {}
        
        # Create and load icons
        self._load_icons()
        
        # Calculate column widths or use provided ones
        self.column_widths = column_widths if column_widths else self._calculate_column_widths()
        
        # Create the table structure
        self._create_table()
        
        # Update appearance - now called AFTER creating the table
        AppearanceManager.register(self)
        self.update_appearance()
        
        # Set the actual width of the frame to match internal content
        self.configure(width=self._get_total_width())
    
    def _get_total_width(self) -> int:
        """Calculate the total width of the table based on column widths"""
        return sum(self.column_widths)
    
    def _calculate_column_widths(self) -> List[int]:
        """Calculate optimal column widths based on headers and available width"""
        # Reserve space for action column (fixed width)
        action_width = 50
        available_width = self.width - action_width
        
        if not self.headers:
            return [available_width, action_width]
        
        # Get a test font to measure text width
        font = ctk.CTkFont(weight="bold")
        
        # Estimate minimum width needed for each header (assuming characters are ~10px wide)
        # This is an approximation since CTk doesn't have direct text measurement
        header_widths = [len(header) * 10 for header in self.headers]
        
        # Ensure minimum width for each column (at least 80px)
        min_width = 80
        header_widths = [max(w, min_width) for w in header_widths]
        
        # Calculate total width needed
        total_needed = sum(header_widths)
        
        # If we need more than available, adjust proportionally
        if total_needed > available_width:
            scale_factor = available_width / total_needed
            header_widths = [int(w * scale_factor) for w in header_widths]
        # If we need less, distribute remaining space proportionally
        elif total_needed < available_width:
            remaining = available_width - total_needed
            # Distribute remaining space proportionally to column width
            for i in range(len(header_widths)):
                proportion = header_widths[i] / total_needed if total_needed > 0 else 1/len(header_widths)
                header_widths[i] += int(remaining * proportion)
        
        # Add action column width
        return header_widths + [action_width]
    
    def _create_table(self):
        """Create the initial table structure"""
        colors = self._get_colors()
        
        # Main table container - controls the total width
        self.table_container = ctk.CTkFrame(
            self, 
            fg_color="transparent",
            width=self._get_total_width(),
            height=40  # Will expand with content
        )
        self.table_container.pack(fill="both", expand=True)
        
        # Create header frame
        self.header_frame = ctk.CTkFrame(
            self.table_container, 
            fg_color=colors["header_bg"],
            corner_radius=self.corner_radius,
            height=self.row_height,
            width=self._get_total_width()
        )
        self.header_frame.pack(fill="x", padx=0, pady=(0, 1))
        
        # Make header frame have fixed width columns
        self.header_frame.pack_propagate(False)
        
        # Set up columns in header frame
        for i, width in enumerate(self.column_widths):
            self.header_frame.columnconfigure(i, weight=0, minsize=width)
        
        # Add header cells
        for i, header in enumerate(self.headers):
            cell = ctk.CTkLabel(
                self.header_frame,
                text=header,
                fg_color="transparent",
                text_color=colors["header_fg"],
                font=ctk.CTkFont(weight="bold"),
                anchor="w",
                padx=10,
                width=self.column_widths[i]
            )
            cell.grid(row=0, column=i, sticky="nsew", padx=1, pady=1)
            self.header_cells.append(cell)
        
        # Add "Actions" header for the last column
        actions_header = ctk.CTkLabel(
            self.header_frame,
            text="Actions",
            fg_color="transparent",
            text_color=colors["header_fg"],
            font=ctk.CTkFont(weight="bold"),
            anchor="center",
            width=self.column_widths[-1]
        )
        actions_header.grid(row=0, column=len(self.headers), sticky="nsew", padx=1, pady=1)
        self.header_cells.append(actions_header)
        
        # Create rows container with the same width
        self.rows_container = ctk.CTkFrame(
            self.table_container, 
            fg_color="transparent",
            width=self._get_total_width()
        )
        self.rows_container.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Add initial data rows if any
        for row_data in self.data:
            self.add_row(row_data)
    
    def add_row(self, row_data: Dict[str, Any], index: int = None) -> int:
        """
        Add a new row to the table
        
        Parameters:
            row_data: Dictionary with data for the row (keys should match headers)
            index: Position to insert the row (None for append)
            
        Returns:
            The index of the added row
        """
        colors = self._get_colors()
        
        # Determine row index
        if index is None or index >= len(self.rows):
            index = len(self.rows)
        
        # Get background color based on even/odd row
        bg_color = colors["row_bg_even"] if index % 2 == 0 else colors["row_bg_odd"]
        
        # Create row frame with rounded corners if it's the last row
        is_last_row = (index == len(self.rows))
        corner_radius = self.corner_radius if is_last_row else 0
        
        row_frame = ctk.CTkFrame(
            self.rows_container,
            fg_color=bg_color,
            corner_radius=corner_radius,
            height=self.row_height,
            width=self._get_total_width()
        )
        
        # Fixed width row
        row_frame.pack(fill="x", padx=0, pady=0)
        row_frame.pack_propagate(False)
        
        # Configure columns in row to match header
        for i, width in enumerate(self.column_widths):
            row_frame.columnconfigure(i, weight=0, minsize=width)
        
        # Create cells for each column
        row_cells = []
        for i, header in enumerate(self.headers):
            # Get cell value or empty string if not found
            cell_value = str(row_data.get(header, ""))
            
            # Create cell label
            cell = ctk.CTkLabel(
                row_frame,
                text=cell_value,
                fg_color="transparent",
                text_color=colors["row_fg"],
                anchor="w",
                padx=10,
                width=self.column_widths[i]
            )
            cell.grid(row=0, column=i, sticky="nsew", padx=1, pady=1)
            row_cells.append(cell)
        
        # Create actions container
        actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        actions_frame.grid(row=0, column=len(self.headers), sticky="nsew", padx=1, pady=1)
        
        # Add edit and delete buttons
        # Use current appearance mode directly
        actual_mode = ctk.get_appearance_mode().lower()
        edit_icon = self.icons.get("edit", {}).get(actual_mode)
        delete_icon = self.icons.get("delete", {}).get(actual_mode)
        
        edit_btn = ctk.CTkButton(
            actions_frame,
            text="",
            image=edit_icon,
            width=30,
            height=30,
            fg_color=colors["button_bg"],
            hover_color=colors["button_hover"],
            border_width=0,
            corner_radius=6,
            command=lambda idx=index: self._handle_edit(idx)
        )
        edit_btn.pack(side="left", padx=1)
        
        delete_btn = ctk.CTkButton(
            actions_frame,
            text="",
            image=delete_icon,
            width=30,
            height=30,
            fg_color=colors["button_bg"],
            hover_color=colors["button_hover"],
            border_width=0,
            corner_radius=6,
            command=lambda idx=index: self._handle_delete(idx)
        )
        delete_btn.pack(side="left", padx=1)
        
        # Create row data entry
        row_entry = {
            "data": row_data,
            "cells": row_cells,
            "frame": row_frame,
            "actions": (edit_btn, delete_btn)
        }
        
        # Insert row data at specified index
        if index < len(self.rows):
            self.rows.insert(index, row_entry)
            self.row_frames.insert(index, row_frame)
            self.action_buttons.insert(index, (edit_btn, delete_btn))
            
            # Update appearance of existing rows (for even/odd coloring)
            self._update_row_appearance()
        else:
            self.rows.append(row_entry)
            self.row_frames.append(row_frame)
            self.action_buttons.append((edit_btn, delete_btn))
        
        return index
    
    def remove_row(self, index: int) -> bool:
        """
        Remove a row from the table
        
        Parameters:
            index: Index of the row to remove
            
        Returns:
            True if row was removed, False otherwise
        """
        if 0 <= index < len(self.rows):
            # Destroy the row frame
            if index < len(self.row_frames):
                self.row_frames[index].destroy()
                del self.row_frames[index]
            
            # Remove from action buttons
            if index < len(self.action_buttons):
                del self.action_buttons[index]
            
            # Remove from rows data
            del self.rows[index]
            
            # Update row appearance for proper even/odd coloring
            self._update_row_appearance()
            return True
        return False
    
    def update_row(self, index: int, row_data: Dict[str, Any]) -> bool:
        """
        Update an existing row with new data
        
        Parameters:
            index: Index of the row to update
            row_data: New data for the row
            
        Returns:
            True if row was updated, False otherwise
        """
        if 0 <= index < len(self.rows):
            row = self.rows[index]
            
            # Update data reference
            row["data"].update(row_data)
            
            # Update cell texts
            for i, header in enumerate(self.headers):
                if i < len(row["cells"]):
                    cell_value = str(row_data.get(header, ""))
                    row["cells"][i].configure(text=cell_value)
            
            return True
        return False
    
    def get_row_data(self, index: int) -> Dict[str, Any]:
        """Get data for a specific row"""
        if 0 <= index < len(self.rows):
            return self.rows[index]["data"].copy()
        return {}
    
    def get_all_data(self) -> List[Dict[str, Any]]:
        """Get all row data as a list of dictionaries"""
        return [row["data"].copy() for row in self.rows]
    
    def clear(self):
        """Remove all rows from the table"""
        # Destroy all row frames
        for frame in self.row_frames:
            frame.destroy()
        
        # Clear all data
        self.rows = []
        self.row_frames = []
        self.action_buttons = []
    
    def _handle_edit(self, index: int):
        """Handle edit button click"""
        if self.edit_command and 0 <= index < len(self.rows):
            row_data = self.get_row_data(index)
            self.edit_command(index, row_data)
    
    def _handle_delete(self, index: int):
        """Handle delete button click"""
        if self.delete_command and 0 <= index < len(self.rows):
            row_data = self.get_row_data(index)
            self.delete_command(index, row_data)
    
    def _get_colors(self):
        """Get theme colors based on appearance mode"""
        mode = ctk.get_appearance_mode()
        
        if mode == "Dark":
            return {
                "header_bg": "#243783",
                "header_fg": "#F8F8F8",
                "row_bg_even": "#1A296C",
                "row_bg_odd": "#243783",
                "row_fg": "#F8F8F8",
                "border": "#F8F8F8",
                "button_bg": "transparent",
                "button_hover": "#12205C",
                "divider": "#F8F8F8"
            }
        else:
            return {
                "header_bg": "#243783",
                "header_fg": "#F8F8F8",
                "row_bg_even": "#F8F8F8",
                "row_bg_odd": "#F3F3F3",
                "row_fg": "#0D0D0D",
                "border": "#243783",
                "button_bg": "transparent",
                "button_hover": "#E8E8E8",
                "divider": "#243783"
            }
    
    def _update_row_appearance(self):
        """Update appearance of all rows (for even/odd coloring and corner radius)"""
        colors = self._get_colors()
        
        for i, frame in enumerate(self.row_frames):
            # Update background color based on even/odd row
            bg_color = colors["row_bg_even"] if i % 2 == 0 else colors["row_bg_odd"]
            frame.configure(fg_color=bg_color)
            
            # Update corner radius for last row only
            is_last_row = (i == len(self.row_frames) - 1)
            corner_radius = self.corner_radius if is_last_row else 0
            
            # Update corner radius safely
            try:
                frame.configure(corner_radius=corner_radius)
            except Exception:
                # Fallback for older CTk versions
                frame._corner_radius = corner_radius
                if hasattr(frame, '_draw_engine'):
                    frame._draw_engine.configure(corner_radius=corner_radius)
    
    def update_appearance(self, appearance_mode: str = None):
        """Update the appearance of the table based on the appearance mode"""
        # If appearance_mode is provided, update the stored mode
        if appearance_mode is not None:
            self.appearance_mode = appearance_mode
            
        # Get the actual current mode from the system
        actual_mode = ctk.get_appearance_mode().lower()
        
        # Get colors based on the actual mode
        colors = self._get_colors()
        
        # Update header
        self.header_frame.configure(fg_color=colors["header_bg"])
        for cell in self.header_cells:
            cell.configure(text_color=colors["header_fg"])
        
        # Update row appearance
        self._update_row_appearance()
        
        # Update all row text colors
        for row in self.rows:
            for cell in row["cells"]:
                cell.configure(text_color=colors["row_fg"])
        
        # Update action buttons
        for edit_btn, delete_btn in self.action_buttons:
            edit_icon = self.icons.get("edit", {}).get(actual_mode)
            delete_icon = self.icons.get("delete", {}).get(actual_mode)
                
            edit_btn.configure(
                fg_color=colors["button_bg"],
                hover_color=colors["button_hover"],
                image=edit_icon
            )
            delete_btn.configure(
                fg_color=colors["button_bg"],
                hover_color=colors["button_hover"],
                image=delete_icon
            )

    def _load_icons(self):
        """Load edit and delete icons"""
        try:
            # Import the open_icon function
            from utils.open_image import open_icon
            
            # Edit icon
            edit_path = "assets/icons/edit.png"
            if not os.path.exists(edit_path):
                print(f"Warning: Edit icon not found at {edit_path}")
            else:
                self.icons["edit"] = {
                    "light": open_icon(edit_path, size=(20, 20)),
                    "dark": open_icon(edit_path, size=(20, 20))
                }
            
            # Delete icon
            delete_path = "assets/icons/trash.png"
            if not os.path.exists(delete_path):
                print(f"Warning: Delete icon not found at {delete_path}")
            else:
                self.icons["delete"] = {
                    "light": open_icon(delete_path, size=(20, 20), tint_color="#FF0000"),
                    "dark": open_icon(delete_path, size=(20, 20), tint_color="#FF0000")
                }
        except Exception as e:
            print(f"Error loading table icons: {e}")