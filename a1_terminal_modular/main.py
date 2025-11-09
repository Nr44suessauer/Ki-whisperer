#!/usr/bin/env python3
"""
A1 Terminal - Modulare Version
Haupteinstiegspunkt
"""

import customtkinter as ctk

# Erscheinungsbild konfigurieren
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

from src.core.a1_terminal import A1Terminal

if __name__ == "__main__":
    app = A1Terminal()
    app.run()
