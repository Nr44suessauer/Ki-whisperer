"""CategorizedComboBox für kategorisierte Dropdowns"""

import customtkinter as ctk

class CategorizedComboBox(ctk.CTkComboBox):
    """Eine erweiterte ComboBox die kategorisierte Optionen unterstützt"""
    
    def __init__(self, master, categories_dict=None, **kwargs):
        self.categories_dict = categories_dict or {}
        self.flat_values = []
        self.update_values_from_categories()
        super().__init__(master, values=self.flat_values, **kwargs)
        # Auch Focus-Events binden für bessere Erkennung
        self.bind("<Enter>", lambda e: self.focus_set())
    
    def update_values_from_categories(self):
        """Erstellt eine flache List aus den kategorisierten Werten"""
        self.flat_values = []
        for category_name, models in self.categories_dict.items():
            if models:  # Nur Kategorien mit Inhalten show
                self.flat_values.append(f"--- {category_name} ---")
                self.flat_values.extend(models)
    
    def set_categories(self, categories_dict):
        """Aktualisiert die Kategorien"""
        self.categories_dict = categories_dict
        self.update_values_from_categories()
        self.configure(values=self.flat_values)
    
    def get_selected_model(self):
        """Gibt das ausgewählte Model back (ohne Kategorie-Headers)"""
        selected = self.get()
        if selected.startswith("--- ") and selected.endswith(" ---"):
            return None  # Kategorie-Header ausgewählt
        return selected