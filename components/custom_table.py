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
        
        # Calculate total table width
        self.total_width = sum(self.column_widths) + 80  # Add space for action column
        
        # Create the table structure
        self._create_table()
        
        # Update appearance - now called AFTER creating the table
        AppearanceManager.register(self)
        self.update_appearance()
    
    def _calculate_column_widths(self) -> List[int]:
        """Calculate optimal column widths based on headers and content"""
        if not self.headers:
            return []
        
        # Calculate widths based on both headers and content
        column_widths = []
        
        for i, header in enumerate(self.headers):
            # Start with header width
            header_width = len(header) * 8 + 40  # Increased padding
            max_width = header_width
            
            # Check content width if data exists
            if self.data:
                for row in self.data:
                    content = str(row.get(header, ""))
                    content_width = len(content) * 7 + 40  # Content typically needs less width per char
                    max_width = max(max_width, content_width)
            
            # Set minimum and maximum constraints
            min_width = 100
            max_allowed_width = 250
            
            column_widths.append(min(max(max_width, min_width), max_allowed_width))
        
        return column_widths
    
    def _create_table(self):
        """Create the initial table structure"""
        colors = self._get_colors()
        
        # Main table container
        self.table_container = ctk.CTkFrame(
            self, 
            fg_color="transparent",
            corner_radius=self.corner_radius
        )
        self.table_container.pack(fill="both", expand=True)
        
        # Configure table container grid
        self.table_container.grid_rowconfigure(0, weight=0)  # Header
        self.table_container.grid_rowconfigure(1, weight=1)  # Content
        self.table_container.grid_columnconfigure(0, weight=1)
        
        # Create header frame with fixed width
        self.header_frame = ctk.CTkFrame(
            self.table_container, 
            fg_color=colors["header_bg"],
            corner_radius=self.corner_radius,
            height=self.row_height,
            width=self.total_width
        )
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 1))
        
        # Configure header frame grid
        for i, width in enumerate(self.column_widths):
            self.header_frame.grid_columnconfigure(i, weight=0, minsize=width)
        # Action column - fixed width at the end
        self.header_frame.grid_columnconfigure(len(self.column_widths), weight=0, minsize=80)
        
        # Add header cells
        for i, header in enumerate(self.headers):
            cell = ctk.CTkLabel(
                self.header_frame,
                text=header,
                fg_color="transparent",
                text_color=colors["header_fg"],
                font=ctk.CTkFont(family="Encode Sans Expanded Bold", size=12, weight="bold"),
                anchor="center",
                width=self.column_widths[i]
            )
            cell.grid(row=0, column=i, sticky="ew", padx=2, pady=1)
            self.header_cells.append(cell)
        
        # Add "Actions" header
        actions_header = ctk.CTkLabel(
            self.header_frame,
            text="Actions",
            fg_color="transparent",
            text_color=colors["header_fg"],
            font=ctk.CTkFont(family="Encode Sans Expanded Bold", size=12, weight="bold"),
            anchor="center",
            width=80
        )
        actions_header.grid(row=0, column=len(self.headers), sticky="ew", padx=2, pady=1)
        self.header_cells.append(actions_header)
        
        # Create scrollable content frame
        self.rows_container = ctk.CTkScrollableFrame(
            self.table_container, 
            fg_color="transparent",
            corner_radius=0
        )
        self.rows_container.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        
        # Configure scrollbar
        self.rows_container._scrollbar.grid_configure(padx=(2, 0))
        
        # Add initial data rows
        for row_data in self.data:
            self.add_row(row_data)
    
    def add_row(self, row_data: Dict[str, Any], index: int = None) -> int:
        """Add a new row to the table"""
        colors = self._get_colors()
        
        # Determine row index
        if index is None or index >= len(self.rows):
            index = len(self.rows)
        
        # Get background color based on even/odd row
        bg_color = colors["row_bg_even"] if index % 2 == 0 else colors["row_bg_odd"]
        
        # Create row frame
        row_frame = ctk.CTkFrame(
            self.rows_container,
            fg_color=bg_color,
            corner_radius=0,
            height=self.row_height
        )
        row_frame.pack(fill="x", padx=0, pady=0)
        
        # Configure row frame grid to match header
        for i, width in enumerate(self.column_widths):
            row_frame.grid_columnconfigure(i, weight=0, minsize=width)
        # Action column
        row_frame.grid_columnconfigure(len(self.column_widths), weight=0, minsize=80)
        
        # Create cells for each column
        row_cells = []
        for i, header in enumerate(self.headers):
            # Get cell value
            cell_value = str(row_data.get(header, ""))
            
            # Create cell label
            cell = ctk.CTkLabel(
                row_frame,
                text=cell_value,
                fg_color="transparent",
                text_color=colors["row_fg"],
                font=ctk.CTkFont(family="Encode Sans Expanded", size=12),
                anchor="center",
                width=self.column_widths[i]
            )
            cell.grid(row=0, column=i, sticky="ew", padx=2, pady=1)
            row_cells.append(cell)
        
        # Create actions frame in the last column
        actions_frame = ctk.CTkFrame(
            row_frame, 
            fg_color="transparent",
            width=80
        )
        actions_frame.grid(row=0, column=len(self.headers), sticky="ew", padx=2, pady=1)
        
        # Center the buttons in the actions frame
        actions_frame.grid_columnconfigure(0, weight=1)
        actions_frame.grid_columnconfigure(1, weight=0)
        actions_frame.grid_columnconfigure(2, weight=0)
        actions_frame.grid_columnconfigure(3, weight=1)
        
        # Load icons
        actual_mode = ctk.get_appearance_mode().lower()
        edit_icon = self.icons.get("edit", {}).get(actual_mode)
        delete_icon = self.icons.get("delete", {}).get(actual_mode)
        
        # Create buttons centered in the actions frame
        edit_btn = ctk.CTkButton(
            actions_frame,
            text="",
            image=edit_icon,
            width=25,
            height=25,
            fg_color=colors["button_bg"],
            hover_color=colors["button_hover"],
            border_width=0,
            corner_radius=6,
            command=lambda idx=index: self._handle_edit(idx)
        )
        edit_btn.grid(row=0, column=1, padx=2)
        
        delete_btn = ctk.CTkButton(
            actions_frame,
            text="",
            image=delete_icon,
            width=25,
            height=25,
            fg_color=colors["button_bg"],
            hover_color=colors["button_hover"],
            border_width=0,
            corner_radius=6,
            command=lambda idx=index: self._handle_delete(idx)
        )
        delete_btn.grid(row=0, column=2, padx=2)
        
        # Store row data
        row_entry = {
            "data": row_data,
            "cells": row_cells,
            "frame": row_frame,
            "actions": (edit_btn, delete_btn),
            "actions_frame": actions_frame
        }
        
        # Insert row data
        if index < len(self.rows):
            self.rows.insert(index, row_entry)
            self.row_frames.insert(index, row_frame)
            self.action_buttons.insert(index, (edit_btn, delete_btn))
            self._update_row_appearance()
        else:
            self.rows.append(row_entry)
            self.row_frames.append(row_frame)
            self.action_buttons.append((edit_btn, delete_btn))
        
        return index
    
    def remove_row(self, index: int) -> bool:
        """Remove a row from the table"""
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
            
            # Update button callbacks with new indices
            self._update_button_callbacks()
            
            return True
        return False
    
    def _update_button_callbacks(self):
        """Update button callbacks after row removal to maintain correct indices"""
        for i, (edit_btn, delete_btn) in enumerate(self.action_buttons):
            edit_btn.configure(command=lambda idx=i: self._handle_edit(idx))
            delete_btn.configure(command=lambda idx=i: self._handle_delete(idx))
    
    def update_row(self, index: int, row_data: Dict[str, Any]) -> bool:
        """Update an existing row with new data"""
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
                "header_bg": "#F8F8F8",
                "header_fg": "#243783",
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
        """Update appearance of all rows (for even/odd coloring)"""
        colors = self._get_colors()
        
        for i, frame in enumerate(self.row_frames):
            # Update background color based on even/odd row
            bg_color = colors["row_bg_even"] if i % 2 == 0 else colors["row_bg_odd"]
            frame.configure(fg_color=bg_color)
    
    def update_appearance(self, appearance_mode: str = None):
        """Update the appearance of the table based on the appearance mode"""
        if appearance_mode is not None:
            self.appearance_mode = appearance_mode
            
        actual_mode = ctk.get_appearance_mode().lower()
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
            from utils.open_image import open_icon
            
            # Edit icon
            edit_path = "assets/icons/edit.png"
            if os.path.exists(edit_path):
                self.icons["edit"] = {
                    "light": open_icon(edit_path, size=(20, 20)),
                    "dark": open_icon(edit_path, size=(20, 20))
                }
            else:
                print(f"Warning: Edit icon not found at {edit_path}")
            
            # Delete icon
            delete_path = "assets/icons/trash.png"
            if os.path.exists(delete_path):
                self.icons["delete"] = {
                    "light": open_icon(delete_path, size=(20, 20), tint_color="#FF0000"),
                    "dark": open_icon(delete_path, size=(20, 20), tint_color="#FF0000")
                }
            else:
                print(f"Warning: Delete icon not found at {delete_path}")
        except Exception as e:
            print(f"Error loading table icons: {e}")