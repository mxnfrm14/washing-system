import customtkinter as ctk
from components.custom_button import CustomButton
from components.tabview import ThemedTabview
import tkinter as tk
import math
import tkinter.messagebox as messagebox
from components.circuit_designer import CircuitDesigner
from components.detail_list import DetailList

class Circuits(ctk.CTkFrame):
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

        # Configure grid for content frame
        self.tab_view = ThemedTabview(self.content_frame)
        self.tab_view.pack(fill="both", expand=True)
        self.tab1 = self.tab_view.add("Pump 1")
        self.tab2 = self.tab_view.add("Pump 2")
        self.tab3 = self.tab_view.add("Synthesis")

        # Configure grid for tabs
        self.tab1.grid_rowconfigure(0, weight=1)
        self.tab1.grid_columnconfigure(0, weight=0, minsize=350)    # Detail list column
        self.tab1.grid_columnconfigure(1, weight=1)                 # Circuit designer column


        # Create the circuit designer for the first tab
        # self.circuit_designer1 = CircuitDesigner(self.tab1, controller)
        self.detail_list1 = DetailList(self.tab1, controller)
        self.detail_list1.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.circuit_designer1_frame = ctk.CTkFrame(self.tab1, fg_color="transparent")
        self.circuit_designer1_frame.grid(row=0, column=1, sticky="nsew", padx=(0,10), pady=10)

        self.circuit_designer1 = ctk.CTkFrame(self.circuit_designer1_frame, fg_color="#FFFFFF") #CircuitDesigner
        self.circuit_designer1.pack(fill="both", expand=True)
        self.mode_frame1 = ctk.CTkFrame(self.circuit_designer1, fg_color="#243783", height=50) #Mode selction
        self.mode_frame1.pack(fill="x", side='bottom')

        
        # Add basic content to other tabs
        label2 = ctk.CTkLabel(self.tab2, text="Circuit Designer for Pump 2 will be implemented here")
        label2.pack(pady=20)

        label3 = ctk.CTkLabel(self.tab3, text="Synthesis view will show combined circuit designs") 
        label3.pack(pady=20)
    
    def update_appearance(self):
        """Update any appearance-dependent elements"""
        # Update detail list appearance if it exists
        if hasattr(self, 'detail_list1'):
            try:
                self.detail_list1.update_appearance()
            except Exception as e:
                print(f"Error updating detail list appearance: {e}")

    def save_configuration(self):
        """Save the configuration via the controller"""
        # Here you would implement code to save all circuit configurations
        # For now just print confirmation
        print("Circuit configurations saved!")
        messagebox.showinfo("Configuration Saved", "Circuit configurations have been saved successfully.")