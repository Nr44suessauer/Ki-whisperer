"""Modern Model Selector Widget"""

import customtkinter as ctk

class ModelSelector(ctk.CTkFrame):
    """Modernes Widget für Model-Auswahl und Management"""
    
    def __init__(self, master, on_model_select=None, on_model_download=None, 
                 on_model_delete=None, on_refresh=None, **kwargs):
        super().__init__(master, **kwargs)
        
        self.on_model_select = on_model_select
        self.on_model_download = on_model_download
        self.on_model_delete = on_model_delete
        self.on_refresh = on_refresh
        
        self.configure(fg_color="#2b2b2b", corner_radius=10, border_width=1, border_color="#4a4a4a")
        
        self._build_ui()
    
    def _build_ui(self):
        """Erstellt die UI"""
        
        # Header
        header = ctk.CTkLabel(
            self,
            text="🤖 AI Model",
            font=("Arial", 14, "bold"),
            anchor="w"
        )
        header.pack(fill="x", padx=15, pady=(15, 10))
        
        # Current Model Section
        current_frame = ctk.CTkFrame(self, fg_color="#1a1a1a", corner_radius=8)
        current_frame.pack(fill="x", padx=10, pady=5)
        
        current_label = ctk.CTkLabel(
            current_frame,
            text="Aktuelles Model:",
            font=("Arial", 10, "bold"),
            anchor="w"
        )
        current_label.pack(anchor="w", padx=10, pady=(8, 2))
        
        # Model Dropdown + Quick Actions
        model_control = ctk.CTkFrame(current_frame, fg_color="transparent")
        model_control.pack(fill="x", padx=10, pady=(0, 8))
        
        self.model_dropdown = ctk.CTkComboBox(
            model_control,
            values=["Kein Model available"],
            command=self._on_model_change,
            font=("Arial", 10),
            dropdown_font=("Arial", 9),
            corner_radius=6
        )
        self.model_dropdown.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        # Quick Action Buttons
        btn_frame = ctk.CTkFrame(model_control, fg_color="transparent")
        btn_frame.pack(side="right")
        
        # Refresh Button
        refresh_btn = ctk.CTkButton(
            btn_frame,
            text="🔄",
            width=35,
            height=28,
            command=self._on_refresh,
            fg_color="#3a3a3a",
            hover_color="#4a4a4a",
            corner_radius=6
        )
        refresh_btn.pack(side="left", padx=2)
        
        # Delete Button
        delete_btn = ctk.CTkButton(
            btn_frame,
            text="🗑️",
            width=35,
            height=28,
            command=self._on_delete,
            fg_color="#722F37",
            hover_color="#8B3A47",
            corner_radius=6
        )
        delete_btn.pack(side="left", padx=2)
        
        # Divider
        divider = ctk.CTkFrame(self, height=2, fg_color="#3a3a3a")
        divider.pack(fill="x", padx=15, pady=10)
        
        # Download Section
        download_label = ctk.CTkLabel(
            self,
            text="⬇️ Add new model",
            font=("Arial", 11, "bold"),
            anchor="w"
        )
        download_label.pack(anchor="w", padx=15, pady=(5, 5))
        
        download_frame = ctk.CTkFrame(self, fg_color="#1a1a1a", corner_radius=8)
        download_frame.pack(fill="x", padx=10, pady=5)
        
        # Model Name Input
        input_frame = ctk.CTkFrame(download_frame, fg_color="transparent")
        input_frame.pack(fill="x", padx=10, pady=10)
        
        self.download_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="z.B. llama3.2:3b",
            font=("Arial", 10),
            corner_radius=6
        )
        self.download_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        download_btn = ctk.CTkButton(
            input_frame,
            text="⬇️ Download",
            width=100,
            command=self._on_download,
            fg_color="#2B8A3E",
            hover_color="#37A24B",
            corner_radius=6,
            font=("Arial", 10, "bold")
        )
        download_btn.pack(side="right")
        
        # Popular Models Quick-Select
        popular_label = ctk.CTkLabel(
            download_frame,
            text="Beliebte Modelle:",
            font=("Arial", 9),
            anchor="w",
            text_color="#888888"
        )
        popular_label.pack(anchor="w", padx=10, pady=(0, 5))
        
        popular_frame = ctk.CTkFrame(download_frame, fg_color="transparent")
        popular_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        popular_models = [
            ("llama3.2:3b", "🦙 Llama 3.2"),
            ("mistral:7b", "🌬️ Mistral"),
            ("codellama:7b", "💻 CodeLlama"),
            ("phi3:mini", "⚡ Phi-3")
        ]
        
        for i, (model, display) in enumerate(popular_models):
            btn = ctk.CTkButton(
                popular_frame,
                text=display,
                width=120,
                height=25,
                command=lambda m=model: self._quick_download(m),
                fg_color="#3a3a3a",
                hover_color="#4a4a4a",
                corner_radius=6,
                font=("Arial", 8)
            )
            btn.grid(row=i // 2, column=i % 2, padx=3, pady=3, sticky="ew")
        
        popular_frame.grid_columnconfigure(0, weight=1)
        popular_frame.grid_columnconfigure(1, weight=1)
        
        # Status Label
        self.status_label = ctk.CTkLabel(
            self,
            text="",
            font=("Arial", 9),
            text_color="#888888"
        )
        self.status_label.pack(padx=15, pady=(5, 10))
    
    def _on_model_change(self, choice):
        """Model wurde changed"""
        if self.on_model_select:
            self.on_model_select(choice)
    
    def _on_refresh(self):
        """Refresh wurde geklickt"""
        if self.on_refresh:
            self.on_refresh()
    
    def _on_delete(self):
        """Delete wurde geklickt"""
        current = self.model_dropdown.get()
        if current and current != "Kein Model available" and self.on_model_delete:
            self.on_model_delete(current)
    
    def _on_download(self):
        """Download-Button wurde geklickt"""
        model_name = self.download_entry.get().strip()
        if model_name and self.on_model_download:
            self.on_model_download(model_name)
            self.download_entry.delete(0, 'end')
    
    def _quick_download(self, model_name):
        """Quick-Download für populäre Modelle"""
        if self.on_model_download:
            self.on_model_download(model_name)
    
    def set_models(self, models):
        """Setzt die verfügbaren Modelle"""
        if models:
            self.model_dropdown.configure(values=models)
            self.model_dropdown.set(models[0])
        else:
            self.model_dropdown.configure(values=["Kein Model available"])
            self.model_dropdown.set("Kein Model available")
    
    def set_current_model(self, model):
        """Setzt das aktuelle Model"""
        if model:
            self.model_dropdown.set(model)
    
    def set_status(self, text, color="#888888"):
        """Setzt den Status-Text"""
        self.status_label.configure(text=text, text_color=color)
