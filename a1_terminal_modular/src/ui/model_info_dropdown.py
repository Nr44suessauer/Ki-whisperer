"""
Erweitertes Dropdown-Menü mit Modellinformationen
"""
import customtkinter as ctk
import tkinter as tk


class ModelInfoDropdown(ctk.CTkFrame):
    """Dropdown-Menü mit erweiterten Modellinformationen"""
    
    def __init__(self, parent, models_dict=None, on_select=None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.models_dict = models_dict or {}  # Format: {"model_name": {"size": "4GB", "type": "LLM", ...}}
        self.on_select = on_select
        self.selected_model = None
        
        # Haupt-Container
        self.configure(fg_color="transparent")
        
        # Button für Dropdown (zeigt ausgewähltes Modell)
        self.dropdown_btn = ctk.CTkButton(
            self,
            text="Modell auswählen...",
            command=self.toggle_dropdown,
            anchor="w",
            height=38,
            font=("Arial", 12),
            fg_color=("#3b8ed0", "#1f6aa5"),
            hover_color=("#2e7ab8", "#144870")
        )
        self.dropdown_btn.pack(fill="x", padx=0, pady=0)
        
        # Info-Label unter dem Button (zeigt Details zum ausgewählten Modell)
        self.info_label = ctk.CTkLabel(
            self,
            text="",
            font=("Arial", 9),
            text_color=("gray50", "gray70"),
            anchor="w"
        )
        self.info_label.pack(fill="x", padx=5, pady=(2, 0))
        
        # Dropdown-Menü (initial versteckt)
        self.dropdown_frame = None
        self.dropdown_visible = False
        
    def toggle_dropdown(self):
        """Öffnet/Schließt das Dropdown-Menü"""
        if self.dropdown_visible:
            self.hide_dropdown()
        else:
            self.show_dropdown()
    
    def show_dropdown(self):
        """Zeigt das Dropdown-Menü"""
        if self.dropdown_visible or not self.models_dict:
            return
        
        # Erstelle Container für Dropdown
        dropdown_container = ctk.CTkFrame(
            self,
            fg_color=("#d4d4d4", "#2b2b2b"),
            corner_radius=8,
            height=min(300, len(self.models_dict) * 60 + 10)
        )
        dropdown_container.pack(fill="x", padx=2, pady=(5, 0))
        dropdown_container.pack_propagate(False)
        
        # Canvas für scrollbaren Inhalt
        canvas = tk.Canvas(
            dropdown_container,
            bg="#d4d4d4" if ctk.get_appearance_mode() == "Light" else "#2b2b2b",
            highlightthickness=0,
            height=min(300, len(self.models_dict) * 60)
        )
        
        # Scrollbar
        scrollbar = ctk.CTkScrollbar(dropdown_container, command=canvas.yview)
        scrollbar.pack(side="right", fill="y", padx=(0, 2), pady=2)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True, padx=2, pady=2)
        
        # Frame im Canvas
        self.dropdown_frame = ctk.CTkFrame(canvas, fg_color="transparent")
        canvas_window = canvas.create_window((0, 0), window=self.dropdown_frame, anchor="nw")
        
        # Füge Modelle hinzu
        for model_name, model_info in self.models_dict.items():
            self.add_model_item(model_name, model_info)
        
        # Update scroll region
        self.dropdown_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))
        
        # Speichere Container statt Frame für späteres Löschen
        self.dropdown_container = dropdown_container
        self.dropdown_visible = True
    
    def hide_dropdown(self):
        """Versteckt das Dropdown-Menü"""
        if not self.dropdown_visible:
            return
        
        if hasattr(self, 'dropdown_container') and self.dropdown_container:
            self.dropdown_container.destroy()
            self.dropdown_container = None
        
        self.dropdown_frame = None
        self.dropdown_visible = False
    
    def add_model_item(self, model_name, model_info):
        """Fügt ein Modell-Item zum Dropdown hinzu"""
        # Container für Modell-Item
        item_frame = ctk.CTkFrame(
            self.dropdown_frame,
            fg_color=("#e8e8e8", "#353535"),
            corner_radius=6,
            height=55
        )
        item_frame.pack(fill="x", padx=5, pady=3)
        item_frame.pack_propagate(False)
        
        # Mache den Frame klickbar
        item_frame.bind("<Button-1>", lambda e: self.select_model(model_name, model_info))
        
        # Hover-Effekt
        def on_enter(e):
            item_frame.configure(fg_color=("#3b8ed0", "#1f6aa5"))
        
        def on_leave(e):
            item_frame.configure(fg_color=("#e8e8e8", "#353535"))
        
        item_frame.bind("<Enter>", on_enter)
        item_frame.bind("<Leave>", on_leave)
        
        # Modell-Name (fett)
        name_label = ctk.CTkLabel(
            item_frame,
            text=model_name,
            font=("Arial", 12, "bold"),
            anchor="w"
        )
        name_label.pack(anchor="w", padx=10, pady=(5, 0))
        name_label.bind("<Button-1>", lambda e: self.select_model(model_name, model_info))
        name_label.bind("<Enter>", on_enter)
        name_label.bind("<Leave>", on_leave)
        
        # Modell-Info (klein, grau)
        size = model_info.get("size", "?")
        param_count = model_info.get("parameters", "")
        model_type = model_info.get("type", "")
        
        info_parts = []
        if size:
            info_parts.append(f"📦 {size}")
        if param_count:
            info_parts.append(f"🔢 {param_count}")
        if model_type:
            info_parts.append(f"🏷️ {model_type}")
        
        info_text = " • ".join(info_parts) if info_parts else "Modell verfügbar"
        
        info_label = ctk.CTkLabel(
            item_frame,
            text=info_text,
            font=("Arial", 9),
            text_color=("gray50", "gray70"),
            anchor="w"
        )
        info_label.pack(anchor="w", padx=10, pady=(0, 5))
        info_label.bind("<Button-1>", lambda e: self.select_model(model_name, model_info))
        info_label.bind("<Enter>", on_enter)
        info_label.bind("<Leave>", on_leave)
    
    def select_model(self, model_name, model_info):
        """Wählt ein Modell aus"""
        self.selected_model = model_name
        
        # Update Button-Text
        display_name = model_name[:35] + "..." if len(model_name) > 35 else model_name
        self.dropdown_btn.configure(text=display_name)
        
        # Update Info-Label
        size = model_info.get("size", "")
        param_count = model_info.get("parameters", "")
        model_type = model_info.get("type", "")
        
        info_parts = []
        if size:
            info_parts.append(f"Größe: {size}")
        if param_count:
            info_parts.append(f"Parameter: {param_count}")
        if model_type:
            info_parts.append(f"Typ: {model_type}")
        
        self.info_label.configure(text=" • ".join(info_parts) if info_parts else "")
        
        # Schließe Dropdown
        self.hide_dropdown()
        
        # Callback aufrufen
        if self.on_select:
            self.on_select(model_name)
    
    def update_models(self, models_dict):
        """Aktualisiert die verfügbaren Modelle"""
        self.models_dict = models_dict
        
        # Schließe Dropdown wenn offen
        if self.dropdown_visible:
            self.hide_dropdown()
        
        # Reset Auswahl wenn Modell nicht mehr verfügbar
        if self.selected_model and self.selected_model not in models_dict:
            self.selected_model = None
            self.dropdown_btn.configure(text="Modell auswählen...")
            self.info_label.configure(text="")
    
    def get_selected(self):
        """Gibt das ausgewählte Modell zurück"""
        return self.selected_model
    
    def set_selected(self, model_name):
        """Setzt das ausgewählte Modell"""
        if model_name in self.models_dict:
            self.select_model(model_name, self.models_dict[model_name])
        else:
            # Modell ist nicht in der Liste, aber zeige es trotzdem an
            self.selected_model = model_name
            display_name = model_name[:35] + "..." if len(model_name) > 35 else model_name
            self.dropdown_btn.configure(text=display_name)
            self.info_label.configure(text="Modell aus Session geladen")
